"""Processes CDX records and gathers pages from the Wayback Machine."""

import argparse
import logging

import celery
from sqlalchemy.orm import Session
from tqdm import tqdm

from celeryworker import process_cdx_record
from gatherspecimens.schema import (Base, CdxRecordSpecimen, MementoFailure,
                                    MementoSpecimen)
from gatherspecimens.utils import common_logging, get_engine

log = logging.getLogger(__name__)


def main():
    """Process records to gather pages."""
    parser = argparse.ArgumentParser(description="Process records to gather pages.")
    parser.add_argument(
        "--start", type=int, default=0, help="Starting offset for processing"
    )
    # Chunk size is the number of records to process at a time. Setting this too
    # large will eat up your memory.
    parser.add_argument(
        "--chunk-size", type=int, default=1000, help="Size of chunks to process"
    )
    args = parser.parse_args()

    engine = get_engine("config.json")
    Base.metadata.create_all(engine)

    with Session(engine) as db_session:
        # Get the total number of records
        cdx_query = db_session.query(CdxRecordSpecimen)
        total_records = cdx_query.count()
        log.info("Total records: %d", total_records)

        # Use tqdm to show a progress bar
        with tqdm(total=total_records) as pbar:
            pbar.update(args.start)

            # Initialize the job groups
            groups = []

            # In steps of chunk_size, process the records.
            for offset in range(args.start, total_records, args.chunk_size):
                results = (
                    cdx_query.order_by(CdxRecordSpecimen.id)
                    .limit(args.chunk_size)
                    .offset(offset)
                    .all()
                )

                # Get the IDs from the results
                ids = [record.id for record in results]

                # Check if any of the records have already been scraped
                already_scraped = set(
                    [
                        s.id
                        for s in db_session.query(MementoSpecimen).filter(
                            MementoSpecimen.id.in_(ids)
                        )
                    ]
                )
                already_failed = set(
                    [
                        s.id
                        for s in db_session.query(MementoFailure).filter(
                            MementoFailure.id.in_(ids)
                        )
                    ]
                )
                log.info(
                    "[%d] Already scraped: %d; already failed: %d",
                    offset,
                    len(already_scraped),
                    len(already_failed),
                )

                # Create a list to hold the celery jobs
                jobs = []

                for record in results:
                    # If the record had a 4xx or higher status code
                    # then there's no point in archiving it.
                    if record.status_code and record.status_code >= 400:
                        log.warning(
                            "[%d] Record %s had error: status code %d",
                            record.id,
                            record.url,
                            record.status_code,
                        )
                        continue

                    # If the record was already scraped or already failed,
                    # then don't try to get it again.
                    if record.id in already_scraped:
                        log.info(
                            "[%d] Record %s already scraped", record.id, record.raw_url
                        )
                        continue
                    elif record.id in already_failed:
                        log.info(
                            "[%d] Record %s previously failed",
                            record.id,
                            record.raw_url,
                        )
                        continue

                    # Need to serialize the record to pass it to the Celery task
                    ser = record.to_serializable()

                    jobs.append(process_cdx_record.s(ser))

                # Create a celery group so the jobs can
                # be gotten in a batch when ready.
                log.debug("Submitting %d jobs", len(jobs))
                job_group = celery.group(jobs)
                res = job_group.apply_async()
                groups.append(res)

                try:
                    # If the first group is ready, or the groups list is too long,
                    # then wait for the first group to finish.
                    # Otherwise, continue processing the next chunk so that the
                    # workers don't go idle.
                    if groups[0].ready() or len(groups) > 5:
                        wait_group = groups.pop(0)
                        for record_id, result_str in wait_group.get():
                            log.info("[%d] Processed record: %s", record_id, result_str)

                except Exception as e:
                    # If there was an error processing the records, log it but continue
                    log.error("Error processing records: %s", e)

                # Update the progress bar with the chunk size
                pbar.update(args.chunk_size)

            # Finish off the job groups that are left over.
            for group in groups:
                for record_id, result_str in group.get():
                    log.info("[%d] Processed record: %s", record_id, result_str)


def run():
    """Run the main function with common logging."""
    common_logging(__name__, __file__, level=logging.ERROR)
    main()


if __name__ == "__main__":
    run()

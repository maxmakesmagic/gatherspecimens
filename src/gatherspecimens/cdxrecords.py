"""Retrieves CDX records from Wayback Machine for a list of URLs."""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Generator, Iterator

import wayback
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from gatherspecimens.schema import Base, CdxRecordSpecimen
from gatherspecimens.utils import common_logging, get_engine, url_hash

log = logging.getLogger(__name__)


def process_results(results: Iterator[wayback.CdxRecord], engine: Engine):
    """Iterate over CDX records and stores them in the database."""
    added = 0

    with Session(engine) as db_session:
        for index, record in enumerate(results):
            raw_hash = url_hash(record.raw_url)

            if index % 100 == 0:
                log.info("[%d] Checking record", index)

            if (
                db_session.query(CdxRecordSpecimen)
                .filter(CdxRecordSpecimen.hash_raw_url == raw_hash)
                .first()
            ):
                # log.info("[%s] Record %s already scraped", run_id, record)
                continue

            new_record = CdxRecordSpecimen.from_cdx_record(record)
            db_session.add(new_record)
            added += 1

            if index % 100 == 0:
                log.info("[%d] Committing records (added so far: %d)", index, added)
                db_session.commit()


def process_url(url: str, engine: Engine, api_limit: int):
    """Process a URL and store found CDX records in the database."""
    session = wayback.WaybackSession(retries=20, backoff=0.5)
    client = wayback.WaybackClient(session=session)

    results: Generator[wayback.CdxRecord] = client.search(
        url, match_type="prefix", limit=api_limit
    )
    process_results(results, engine)


def main():
    """Process URLs for CDX records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        help="Path to the database configuration file",
        type=Path,
        default=Path("config.json"),
    )
    parser.add_argument(
        "--input",
        help="Path to the URL input file",
        type=Path,
        default=Path("input.json"),
    )
    parser.add_argument(
        "--limit",
        help="API limit for Wayback Machine",
        default=1000,
    )
    args = parser.parse_args()

    engine = get_engine(args.config)
    Base.metadata.create_all(engine)

    with open(args.input, "r") as f:
        urls = json.load(f)

    for url in urls:
        log.info("Processing URLs under %s", url)

        while True:
            try:
                process_url(url, engine, args.limit)
                break
            except Exception:
                log.exception("Error while processing; sleep a while")
                time.sleep(60)


def run():
    """Run the main function with common logging."""
    common_logging(__name__, __file__)
    main()


if __name__ == "__main__":
    run()

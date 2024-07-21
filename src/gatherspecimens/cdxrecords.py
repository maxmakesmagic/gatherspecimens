import json
import logging
import time
from typing import Generator, Iterator

import wayback
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from schema import Base, StoredCdxRecord
from utils import common_logging, url_hash

log = logging.getLogger(__name__)


def process_results(results: Iterator[wayback.CdxRecord], engine: Engine):
    added = 0

    with Session(engine) as db_session:
        for index, record in enumerate(results):
            raw_hash = url_hash(record.raw_url)

            if index % 100 == 0:
                log.info("[%d] Checking record", index)

            if (
                db_session.query(StoredCdxRecord)
                .filter(StoredCdxRecord.hash_raw_url == raw_hash)
                .first()
            ):
                # log.info("[%s] Record %s already scraped", run_id, record)
                continue

            new_record = StoredCdxRecord.from_cdx_record(record)
            db_session.add(new_record)
            added += 1

            if index % 100 == 0:
                log.info("[%d] Committing records (added so far: %d)", index, added)
                db_session.commit()


def process_url(url: str, engine: Engine):
    session = wayback.WaybackSession(retries=20, backoff=0.5)
    client = wayback.WaybackClient(session=session)

    results: Generator[wayback.CdxRecord] = client.search(url, match_type="prefix")
    process_results(results, engine)


def main():
    with open("config.json", "rb") as f:
        creds = json.load(f)
    connection_string = f"postgresql+psycopg2://{creds['user']}:{creds['pass']}@{creds['host']}:{creds['port']}/{creds['database']}"

    log.info("Connection string: %s", connection_string)

    # engine = create_engine(connection_string, echo=True)
    # Base.metadata.drop_all(engine)
    # return

    # engine = create_engine(connection_string, echo=True)
    # Base.metadata.create_all(engine)
    # return

    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)

    with open("input.json", "r") as f:
        urls = json.load(f)

    for url in urls:
        log.info("Processing URLs under %s", url)

        while True:
            try:
                process_url(url, engine)
                break
            except Exception as e:
                log.exception("Error while processing; sleep a while")
                time.sleep(60)


def run():
    common_logging("cdxrecords")
    main()


if __name__ == "__main__":
    run()

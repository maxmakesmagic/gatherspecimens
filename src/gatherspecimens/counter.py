"""Counts how many CDX records are stored in the database."""

import logging
import time

from sqlalchemy.orm import Session

from .schema import StoredCdxRecord
from .utils import common_logging, get_engine

log = logging.getLogger(__name__)


def main():
    """Count stored records."""
    engine = get_engine("config.json")

    with Session(engine) as db_session:
        while True:
            cdx_count = db_session.query(StoredCdxRecord).count()
            log.info("CDX records: %d", cdx_count)
            time.sleep(60)


def run():
    """Run the main function with common logging."""
    common_logging(__name__, __file__)
    main()


if __name__ == "__main__":
    run()

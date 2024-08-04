"""Extract test rows from the database."""

import logging
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from gatherspecimens.schema import CdxRecordSpecimen, MementoSpecimen
from gatherspecimens.utils import common_logging, get_engine

log = logging.getLogger(__name__)

tests = Path(__file__).parent
test_data = tests / "test_data"
root = tests.parent


def main():
    """Extract test rows from the main database."""
    engine = get_engine("config.json")

    with open(tests / "testrows.yml") as f:
        testrows = yaml.safe_load(f)

    with Session(engine) as db_session:
        for row in testrows:
            # Extract information about the row from both the
            # CdxRecordSpecimen and the MementoSpecimen tables.
            cdx_row = db_session.get(CdxRecordSpecimen, row)
            memento_row = db_session.get(MementoSpecimen, row)

            # Serialize the information so that we can write it to a file.
            data = {}
            if cdx_row:
                data["cdx"] = cdx_row.to_serializable()
            if memento_row:
                data["memento"] = memento_row.to_serializable()

            # Write the serialized information to a file.
            output_file = test_data / f"{row}.yml"
            with open(output_file, "w") as f:
                yaml.safe_dump(data, f)
            log.info("Extracted row %s as %s", row, output_file)


def run():
    """Run the main function with common logging."""
    common_logging(__name__, __file__)
    main()


if __name__ == "__main__":
    run()

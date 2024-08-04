"""Common fixtures for tests."""

import logging
from pathlib import Path

import pytest
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from gatherspecimens.schema import Base, CdxRecordSpecimen, MementoSpecimen

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def test_db_session():
    """Create a test database with SQLite and yield it."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    # Find all the test data files in the test_data directory.
    tests = Path(__file__).parent
    test_data = tests / "test_data"
    test_files = test_data.glob("*.yml")

    with Session(engine) as db_session:
        # Create test rows
        for test_file in test_files:
            with open(test_file) as f:
                test_data = yaml.safe_load(f)

            cdx_data = test_data.get("cdx")
            if cdx_data:
                cdx_row = CdxRecordSpecimen.from_serializable(cdx_data)
                db_session.add(cdx_row)
                log.debug("Added %s", cdx_row)

            memento_data = test_data.get("memento")
            if memento_data:
                memento_row = MementoSpecimen.from_serializable(memento_data)
                db_session.add(memento_row)
                log.debug("Added %s", memento_row)

        db_session.commit()

        log.debug("Yielding session")
        yield db_session
        log.debug("Finished yielding")

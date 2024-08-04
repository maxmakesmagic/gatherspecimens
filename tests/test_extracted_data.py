"""Tests for testing extracted data."""

import logging

from sqlalchemy.orm import Session

from gatherspecimens.schema import CdxRecordSpecimen

log = logging.getLogger(__name__)


def test_extract(test_db_session: Session):
    """Basic test to assert the existence of rows in the test database."""
    cdx_rows = test_db_session.query(CdxRecordSpecimen).all()
    log.info("CDX rows: %d", len(cdx_rows))
    assert len(cdx_rows) > 0

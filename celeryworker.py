"""Celery worker for distributed record gathering."""

import logging
import time
from typing import Any, Dict, Tuple

import wayback
from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from wayback.exceptions import MementoPlaybackError

from gatherspecimens.schema import (CdxRecordSpecimen, MementoFailure,
                                    MementoSpecimen)
from gatherspecimens.utils import get_engine

app = Celery("celeryworker")
app.config_from_object("celeryconfig")

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DistributedWayback(Task):
    """Task for distributed Wayback processing."""

    def __init__(self):
        """Set up common resources for the task."""
        self.engine = get_engine("config.json")
        self.session = wayback.WaybackSession(retries=20, backoff=0.5)
        self.client = wayback.WaybackClient(session=self.session)
        self.countdown = 10


# Add some time limits - some jobs lock up when trying to gather mementos
# and the time limits will kill them as necessary.
@app.task(base=DistributedWayback, bind=True, soft_time_limit=120, time_limit=150)
def process_cdx_record(
    self: DistributedWayback, ser: Dict[str, Any]
) -> Tuple[int, str]:
    """Process a CdxRecordSpecimen and stores the memento in the database."""
    record_specimen = CdxRecordSpecimen.from_serializable(ser)
    record = record_specimen.to_cdx_record()
    log.info("[%d] Processing record", record_specimen.id)

    if record.status_code and record.status_code >= 400:
        log.warning(
            "[%d] Record %s had error: status code %d",
            record_specimen.id,
            record_specimen.url,
            record_specimen.status_code,
        )
        return (record_specimen.id, f"status code error: {record_specimen.status_code}")

    with Session(self.engine) as db_session:
        # The result string is a friendly return message to the user
        # to show what happened with the memento gathering.
        result_str = "unknown"

        try:
            start_time = time.time()
            memento = self.client.get_memento(record)
            memento_time = time.time() - start_time
            log.info("[%s] Memento gather time: %s", record_specimen.id, memento_time)

            if memento.ok:
                new_page = MementoSpecimen(
                    id=record_specimen.id,
                    hash_raw_url=record_specimen.hash_raw_url,
                    raw_url=record_specimen.raw_url,
                    url=record_specimen.url,
                    mime_type=record_specimen.mime_type,
                    status_code=record_specimen.status_code,
                    time=record.timestamp,
                    view_url=record_specimen.view_url,
                    html_content=memento.content,
                )
                db_session.add(new_page)
                log.info("[%s] Result processed %s", record_specimen.id, record.url)
                result_str = "gathered"
            else:
                log.warning(
                    "[%s] Memento had error: status code %d",
                    record_specimen.id,
                    memento.status_code,
                )
                new_memfail = MementoFailure(id=record_specimen.id)
                db_session.add(new_memfail)
                result_str = f"memento error: {memento.status_code}"

        except SoftTimeLimitExceeded as e:
            log.error("[%s] Result hit soft time limit: %s", record_specimen.id, e)
            new_memfail = MementoFailure(id=record_specimen.id)
            db_session.add(new_memfail)
            result_str = f"soft time limit exceeded: {e}"

        except MementoPlaybackError as e:
            log.debug("[%s] Result hit mementoplaybackerror %s", record_specimen.id, e)
            new_memfail = MementoFailure(id=record_specimen.id)
            db_session.add(new_memfail)
            result_str = f"memento playback error: {e}"

        except ConnectionResetError as e:
            log.error(
                "[%s] Connection reset error, retrying in %d seconds: %s",
                record_specimen.id,
                self.countdown,
                e,
            )
            raise self.retry(countdown=self.countdown, exc=e)

        except Exception as e:
            log.debug("[%s] Result hit exception %s", record_specimen.id, e)
            result_str = f"exception: {e}"

        db_start_time = time.time()
        try:
            db_session.commit()
        except SQLAlchemyError as e:
            log.error("[%s] Error committing record: %s", record_specimen.id, e)
            result_str = "error while committing"
        db_time = time.time() - db_start_time
        log.info("[%s] Database commit time: %s", record_specimen.id, db_time)

    # Return the ID that was processed and the result string
    return record_specimen.id, result_str

"""Utility functions for the gatherspecimens package."""

import hashlib
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import Engine, create_engine

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def url_hash(url: str) -> str:
    """Hash a URL using SHA-256."""
    m = hashlib.sha256()
    m.update(url.encode("utf-8"))
    return m.hexdigest()


def nospecial(url: str) -> str:
    """Remove special characters from a URL."""
    return re.sub(r"[^a-zA-Z0-9\_\-]+", "_", url)


def common_logging(name: str, filename: str):
    """Set up common logging for scripts."""
    if name == "__main__":
        name = Path(filename).stem

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    logs = Path("logs")
    logs.mkdir(exist_ok=True)
    log_filename = logs / f"{name}.{timestamp}.log"

    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    # Suppress spammy logging
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("wayback").setLevel(logging.INFO)


def get_engine(config_file: Path) -> Engine:
    """Create an SQLAlchemy engine from a JSON configuration."""
    with open(config_file, "r") as f:
        creds = json.load(f)
    connection_string = (
        f"postgresql+psycopg2://{creds['user']}:"
        f"{creds['pass']}@{creds['host']}:{creds['port']}"
        f"/{creds['database']}"
    )

    log.debug("Connection string: %s", connection_string.replace(creds["pass"], "****"))
    engine = create_engine(connection_string)
    return engine

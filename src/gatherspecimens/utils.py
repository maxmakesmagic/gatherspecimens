import hashlib
import logging
import re
import sys
from datetime import datetime
from pathlib import Path


def url_hash(url: str) -> str:
    m = hashlib.sha256()
    m.update(url.encode("utf-8"))
    return m.hexdigest()


def nospecial(url: str) -> str:
    return re.sub("[^a-zA-Z0-9\_\-]+", "_", url)


def common_logging(name: str):
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

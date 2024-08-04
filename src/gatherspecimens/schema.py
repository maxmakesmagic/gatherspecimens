"""SQLAlchemy schema for the gatherspecimens package."""

import base64
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Integer, LargeBinary, String, UnicodeText
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing_extensions import Self
from wayback import CdxRecord

from gatherspecimens.utils import url_hash


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class CdxRecordSpecimen(Base):
    """Model for storing CDX records in the database."""

    __tablename__ = "cdx_record_specimen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hash_raw_url: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    key: Mapped[str] = mapped_column(UnicodeText)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    url: Mapped[str] = mapped_column(UnicodeText)
    mime_type: Mapped[str] = mapped_column(String)
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    digest: Mapped[str] = mapped_column(String)
    length: Mapped[Optional[int]] = mapped_column(Integer)
    raw_url: Mapped[str] = mapped_column(UnicodeText)
    view_url: Mapped[str] = mapped_column(UnicodeText)

    @classmethod
    def from_cdx_record(cls, record: CdxRecord) -> Self:
        """Create a new instance from a CdxRecord."""
        return cls(
            hash_raw_url=url_hash(record.raw_url),
            key=record.key,
            timestamp=record.timestamp,
            url=record.url,
            mime_type=record.mime_type,
            status_code=record.status_code,
            digest=record.digest,
            length=record.length,
            raw_url=record.raw_url,
            view_url=record.view_url,
        )

    def to_cdx_record(self) -> CdxRecord:
        """Convert the instance to a CdxRecord."""
        timestamp = self.timestamp.replace(tzinfo=timezone.utc)
        return CdxRecord(
            key=self.key,
            timestamp=timestamp,
            url=self.url,
            mime_type=self.mime_type,
            status_code=self.status_code,
            digest=self.digest,
            length=self.length,
            raw_url=self.raw_url,
            view_url=self.view_url,
        )

    def to_serializable(self) -> Dict[str, Any]:
        """Convert the instance to a serializable dictionary."""
        return {
            "id": self.id,
            "hash_raw_url": self.hash_raw_url,
            "key": self.key,
            "timestamp": self.timestamp,
            "url": self.url,
            "mime_type": self.mime_type,
            "status_code": self.status_code,
            "digest": self.digest,
            "length": self.length,
            "raw_url": self.raw_url,
            "view_url": self.view_url,
        }

    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> Self:
        """Create a new instance from a serializable dictionary."""
        return cls(
            id=data["id"],
            hash_raw_url=data["hash_raw_url"],
            key=data["key"],
            timestamp=data["timestamp"],
            url=data["url"],
            mime_type=data["mime_type"],
            status_code=data["status_code"],
            digest=data["digest"],
            length=data["length"],
            raw_url=data["raw_url"],
            view_url=data["view_url"],
        )


class MementoSpecimen(Base):
    """Model for storing scraped pages in the database."""

    __tablename__ = "memento_specimen"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash_raw_url: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    raw_url: Mapped[str] = mapped_column(UnicodeText)
    url: Mapped[str] = mapped_column(UnicodeText, index=True)
    mime_type: Mapped[str] = mapped_column(String)
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    time: Mapped[datetime] = mapped_column(DateTime)
    view_url: Mapped[str] = mapped_column(UnicodeText)
    html_content: Mapped[bytes] = mapped_column(LargeBinary)

    def to_serializable(self) -> Dict[str, Any]:
        """Convert the instance to a serializable dictionary."""
        base64_content = base64.b64encode(self.html_content).decode("utf-8")
        return {
            "id": self.id,
            "hash_raw_url": self.hash_raw_url,
            "raw_url": self.raw_url,
            "url": self.url,
            "mime_type": self.mime_type,
            "status_code": self.status_code,
            "time": self.time,
            "view_url": self.view_url,
            "html_content": base64_content,
        }

    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> Self:
        """Create a new instance from a serializable dictionary."""
        content = base64.b64decode(data["html_content"])
        return cls(
            id=data["id"],
            hash_raw_url=data["hash_raw_url"],
            raw_url=data["raw_url"],
            url=data["url"],
            mime_type=data["mime_type"],
            status_code=data["status_code"],
            time=data["time"],
            view_url=data["view_url"],
            html_content=content,
        )


class MementoFailure(Base):
    """Model for storing failed memento retrievals in the database."""

    __tablename__ = "memento_failure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

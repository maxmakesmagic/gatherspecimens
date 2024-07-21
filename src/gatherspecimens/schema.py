"""SQLAlchemy schema for the gatherspecimens package."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, LargeBinary, String, UnicodeText
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing_extensions import Self
from wayback import CdxRecord

from .utils import url_hash


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class StoredCdxRecord(Base):
    """Model for storing CDX records in the database."""

    __tablename__ = "stored_cdx_record"

    hash_raw_url: Mapped[str] = mapped_column(String(64), primary_key=True)
    key: Mapped[str] = mapped_column(UnicodeText)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
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
        return CdxRecord(
            key=self.key,
            timestamp=self.timestamp,
            url=self.url,
            mime_type=self.mime_type,
            status_code=self.status_code,
            digest=self.digest,
            length=self.length,
            raw_url=self.raw_url,
            view_url=self.view_url,
        )


class Scraped(Base):
    """Model for storing scraped pages in the database."""

    __tablename__ = "scraped"

    hash_raw_url: Mapped[str] = mapped_column(String(64), primary_key=True)
    raw_url: Mapped[str] = mapped_column(UnicodeText)
    url: Mapped[str] = mapped_column(UnicodeText, index=True)
    mime_type: Mapped[str] = mapped_column(String)
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    time: Mapped[datetime] = mapped_column(DateTime)
    view_url: Mapped[str] = mapped_column(UnicodeText)
    html_content: Mapped[bytes] = mapped_column(LargeBinary)

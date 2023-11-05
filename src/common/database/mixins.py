from datetime import datetime

from sqlalchemy import func, DateTime
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase

from src.common.types.db_types import int_pk


class BaseClass(DeclarativeBase):
    __table__: str


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )


class IdPrimaryKeyMixin:
    id: Mapped[int_pk] = mapped_column()

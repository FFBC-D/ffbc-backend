from datetime import datetime

from sqlalchemy import func, DateTime
from sqlalchemy.orm import mapped_column, Mapped, declarative_mixin

from src.common.types.db_types import int_pk


@declarative_mixin
class BaseClass:
    __table__: str

    id: Mapped[int_pk] = mapped_column(init=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), init=False
    )

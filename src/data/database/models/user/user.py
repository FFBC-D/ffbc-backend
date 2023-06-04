from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from src.common.database.mixins import BaseClass
from src.data.database.models import mapper_registry


@mapper_registry.mapped_as_dataclass(kw_only=True)
class User(BaseClass):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    phone: Mapped[str | None] = mapped_column(nullable=True, unique=True, default=None)
    birth_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    street: Mapped[str | None] = mapped_column(nullable=True, default=None)
    city: Mapped[str | None] = mapped_column(nullable=True, default=None)
    country: Mapped[str | None] = mapped_column(nullable=True, default=None)

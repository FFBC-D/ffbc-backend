from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.database.mixins import BaseClass
from src.data.database.models import mapper_registry

if TYPE_CHECKING:
    from src.data.database.models.jwt import BlacklistToken


@mapper_registry.mapped_as_dataclass(kw_only=True)
class OutstandingToken(BaseClass):
    __tablename__ = "outstanding_tokens"

    user_id: Mapped[int] = mapped_column(nullable=False)
    jti: Mapped[str] = mapped_column(nullable=False, index=True)
    token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    blacklist_token: Mapped["BlacklistToken"] = relationship(
        back_populates="outstanding_token", uselist=False, init=False
    )

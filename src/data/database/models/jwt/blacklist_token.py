from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.common.database.mixins import BaseClass
from src.data.database.models import mapper_registry

if TYPE_CHECKING:
    from src.data.database.models.jwt import OutstandingToken


@mapper_registry.mapped_as_dataclass(kw_only=True)
class BlacklistToken(BaseClass):
    __tablename__ = "blacklist_tokens"

    outstanding_token_id: Mapped[int] = mapped_column(
        ForeignKey("outstanding_tokens.id"),
    )
    outstanding_token: Mapped["OutstandingToken"] = relationship(
        back_populates="blacklist_token", uselist=False, init=False
    )

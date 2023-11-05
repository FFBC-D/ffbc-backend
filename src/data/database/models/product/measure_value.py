from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.database.mixins import BaseClass, TimestampMixin, IdPrimaryKeyMixin

if TYPE_CHECKING:
    from .measure_category import MeasureCategory


class MeasureValue(IdPrimaryKeyMixin, TimestampMixin, BaseClass):
    __tablename__ = "measure_values"

    name: Mapped[str] = mapped_column(nullable=False, doc="Название")
    category_id: Mapped[int] = mapped_column(ForeignKey("measure_categories.id"), nullable=False)
    category: Mapped["MeasureCategory"] = relationship(back_populates="values", uselist=False)

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.database.mixins import BaseClass, IdPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from .product_category import ProductCategory
    from .measure_value import MeasureValue


class MeasureCategory(IdPrimaryKeyMixin, TimestampMixin, BaseClass):
    __tablename__ = "measure_categories"

    name: Mapped[str] = mapped_column(nullable=False, doc="Название")
    product_categories: Mapped[list["ProductCategory"]] = relationship(
        secondary="product_categories_measure_categories",
        back_populates="measure_categories",
    )
    values: Mapped[list["MeasureValue"]] = relationship(back_populates="category")

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.common.database.mixins import BaseClass


class ProductCategoryMeasureCategory(BaseClass):
    __tablename__ = "product_categories_measure_categories"

    product_category_id: Mapped[int] = mapped_column(
        ForeignKey("product_categories.id"), primary_key=True
    )
    measure_category_id: Mapped[int] = mapped_column(
        ForeignKey("measure_categories.id"), primary_key=True
    )

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.common.database.mixins import BaseClass


class ProductCategoryModification(BaseClass):
    __tablename__ = "product_categories_modifications"

    product_category_id: Mapped[int] = mapped_column(
        ForeignKey("product_categories.id"), primary_key=True
    )
    product_modification_id: Mapped[int] = mapped_column(
        ForeignKey("product_modifications.id"), primary_key=True
    )

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.common.database.mixins import BaseClass, IdPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from src.data.database.models.product.product_modification import ProductModification
    from src.data.database.models.product.product import Product
    from src.data.database.models.product import MeasureCategory


class ProductCategory(IdPrimaryKeyMixin, TimestampMixin, BaseClass):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(nullable=False, doc="Название")
    measure_categories: Mapped[list["MeasureCategory"]] = relationship(
        secondary="product_categories_measure_categories",
        back_populates="product_categories",
        lazy="selectin",
    )
    product_modifications: Mapped[list["ProductModification"]] = relationship(
        secondary="product_categories_modifications",
        back_populates="product_categories",
        lazy="selectin",
    )
    products: Mapped["Product"] = relationship(back_populates="product_category")

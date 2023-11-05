from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.common.database.mixins import BaseClass, IdPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from src.data.database.models.product.product_category import ProductCategory


class Product(IdPrimaryKeyMixin, TimestampMixin, BaseClass):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(nullable=False, doc="Название")
    base_price: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=6), doc="Базовая цена")
    price_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(precision=9, scale=6), doc="Множитель цены"
    )
    description: Mapped[str | None] = mapped_column(nullable=True, doc="Описание")
    video: Mapped[str] = mapped_column(nullable=True, doc="Видео")

    product_category_id: Mapped[int] = mapped_column(ForeignKey("product_categories.id"))
    product_category: Mapped["ProductCategory"] = relationship(back_populates="products")

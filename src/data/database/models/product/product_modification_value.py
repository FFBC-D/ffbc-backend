from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.database.mixins import BaseClass, IdPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from src.data.database.models.product.product_modification import ProductModification


class ProductModificationValue(IdPrimaryKeyMixin, TimestampMixin, BaseClass):
    __tablename__ = "product_modification_values"

    name: Mapped[str] = mapped_column(nullable=False, doc="Название")
    price: Mapped[Decimal] = mapped_column(Numeric(precision=9, scale=6))
    modification_id: Mapped[int] = mapped_column(
        ForeignKey("product_modifications.id"), nullable=False
    )
    modification: Mapped["ProductModification"] = relationship(back_populates="values")

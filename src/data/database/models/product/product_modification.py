from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.common.database.mixins import BaseClass, IdPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from src.data.database.models.product.product_category import ProductCategory
    from src.data.database.models.product import ProductModificationValue


class ProductModification(IdPrimaryKeyMixin, TimestampMixin, BaseClass):
    __tablename__ = "product_modifications"

    name: Mapped[str] = mapped_column(nullable=False, doc="Название")
    icon: Mapped[str] = mapped_column(nullable=True, doc="Иконка")
    product_categories: Mapped[list["ProductCategory"]] = relationship(
        secondary="product_categories_modifications", back_populates="product_modifications"
    )
    values: Mapped[list["ProductModificationValue"]] = relationship(back_populates="modification")

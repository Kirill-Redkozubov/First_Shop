from decimal import Decimal
from sqlalchemy import String, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship  # New
from sqlalchemy import ForeignKey  # New

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(200))
    stock: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))  # New
    seller_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category: Mapped["Category"] = relationship(back_populates="products")  # New
    seller: Mapped['User'] = relationship(back_populates='products')
    reviews: Mapped[list['Review']] = relationship(back_populates='product')
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), default=Decimal('0.00'))
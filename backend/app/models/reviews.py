from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base





class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    comment: Mapped[str | None] = mapped_column(String(200))
    comment_date: Mapped[datetime] = mapped_column(default=datetime.now)
    grade: Mapped[int] = mapped_column(
        CheckConstraint('grade >= 1 and grade <= 5'),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped['User'] = relationship(back_populates='reviews')
    product: Mapped['Product'] = relationship(back_populates='reviews')



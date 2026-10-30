from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db
from app.models import Product as ProductModel
from app.models import Review as ReviewModel

async def recalculate_product_grade(product_id: int, db: AsyncSession):
    new_rating = await db.scalar(select(func.avg(ReviewModel.grade)).where(ReviewModel.product_id == product_id, ReviewModel.is_active))
    product = await db.get(ProductModel, product_id)
    if new_rating:
        product.rating = round(float(new_rating), 2)
    else: product.rating = 0
    
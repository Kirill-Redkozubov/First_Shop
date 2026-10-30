from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin, get_current_buyer
from app.db_depends import get_async_db
from app.schemas import Review, ReviewCreate
from app.models import Review as ReviewModel
from app.models import User as UserModel
from app.models import Product as ProductModel
from app.services.item_rating import recalculate_product_grade



router = APIRouter(prefix='/reviews', tags=['reviews'])


db_session = Annotated[AsyncSession, Depends(get_async_db)]
current_buyer = Annotated[UserModel, Depends(get_current_buyer)]
current_admin = Annotated[UserModel, Depends(get_current_admin)]

@router.get('/', response_model=list[Review])
async def all_reviews(db: db_session):
    reviews = await db.scalars(select(ReviewModel).where(ReviewModel.is_active))
    return reviews.all()

@router.post('/', response_model=Review)
async def create_review(new_review: ReviewCreate, current_user: current_buyer, db: db_session):
    product = await db.scalar(select(ProductModel).where(ProductModel.id == new_review.product_id, ProductModel.is_active))
    if not product:
        raise HTTPException(status_code=400, detail='product not found or inactive')
    review = ReviewModel(**new_review.model_dump(), user_id=current_user.id)
    db.add(review)
    await db.flush()
    #Расчет средней оценки! services/item_rating
    await recalculate_product_grade(product.id, db)
    await db.commit()
    await db.refresh(review)
    return review


@router.delete('/{review_id}')
async def delete_review_by_id(review_id: int, current_user: current_admin, db: db_session):
    review = await db.scalar(select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active))
    if not review:
        raise HTTPException(status_code=404, detail='review not found')
    review.is_active = False
    await db.flush()
    await recalculate_product_grade(review.product_id, db)
    await db.commit()
    return {'message': 'Review deleted'}
    
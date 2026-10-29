from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, update
from app.auth import get_current_seller
from app.schemas import Product as ProductSchema, ProductCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.models import Product as ProductModel, Category as CategoryModel
from app.models import User as UserModel



# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)

db_session = Annotated[AsyncSession, Depends(get_async_db)]
current_seller = Annotated[UserModel, Depends(get_current_seller)]


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: db_session):
    result = await db.scalars(select(ProductModel).where(ProductModel.is_active))
    return result.all()
    
    

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, current_user: current_seller, db: db_session):
    db_categories = await db.scalar(select(CategoryModel).where(CategoryModel.id == product.category_id,
                                                          CategoryModel.is_active))
    if not db_categories:
        raise HTTPException(status_code=400, detail=f'Category_id: {product.category_id} not found or inactive')
    new_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product
    

@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: db_session):
    result = (await db.scalars(select(ProductModel).where(ProductModel.category_id == category_id,
                                                   ProductModel.is_active))).all()
    if not result:
        raise HTTPException(status_code=404, detail=f'Product with category: {category_id} not found')
    return result
    


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: int, db: db_session):
    result = await db.scalar(select(ProductModel).where(ProductModel.id == product_id, 
                                                   ProductModel.is_active))
    if not result:
        raise HTTPException(status_code=404, detail=f'Product with id: {product_id} not found')
    return result


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(product_id: int, current_user: current_seller, update_product: ProductCreate, db: db_session):
    db_product = await db.scalar(select(ProductModel).where(ProductModel.id == product_id))
    if not db_product:
        raise HTTPException(status_code=404, detail=f'Product with id: {product_id} not found')
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You can only update your own products')
    db_category = await db.scalar(select(CategoryModel).where(CategoryModel.id == update_product.category_id))
    if not db_category:
        raise HTTPException(status_code=404, detail=f'Category with id: {update_product.category_id} not found')
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(**update_product.model_dump()))
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, current_user: current_seller, db: db_session):
    product = await db.scalar(select(ProductModel).where(ProductModel.is_active, ProductModel.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail=f'Product with id: {product_id} not found or inactive')
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You can only delete your own products')
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    await db.commit()
    await db.refresh(product)
    return product
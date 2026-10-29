from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from app.auth import get_current_admin
from app.schemas import Category as CategorySchema, CategoryCreate
from app.models import Category as CategoryModel, User as UserModel
from app.db_depends import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession




# Создаём маршрутизатор с префиксом и тегом
router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)

db_session = Annotated[AsyncSession, Depends(get_async_db)]
current_admin = Annotated[UserModel, Depends(get_current_admin)]



@router.get("/", response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def get_all_categories(db: db_session):
    result = await db.scalars(select(CategoryModel).where(CategoryModel.is_active == True))
    return result.all()
    
    
@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, current_user: current_admin, db: db_session):
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id,
                                           CategoryModel.is_active == True)
        parent = await db.scalar(stmt)
        if parent is None:
            raise HTTPException(status_code=404, detail='Parent category not found')
    
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, current_user: current_admin, category: CategoryCreate, db: db_session):
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True)
    #категория которую обновляем
    db_category = await db.scalar(stmt)
    if not db_category:
        raise HTTPException(status_code=404, detail='Category not found')
    if category.parent_id is not None:
        #категорию на которую хотим ссылаться в обновленной категории
        parent = await db.scalar(select(CategoryModel).where(CategoryModel.id == category.parent_id, 
                                                       CategoryModel.is_active == True))
        if not parent:
            raise HTTPException(status_code=404, detail='Parent not found')
        # если категория родитель сама себе (id == parent_id)
        if category_id == category.parent_id:
            raise HTTPException(status_code=400, detail="Category can't be its own parent")
    db_category.parent_id = category.parent_id
    db_category.name = category.name
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, current_user: current_admin, db: db_session):
    stmt = update(CategoryModel).where(CategoryModel.id == category_id, 
                                       CategoryModel.is_active == True).values(is_active=False)
    result = await db.execute(stmt)
    print(f'Изменено строк: {result.rowcount}')
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f'Category with id: {category_id} not found')
    await db.commit()
    return {"status": "success", "message": "Category marked as inactive"}
    
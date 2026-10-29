from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, select, update
from database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promocode import PromoCodeModel

router = APIRouter()

@router.delete('/{promocode_id}')
async def get_projects(promocode_id: int, db: AsyncSession = Depends(get_async_db)):
    promo = await db.get(PromoCodeModel, promocode_id)
    if promo and promo.is_active:
        promo.is_active = False
        await db.commit()
        return {"status": "success", "message": "Promocode marked as inactive"}
    raise HTTPException(status_code=404, detail='error')
    




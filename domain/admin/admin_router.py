from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from domain.admin import admin_schema, admin_crud


router = APIRouter(
    prefix = "KU/admin"
)

@router.post("/SignIn",status_code = 201)
async def admin_sign_in(request : admin_schema.LogInData, db : AsyncSession):
    _result = await admin_sign_in_db(request, db)
    return _result

@router.post("/Carving",status_code = 201)
async def admin_sign_in(request : admin_schema.LogInData, db : AsyncSession):
    _result = await admin_sign_in_db(request, db)
    return _result

@router.post("/Post",status_code = 201)
async def create_post_in(request : admin_schema.PostRequest, db : AsyncSession):
    _result = await create_post_in_db(request, db)
    return _result

@router.post("/Clean/Match",status_code = 201)
async def admin_sign_in(request : admin_schema.LogInData, db : AsyncSession):
    _result = await admin_sign_in_db(request, db)
    return _result
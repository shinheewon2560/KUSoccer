from fastapi import APIRouter, Depends,Response,status
from sqlalchemy.orm import Session
from domain.user import user_schema

from database import get_DB
from domain.user import user_schema, user_crud

router = APIRouter(
    prefix = "/KU/User"
)

#회원가입
@router.post("/sign")
def sign_up(response : Response, request : user_schema.UserInformation, db : Session = Depends(get_DB)):
    _result  = user_crud.sign_on(request,db)
    response.status_code = status.HTTP_202_ACCEPTED

    return _result

"""
@router.delete("/sign")
def user_delete(resopnse : Response, password : str, db : Session = Depends(get_DB)):
    _result = user_crud.delete(,db)
    return _result
"""
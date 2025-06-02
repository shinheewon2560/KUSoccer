from fastapi import APIRouter, Depends,Response,status
from sqlalchemy.orm import Session

from models import User
from database import get_DB
from domain.user import user_schema, user_crud

router = APIRouter(
    prefix = "/KU/User"
)

#회원가입
@router.post("/sign_up")
def sign_up(response : Response, request : user_schema.UserInformation, db : Session = Depends(get_DB)):
    _result  = user_crud.crave_on_DB(request,db)
    response.status_code = status.HTTP_202_ACCEPTED
    return _result


@router.post("/sign_in")
def sign_in(response : Response, request : user_schema.SignInData, db : Session = Depends(get_DB)):
    _result = user_crud.sign_in(request.e_mail, request.password,db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.post("/verify-password")
def check_password(response : Response, password : user_schema.Password , request_user_id : int = Depends(user_crud.get_and_check_token_and_return_id), db : Session = Depends(get_DB)):
    data = db.query(User).filter(User.id == request_user_id).first()
    password_str = password.password
    if data.hash != user_crud.hashing(password_str + data.salt):
        response.status_code = status.HTTP_403_FORBIDDEN
        return{"message" : "비밀번호가 일치하지 않습니다."}

    return {"message":"인증되었습니다"}

@router.put("/recarve")
def imodify_info(response : Response, request : user_schema.UserInformation, request_user_id : int, db : Session = Depends(get_DB)):
    _result = user_crud.recarving_info(request, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

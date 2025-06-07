from fastapi import APIRouter, Depends,Response,status
from sqlalchemy.orm import Session

from models import User
from database import get_DB
from domain.user import user_schema, user_crud

router = APIRouter(
    prefix = "/KU/User"
)

#회원가입
@router.post("/SignUp")
def sign_up(response : Response, request : user_schema.UserCreate, db : Session = Depends(get_DB)):
    _result  = user_crud.sign_up_in_db(request,db)
    response.status_code = status.HTTP_202_ACCEPTED
    return _result
#e_mail이 유효한 e_mail인지 확인하는 검증절차 필요(e_mail로 인증메일 발송등)

@router.post("/SignIn")
def sign_in(response : Response, request : user_schema.LogInInput, db : Session = Depends(get_DB)):
    _result = user_crud.authenticate_user(request,db)
    response.status_code = status.HTTP_200_OK
    return _result

#user정봅 수정 등 추가적인 확인이 필요할 때 쓰는 url
@router.get("/Verify-password")
def check_password(response : Response, password : user_schema.Password , request_user_id : int = Depends(user_crud.check_token_and_return_id), db : Session = Depends(get_DB)):
    data = db.query(User).filter(User.id == request_user_id).first()
    password_str = password.password
    if data.hash != user_crud.hashing(password_str + data.salt):
        response.status_code = status.HTTP_403_FORBIDDEN
        return{"message" : "비밀번호가 일치하지 않습니다."}

    return {"message":"인증되었습니다"}

#Verrify_password를 거쳤는지 확인하는 보안점 한번 더 확인
@router.get("/MyProfile")
def print_my_profile(response: Response, request_user_id : int = Depends(user_crud.check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = user_crud.get_my_profile_from_db(request_user_id,db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.put("/MyProfile")
def modify_info(response : Response, request : user_schema.UserUpdate, request_user_id : int = Depends(user_crud.check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = user_crud.modify_info_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.get("/Profile")
def print_user_profile(response: Response, user_id : int , request_user_id : int = Depends(user_crud.check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = user_crud.get_user_profile_from_db(request_user_id, user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

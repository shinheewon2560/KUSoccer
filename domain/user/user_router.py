from fastapi import APIRouter, Depends,Response,status
from sqlalchemy.ext.asyncio import AsyncSession


from database import get_DB
from domain.user import user_schema, user_crud

router = APIRouter(
    prefix = "/KU/User"
)

#회원가입
@router.post("/SignUp")
async def sign_up(response : Response, request : user_schema.UserCreate, db : AsyncSession = Depends(get_DB)):
    _result  = await user_crud.sign_up_in_db(request,db)
    response.status_code = status.HTTP_201_CREATED
    return _result
#e_mail이 유효한 e_mail인지 확인하는 검증절차 필요(e_mail로 인증메일 발송등)

@router.post("/SignIn")
async def sign_in(response : Response, request : user_schema.LogInInput, db : AsyncSession = Depends(get_DB)):
    _result = await user_crud.authenticate_user(request,db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.get("/Profile")
async def get_user_profile(response: Response, user_id : int , request_user_id : int = Depends(user_crud.get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await user_crud.get_user_profile_from_db(request_user_id, user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

#user정보 수정 등 추가적인 확인이 필요할 때 쓰는 url
#2차 검증이라고 보면 됨
@router.post("/Auth")
async def check_password(response : Response, password : user_schema.Password , payload : dict = Depends(user_crud.decode_token), db : AsyncSession = Depends(get_DB)):
    _result = await user_crud.check_password_in_db(password.password, payload, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.get("/Profile/Me")
async def get_my_profile(response: Response,request_user_id : int = Depends(user_crud.get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await user_crud.get_my_profile_from_db(request_user_id,db)
    response.status_code = status.HTTP_200_OK
    return _result

#Verrify_password를 거쳤는지 확인하는 보안점 한번 더 확인
#-> 새로운 jwt토큰을 하나 더 발급(유효시간 5분)해서 해결
#-> 프론트에서 jwt토큰을 스택으로 관리해서 유효하지 않은 토큰이면 이전 토큰을 사용할 수 있게 요청
@router.put("/Profile/Me")
async def modify_info(response : Response, request : user_schema.UserUpdate, request_user_id : int = Depends(user_crud.get_id_from_doubly_verified_token), db : AsyncSession = Depends(get_DB)):
    _result = await user_crud.modify_info_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/Me")
async def delete_user(response : Response,request_user_id : int = Depends(user_crud.get_id_from_doubly_verified_token), db : AsyncSession = Depends(get_DB)):
    await user_crud.delete_user_in_db(request_user_id, db)
    response.status_code = status.HTTP_204_NO_CONTENT
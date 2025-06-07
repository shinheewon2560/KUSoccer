from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from fastapi import Depends
from sqlalchemy.orm import Session

from models import Crew
from database import get_DB
from domain.crew import crew_schema, crew_crud
from domain.user.user_crud import check_token_and_return_id

router = APIRouter(
    prefix = "/KU/Crew"
)

@router.post("/NewCrew")
def creat_crew(response : Response, request : crew_schema.CreateCrewRequest ,request_user_id : int = Depends(check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = crew_crud.create_crew_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.get("/Profile")
def get_info(response : Response, crew_id : int, db : Session = Depends(get_DB)):
    _result = crew_crud.get_info_in_db(crew_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

"""
    리더만 멤버 추가, 삭제가 가능하도록 설정
"""

@router.post("/Member")
def add_member(response : Response, request : crew_schema.UserEmail, request_user_id : int = Depends(check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = crew_crud.add_member_in_db(request.e_mail,request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/Member")
def delete_member(response : Response, request : crew_schema.UserEmail , request_user_id : int = Depends(check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = crew_crud.delete_member_in_db(request.e_mail, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result
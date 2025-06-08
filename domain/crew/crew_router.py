from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from fastapi import Depends
from sqlalchemy.orm import Session

from models import Crew
from database import get_DB
from domain.crew import crew_schema, crew_crud
from domain.user.user_crud import get_id_from_token

router = APIRouter(
    prefix = "/KU/Crew"
)

@router.post("/")
def creat_crew(response : Response, request : crew_schema.CreateCrewRequest ,request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = crew_crud.create_crew_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.get("/{crew_id}")
def get_info(response : Response, crew_id : int, db : Session = Depends(get_DB)):
    _result = crew_crud.get_info_in_db(crew_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/{crew_id}/Me")
def delete_member_by_self(response : Response, crew_id : int, request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = crew_crud.delete_member_by_self_in_db(crew_id, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

"""
    리더 전용 url
"""

@router.post("/{crew_id}/Member")
def add_member(response : Response, crew_id : int, request : crew_schema.UserEmail, request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = crew_crud.add_member_in_db(crew_id,request.e_mail,request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/{crew_id}/Member")
def delete_member_by_leader(response : Response, crew_id : int, request : crew_schema.UserEmail , request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = crew_crud.delete_member_by_leader_in_db(crew_id, request.e_mail, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/{crew_id}")
def delete_crew(response : Response, crew_id : int, request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = crew_crud.delete_crew_in_db(crew_id, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

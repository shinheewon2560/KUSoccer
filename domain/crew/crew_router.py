from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_DB
from domain.crew import crew_schema, crew_crud
from domain.user.user_crud import get_id_from_token

router = APIRouter(
    prefix = "/KU/Crew"
)

@router.post("/")
async def creat_crew(response : Response, request : crew_schema.CreateCrewRequest ,request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.create_crew_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.get("/{crew_id}")
async def get_info(response : Response, crew_id : int, db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.get_info_in_db(crew_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/{crew_id}/Member")
async def delete_member_by_self(response : Response, crew_id : int, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    await crew_crud.delete_member_by_self_in_db(crew_id, request_user_id, db)
    response.status_code = status.HTTP_204_NO_CONTENT

@router.post("/{crew_id}/Member/Apply")
async def apply_crew(response : Response, crew_id : int, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.apply_crew_in_db(crew_id, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

"""
    #리더 전용 url
"""
@router.post("/{crew_id}/Leader/leader",status_code = 201)
async def add_leader(crew_id : int , request : crew_schema.UserEmail, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.add_leader_in_db(crew_id, request, request_user_id, db)
    return _result

@router.delete("/{crew_id}/Leader/leader",status_code = 204)
async def delete_leader(crew_id : int , request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    await crew_crud.delete_leader_in_db(crew_id,request_user_id, db)

@router.put("/{crew_id}/Leader/Profile", status_code= 200)
async def modify_crew_profile(crew_id : int, request : crew_schema.ModifyCrewRequest, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.modify_crew_profile_in_db(crew_id,request,request_user_id,db)
    return _result

@router.get("/{crew_id}/Leader/Apply")
async def get_apply_list(response : Response, crew_id : int, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.get_apply_list_in_db(crew_id, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.post("/{crew_id}/Leader/Accept")
async def accept_user(response : Response, crew_id : int, request : crew_schema.CrewAcceptRequest, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.accept_user_in_db(crew_id,request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.post("/{crew_id}/Leader/member")
async def add_member(response : Response, crew_id : int, request : crew_schema.UserEmail, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await crew_crud.add_member_in_db(crew_id,request.e_mail,request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.delete("/{crew_id}/Leader/member")
async def delete_member_by_leader(response : Response, crew_id : int, request : crew_schema.UserEmail , request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    await crew_crud.delete_member_by_leader_in_db(crew_id, request.e_mail, request_user_id, db)
    response.status_code = status.HTTP_204_NO_CONTENT

@router.delete("/{crew_id}/Leader/")
async def delete_crew(response : Response, crew_id : int, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    await crew_crud.delete_crew_in_db(crew_id, request_user_id, db)
    response.status_code = status.HTTP_204_NO_CONTENT


from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from domain.match import match_crud,match_schema
from domain.user.user_crud import get_id_from_token, get_id_from_doubly_verified_token
from database import get_DB

router = APIRouter(
    prefix = "/KU/Match"
)

@router.post("/Duel/")
async def post_match(response : Response, request : match_schema.MatchPostRequest, request_user_id : int = Depends(get_id_from_token),db : AsyncSession = Depends(get_DB)):
    _result = await match_crud.post_match_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.post("/Accept/")
async def accept_match(response : Response, request : match_schema.MatchAcceptRequest, request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    _result = await match_crud.accept_match_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

@router.delete("/Cancel/", status_code=204)
async def cancel_match(match_id : int ,crew_id : int , request_user_id : int = Depends(get_id_from_token), db : AsyncSession = Depends(get_DB)):
    await match_crud.cancel_match_in_db(match_id ,crew_id, request_user_id, db)

@router.get("/List/")
async def get_match_list(response : Response, page_num : int, search_mode : str = "all", db : AsyncSession = Depends(get_DB)):
    _result = await match_crud.get_match_list_from_db(page_num,search_mode,db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.get("/")
async def get_match(response : Response, match_num : int,  db : AsyncSession = Depends(get_DB)):
    _result = await match_crud.get_match_from_db(match_num, db)
    response.status_code = status.HTTP_200_OK
    return _result


#request를 win, lose, draw로 한정함
@router.post("/List/", status_code=200)
async def end_match(match_num : int, request : match_schema.MatchEndRequest, db : AsyncSession = Depends(get_DB)):
    _result = await match_crud.end_match_in_db(request, match_num, db)
    return _result
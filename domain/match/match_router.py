from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from domain.match import match_crud,match_schema
from domain.user.user_crud import get_id_from_token
from database import get_DB
from models import Match

router = APIRouter(
    prefix = "/KU/Match"
)

@router.post("/Duel/")
def post_match(response : Response, request : match_schema.MatchPostRequest, request_user_id : int = Depends(get_id_from_token),db : Session = Depends(get_DB)):
    _result = match_crud.post_match_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.post("/Accept/")
def accept_match(response : Response, request : match_schema.MatchAcceptRequest, request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = match_crud.accept_match_in_db(request, request_user_id, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.get("/List/{page_num}")
def get_match_list(response : Response, page_num : int, db : Session = Depends(get_DB)):
    _result = match_crud.get_match_list_from_db(page_num, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.get("/List/{match_num}")
def get_match(response : Response, match_num : int,  db : Session = Depends(get_DB)):
    _result = match_crud.get_match_from_db(match_num, db)
    response.status_code = status.HTTP_200_OK
    return _result

@router.delete("/{match_num}")
def delete_post(match_num : int, response : Response, request_user_id : int = Depends(get_id_from_token), db : Session = Depends(get_DB)):
    _result = match_crud.delete_match_on_db(request_user_id,match_num, db)
    response.status_code = status.HTTP_202_ACCEPTED
    return _result
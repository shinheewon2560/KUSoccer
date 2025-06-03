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

@router.post("/")
def creat_crew(response : Response, request : crew_schema.CreateCrewRequest ,request_user_id : int = Depends(check_token_and_return_id), db : Session = Depends(get_DB)):
    _result = crew_crud.carving_on(request, request_user_id, db)
    response.status_code = status.HTTP_201_CREATED
    return _result
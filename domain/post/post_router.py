from fastapi import APIRouter,Depends,Response,status
from sqlalchemy.orm import Session
from domain.post import post_schema

from database import get_DB
from domain.post import post_schema, post_crud

router = APIRouter(
    prefix = "/KU/Post"
)

#개시물 리스트 출력
@router.get("/list")
def show_crew_list(response : Response, db : Session = Depends(get_DB)):
    _result = post_crud.show_post(db)
    response.status_code = status.HTTP_202_ACCEPTED
    return _result

#개시물 객체 출력
@router.get("/list/{post_num}")
def serching_id(post_num : int, response : Response, db : Session = Depends(get_DB)):
    _result = post_crud.serching_post(post_num,db)
    response.status_code = status.HTTP_200_OK
    return _result

#개시물 추가
@router.post("/")
def add_crew(request_user_id : int ,request : post_schema.PostRequest,response: Response, db : Session = Depends(get_DB)):
    _result = post_crud.post_crew(request_user_id, request, db)
    response.status_code = status.HTTP_201_CREATED
    return _result

#개시물 게시물 수정
@router.put("/")
def modify_crew(request_user_id : int, post_num : int ,request : post_schema.ModifyRequest, response : Response, db : Session = Depends(get_DB)):
    _result = post_crud.modifing_post(request_user_id, post_num,request, db)
    response.status_code = status.HTTP_202_ACCEPTED
    return _result

#개시물 삭제
@router.delete("/")
def delete_crew(request_user_id : int, post_num : int, response : Response, db : Session = Depends(get_DB)):
    _result = post_crud.delete_post(request_user_id,post_num, db)
    response.status_code = status.HTTP_202_ACCEPTED
    return _result

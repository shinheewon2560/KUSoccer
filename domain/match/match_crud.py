from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from domain.match import match_schema
from models import Match, Crew


def post_match_in_db(request : match_schema.MatchPostRequest, requset_user_id : int, db : Session):
    opponent_crew = db.query(Crew).filter(Crew.crew_name == request.opponent_crew_name).first()
    if opponent_crew is None:
        raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다.")
    data = Match(
        title = request.title,
        content = request.content,
        request_crew_id = request.request_crew_id,
        opponent_crew_id = None,
        when  = request.when,
        where = request.where
    )
    db.add(data)
    db.commit()
    return {"message":"성공적으로 등록되었습니다."}

def accept_match_in_db(request : match_schema.MatchAcceptRequest, request_user_id : int , db : Session):
    match_data = db.query(Match).filter(Match.id == request.match_id).first()
    if match_data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물이 존재하지 않습니다.")
    if match_data.opponent_crew:
        raise HTTPException(status_code = 403, detail = "이미 상대방이 결정된 경기입니다.")
    if match_data.request_crew_id == request.accept_crew_id:
        raise HTTPException(status_code = 403, detail = "같은 팀끼리 경기는 불가합니다.")
    match_data.opponent_crew_id = request.accept_crew_id
    db.commit()
    return {"message":"성공적으로 등록 되었습니다."}

def get_match_list_from_db(page_num : int, db : Session):
    number_of_post = 10
    skip = (page_num - 1) * number_of_post
    
    post_list = db.query(Match).order_by(Match.id.asc()).offset(skip).limit(number_of_post).all()
    return post_list

def get_match_from_db(match_num : int, db : Session):
    data = db.query(Match).filter(Match.id == match_num).first()
    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    if data.opponent_crew:
        _result = {
            "title" : data.title,
            "when" : data.when,
            "where" : data.where,
            "content" : data.content,
            "request_crew" : data.request_crew.crew_name,
            "opponent_crew" : data.opponent_crew.crew_name
        }
    else:
        _result = {
            "title" : data.title,
            "when" : data.when,
            "where" : data.where,
            "content" : data.content,
            "request_crew" : data.request_crew.crew_name
        }
    return _result


def delete_match_on_db(request_user_id : int, match_num : int, db : Session):
    data = db.query(Match).filter(Match.id == match_num).first()
    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    if data.request_crew.leader_id != request_user_id:
        raise HTTPException(status_code = 403, detail = "게시물은 작성자와 운영자 외에 삭제 불가능합니다.")
    
    db.delete(data)
    db.commit()
    return {"message" : "성공적으로 삭제 되었습니다."}
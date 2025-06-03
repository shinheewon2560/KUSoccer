from fastapi import HTTPException
from datetime import datetime

from sqlalchemy.orm import Session

from models import Crew,User
from domain.crew import crew_schema

def check_str_vaild(data : str) -> str:
    if data is None or data == "":
        raise HTTPException(status_code = 400, detail = "잘못된 응답입니다.")
    return data

def carving_on(request : crew_schema.CreateCrewRequest, request_user_id : int, db : Session):
    crew_name = check_str_vaild(request.crew_name)

    if db.query(Crew).filter(Crew.crew_name == crew_name).first():
        raise HTTPException(status_code = 202, detail = "이미 존재하는 팀 이름입니다.")
    reader_data = db.query(User).filter(User.id == request_user_id).first()
    if reader_data is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다.")
    if reader_data.crew:
        raise HTTPException(status_code = 202, detail = "이미 소속된 팀이 있습니다.")
    
    crew_data = Crew(
        crew_name = request.crew_name,
        greetings = request.greetings,
        reader_id = request_user_id,
        create_on = datetime.now()
    )
    db.add(crew_data)
    db.commit()
    return {"message" : "성공적으로 등록 되었습니다."}
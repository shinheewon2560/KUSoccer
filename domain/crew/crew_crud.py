from fastapi import HTTPException
from datetime import datetime

from sqlalchemy.orm import Session

from models import Crew,User
from domain.crew import crew_schema

"""
    essential function
"""

def check_str_vaild(data : str) -> str:
    if data is None or data == "":
        raise HTTPException(status_code = 400, detail = "잘못된 응답입니다.")
    return data

"""
    router function
"""

def create_crew_in_db(request : crew_schema.CreateCrewRequest, request_user_id : int, db : Session):
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

    new_column = db.query(Crew).filter(Crew.crew_name == crew_name).first()
    reader_data.crew = new_column.index
    db.commit()

    return {"message" : "성공적으로 등록 되었습니다."}

def get_info_in_db(id : int, db : Session):
    crew_data = db.query(Crew).filter(Crew.index == id).first()

    if crew_data is None:
        raise HTTPException(status_code = 404, detail = "존재하지 않는 페이지입니다.")
    
    member_str = str(crew_data.member_list)
    member_list = []
 
    for i in member_str.split(" "):
        if not i or i.lower() == "none":
            continue
        else:
            member_list.append(int(i))

    
    _return = {
        "crew_name" : f"{crew_data.crew_name}",
        "greetings" : f"{crew_data.greetings}",
        "reader_id" : f"{crew_data.reader_id}",
        "member_list" : member_list,
        "create_on" : f"{crew_data.create_on}"
    }

    return _return


def add_member_in_db(name : str, id : int, db : Session):
    crew_data = db.query(Crew).filter(Crew.reader_id == id).first()
    if crew_data is None:
        raise HTTPException(status_code = 403, detail = "팀원 추가는 리더만 가능합니다.")
    user_column = db.query(User).filter(User.user_name == name).first()
    if user_column is None:
        raise HTTPException(status_code = 404, detail = "유저가 존재하지 않습니다.")
    if user_column.crew:
        raise HTTPException(status_code = 202, detail = "이미 소속된 팀이 있습니다.")
    
    member_str = str(crew_data.member_list)
    member_list = []
 
    for i in member_str.split(" "):
        if not i or i.lower() == "none":
            continue
        else:
            member_list.append(int(i))

    for i in member_list:
        if user_column.id == i:
            raise HTTPException(status_code = 202, detail = "이미 존재하는 팀원입니다.")

    if crew_data.member_list is None:
        crew_data.member_list = f"{user_column.id} "
    else:
        crew_data.member_list += f"{user_column.id} "

    db.commit()
    return {"message" : f"{name}님을 성공적으로 등록하였습니다."}

def delete_member_in_db(name : str, id : int, db : Session):
    crew_data = db.query(Crew).filter(Crew.reader_id == id).first()
    if crew_data is None:
        raise HTTPException(status_code = 403, detail = "팀원 삭제는 리더만 가능합니다.")
    user_column = db.query(User).filter(User.user_name == name).first()
    if user_column is None:
        raise HTTPException(status_code = 404, detail = "잘못된 이름입니다.")
    
    member_str = str(crew_data.member_list)
    member_list = [int(id_str) for id_str in member_str.strip().split()]
    
    result = 0
    for i in member_list:
        if user_column.id == i:
            member_list.remove(i)
            result += 1

    if result > 0: 

        new_list = ""
        for i in member_list:
            new_list += f"{i} "

        crew_data.member_list = new_list
        user_column.crew = None
        db.commit()
        return {"message" : "성공적으로 삭제했습니다."}
    else:
        raise HTTPException(status_code = 404, detail = "해당 유저를 팀원 리스트에서 찾을 수 없습니다.")
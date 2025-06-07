#domain.crew.crew_crud.py
"""
    CRUD는 Router에서 할 작업들(함수)를 모아서 정리해둔 파일, 일종의 라이브러리화
"""

from fastapi import HTTPException
#status code 반환을 위한 lib
from datetime import datetime
#data중에 시간을 표시하기 위함
from sqlalchemy.orm import Session
#sqllite로 DB를 구현

from models import Crew,User
#DB속 table을 models 파일에 설정해 뒀으니 table참조를 위해 
from domain.crew import crew_schema
#schema를 통해 input, output을 조정하니


"""
    essential function (router에 직접 쓰이는 함수가 아님 / 반복적으로 쓰이는 흐음을 편히하기 위해, 단위 테스트를 용이하게 하기 위해 이렇게 작성)
"""

def check_str_vaild(data : str) -> str:
    if not data or data == "":
        raise HTTPException(status_code = 400, detail = "잘못된 응답입니다.")
    return data

"""
    router function
"""


def create_crew_in_db(request : crew_schema.CreateCrewRequest, request_user_id : int, db : Session):
    crew_name = check_str_vaild(request.crew_name)

    if db.query(Crew).filter(Crew.crew_name == crew_name).first():
        raise HTTPException(status_code = 202, detail = "이미 존재하는 팀 이름입니다.")
    
    crew_leader_row = db.query(User).filter(User.id == request_user_id).first()
    if crew_leader_row is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다.")
    
    new_crew_data = Crew(
        crew_name = request.crew_name,
        description = request.description,
        leader_id = request_user_id,

        create_on = datetime.now()
    )

    db.add(new_crew_data)
    #DB임시반영 부분
    db.flush()

    new_crew_data.members.append(crew_leader_row)
    db.commit()

    return {"message" : "성공적으로 등록 되었습니다."}


def get_info_in_db(id : int, db : Session):
    crew_row = db.query(Crew).filter(Crew.id == id).first()

    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "존재하지 않는 페이지입니다.")

    _return = crew_schema.CrewInformation.from_orm(crew_row)

    return _return


def add_member_in_db(user_email : str, id : int, db : Session):
    crew_row = db.query(Crew).filter(Crew.leader_id == id).first()
    if crew_row is None:
        raise HTTPException(status_code = 403, detail = "팀원 추가는 리더만 가능합니다.")
    
    user_row = db.query(User).filter(User.e_mail == user_email).first()
    if user_row is None:
        raise HTTPException(status_code = 404, detail = "유저가 존재하지 않습니다.")
    
    if user_row in crew_row.members:
        raise HTTPException(status_code=202, detail="이미 존재하는 팀원입니다.")
    
    crew_row.members.append(user_row)

    db.commit()
    return {"message" : f"{user_row.user_name}님을 성공적으로 등록하였습니다."}


def delete_member_in_db(user_email : str, id : int, db : Session):
    crew_row = db.query(Crew).filter(Crew.leader_id == id).first()
    if crew_row is None:
        raise HTTPException(status_code = 403, detail = "팀원 삭제는 리더만 가능합니다.")
    
    for user in crew_row.members:
        if user.e_mail == user_email:
            crew_row.members.remove(user)
            db.commit()
            return {"message": "성공적으로 삭제했습니다."}
        
    raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
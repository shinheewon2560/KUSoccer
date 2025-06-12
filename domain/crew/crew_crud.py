#domain.crew.crew_crud.py
"""
    CRUD는 Router에서 할 작업들(함수)를 모아서 정리해둔 파일, 일종의 라이브러리화
"""

from fastapi import HTTPException
#status code 반환을 위한 lib
from datetime import datetime
#data중에 시간을 표시하기 위함
from sqlalchemy.orm import selectinload
#sqllite로 DB를 구현
from sqlalchemy.ext.asyncio import AsyncSession

from models import Crew,User,user_crew_apply_table, Match
#DB속 table을 models 파일에 설정해 뒀으니 table참조를 위해 
from domain.crew import crew_schema
#schema를 통해 input, output을 조정하니
from sqlalchemy import select


"""
    essential function (router에 직접 쓰이는 함수가 아님 / 반복적으로 쓰이는 흐음을 편히하기 위해, 단위 테스트를 용이하게 하기 위해 이렇게 작성)
"""

def check_str_valid(data : str) -> str:
    if not data or data == "":
        raise HTTPException(status_code = 400, detail = "잘못된 응답입니다.")
    return data

"""
    router function
"""

async def create_crew_in_db(request : crew_schema.CreateCrewRequest, request_user_id : int, db : AsyncSession):
    crew_name = check_str_valid(request.crew_name)
    crew_query = select(Crew).filter(Crew.crew_name == crew_name)
    crew_result = await db.execute(crew_query)
    crew_data = crew_result.scalars().first()
    if crew_data:
        raise HTTPException(status_code = 409, detail = "이미 존재하는 팀 이름입니다.")
    
    leader_query = select(User).filter(User.id == request_user_id)
    leader_result = await db.execute(leader_query)
    leader_row = leader_result.scalars().first()

    if leader_row is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다.")
    
    new_crew_data = Crew(
        crew_name = request.crew_name,
        description = request.description,
        create_on = datetime.now()
    )
    db.add(new_crew_data)
    
    new_crew_data.leaders.append(leader_row)
    await db.commit()

    return {"message" : "성공적으로 등록 되었습니다."}


async def get_info_in_db(id : int, db : AsyncSession):
    query = select(Crew).options(selectinload(Crew.members),selectinload(Crew.opponent_match),selectinload(Crew.request_match)).filter(Crew.id == id)
    result = await db.execute(query)
    crew_row = result.scalars().first()

    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "존재하지 않는 페이지입니다.")

    _return = crew_schema.CrewInformation.from_orm(crew_row)

    return _return

async def add_member_in_db(crew_id : int, user_email : str, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "팀을 찾을 수 없습니다.")
    
    for leader in crew_row.leaders:
        if leader.id != request_user_id:
            raise HTTPException(status_code = 403, detail = "팀원 추가 권한은 리더에게만 있습니다.")
    
    user_query = select(User).filter(User.e_mail == user_email)
    user_result = await db.execute(user_query)
    user_row = user_result.scalars().first()
    if user_row is None:
        raise HTTPException(status_code = 404, detail = "유저가 존재하지 않습니다.")
    
    if user_row in crew_row.members:
        raise HTTPException(status_code = 409, detail="이미 존재하는 팀원입니다.")
    
    crew_row.members.append(user_row)

    await db.commit()
    return {"message" : f"{user_row.user_name}님을 성공적으로 등록하였습니다."}


async def delete_member_by_leader_in_db(crew_id : int, user_email : str, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "팀을 찾을 수 없습니다.")
    
    if request_user_id not in [leader.id for leader in crew_row.leaders]:
        raise HTTPException(status_code = 403, detail = "팀원 삭제는 리더만 가능합니다.")
    
    for user in crew_row.members:
        if user.e_mail == user_email:
            #왜 이런식으로 되는지 확인
            #-> 아마 list형으로 했기에 가능(?)
            crew_row.members.remove(user)
            await db.commit()
        
    raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
async def delete_member_by_self_in_db(crew_id : int, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "찾을 수 없습니다.")
    
    for user in crew_row.members:
        if user.id == request_user_id:
            crew_row.members.remove(user)
            await db.commit()
        
    raise HTTPException(status_code = 403, detail = "당신은 이 팀의 맴버가 아닙니다.")


async def delete_crew_in_db(crew_id : int, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "찾을 수 없습니다.")
    for leader in crew_row.leaders:
        if leader.id != request_user_id:
            raise HTTPException(status_code = 403, detail = "팀 삭제는 리더만 가능합니다.")
    await db.delete(crew_row)
    await db.commit()

async def apply_crew_in_db(crew_id : int, request_user_id : int , db : AsyncSession):
    crew_query = select(Crew).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "팀을 찾을 수 없습니다.")
    
    for user in crew_row.apply_user:
        if user.id == request_user_id:
            raise HTTPException(status_code= 409, detail = "이미 존재하는 팀원입니다.")
    
    user_query = select(Crew).filter(Crew.id == request_user_id)
    user_result = await db.execute(user_query)
    user_row = user_result.scalars().first()

    crew_row.apply_user.append(user_row)
    await db.commit()
    return {"message": " 성공적으로 등록되었습니다."}

async def accept_user_in_db(crew_id : int, request : crew_schema.CrewAcceptRequest, request_user_id : int , db : AsyncSession):
    crew_query = select(Crew).outerjoin(Crew.leaders).filter(Crew.id == crew_id, User.id == request_user_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "당신이 리더인 팀을 찾을 수 없습니다.")
    
    #테이블 객체에 접근할 때는 .c를 붙여서 해야함
    #다른 것들은 모두 orm객체
    apply_record = db.execute(user_crew_apply_table.select().where(user_crew_apply_table.c.crew_id == crew_id,user_crew_apply_table.c.user_id == request.user_id)).first()
    if apply_record is None:
        raise HTTPException(status_code = 404, detail = "요청을 찾을 수 없습니다.")
    
    user_query = select(User).filter(User.id == request_user_id)
    user_result = await db.execute(user_query)
    user_row = user_result.scalars().first()
    if user_row is None:
        raise HTTPException(status_code = 404, detail = "유저를 찾을 수 없습니다.")
    
    crew_row.apply_user.remove(user_row)

    if request.answer == True:
        crew_row.members.append(user_row)
        message = "성공적으로 등록되었습니다."
    else:
        message = "성공적으로 거절되었습니다."

    await db.commit()
    return {"message": message}

async def get_apply_list_in_db(crew_id : int, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).outerjoin(Crew.leaders).filter(Crew.id == crew_id, User.id == request_user_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 403, detail = "권한이 없습니다.")
    
    return crew_schema.ApplyInform.from_orm(crew_row)

async def modify_crew_profile_in_db(crew_id : int, request : crew_schema.ModifyCrewRequest, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).outerjoin(Crew.leaders).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "팀이 존재하지 않습니다.")
    
    if request_user_id not in [leader.id for leader in crew_row.leaders]:
        raise HTTPException(status_code = 403, detail = "팀 정보 수정은 팀장만 가능합니다.")
    
    crew_row.crew_name = request.crew_name
    crew_row.description = request.description
    await db.commit()
    return {"message":"성공적으로 수정되었습니다."}

async def add_leader_in_db(crew_id : int , request : crew_schema.UserEmail, request_user_id : int , db : AsyncSession):
    crew_query = select(Crew).outerjoin(Crew.leaders).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "팀을 찾울 수 없습니다.")
    
    if request_user_id not in [leader.id for leader in crew_row.leaders]:
        raise HTTPException(status_code = 403, detail = "리더만이 새로운 리더를 추가할 수 있습니다.")
    
    user_query = select(User).filter(User.e_mail == request.e_mail)
    user_result = await db.execute(user_query)
    user_row = user_result.scalars().first()
    if user_row is None:
        raise HTTPException(status_code = 404, detail = "유저를 찾을 수 없습니다.")

    if user_row.id in [member.id for member in crew_row.members]:
        crew_row.members.remove(user_row)
    if user_row.id in [leader.id for leader in crew_row.leaders]:
        raise HTTPException(status_code = 409, detail = "이미 리더로 등록된 사람입니다.")

    crew_row.leaders.append(user_row)
    await db.commit()
    return {"message":f"{user_row.user_name}님을 리더로 등록했습니다."}

async def delete_leader_in_db(crew_id : int, request_user_id : int, db : AsyncSession):
    crew_query = select(Crew).outerjoin(Crew.leaders).filter(Crew.id == crew_id)
    crew_result = await db.execute(crew_query)
    crew_row = crew_result.scalars().first()
    if crew_row is None:
        raise HTTPException(status_code = 404, detail = "팀을 찾을 수 없습니다.")
    
    if request_user_id not in [leader.id for leader in crew_row.leaders]:
        raise HTTPException(status_code = 403, detail = "리더만이 삭제할 수 있습니다.")
    
    user_query = select(User).filter(User.id == request_user_id)
    user_result = await db.execute(user_query)
    user_row = user_result.scalars().first()

    if user_row is None:
        raise HTTPException(status_code = 404, detail = "유저를 찾을 수 없습니다.")

    crew_row.leaders.remove(user_row)

    if not crew_row.leaders:
        """
        delete_query = select(Match).where((Match.request_crew_id == crew_id) | (Match.opponent_crew_id == crew_id))
        query_result = await db.execute(delete_query)
        matches_to_delete = query_result.scalars().all()
        for match in matches_to_delete:
            await db.delete(match)"""
        await db.delete(crew_row)

    await db.commit()
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.match import match_schema
from models import Match, Crew


async def post_match_in_db(request : match_schema.MatchPostRequest, request_user_id : int, db : AsyncSession):
    opponent_crew_query = select(Crew).filter(Crew.crew_name == request.opponent_crew_name)
    opponent_crew_result = await db.execute(opponent_crew_query)
    opponent_crew = opponent_crew_result.scalars().first()
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
    await db.commit()
    return {"message":"성공적으로 등록되었습니다."}

async def accept_match_in_db(request : match_schema.MatchAcceptRequest, request_user_id : int , db : AsyncSession):
    match_data_query = select(Match).filter(Match.id == request.match_id)
    match_data_result = await db.execute(match_data_query)
    match_data = match_data_result.scalars().first()
    if match_data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물이 존재하지 않습니다.")
    if match_data.opponent_crew:
        raise HTTPException(status_code = 409, detail = "이미 상대방이 결정된 경기입니다.")
    if match_data.request_crew_id == request.accept_crew_id:
        raise HTTPException(status_code = 400 , detail = "같은 팀끼리 경기는 불가합니다.")
    match_data.opponent_crew_id = request.accept_crew_id
    await db.commit()
    return {"message":"성공적으로 등록 되었습니다."}

async def get_match_list_from_db(page_num : int, db : AsyncSession):
    number_of_post = 10
    skip = (page_num - 1) * number_of_post
    
    post_list_query  = select(Match).order_by(Match.id.asc()).offset(skip).limit(number_of_post)
    post_list_result = await db.execute(post_list_query)
    post_list = post_list_result.scalars().all()
    
    return post_list

async def get_match_from_db(match_num : int, db : AsyncSession):
    data_query = select(Match).filter(Match.id == match_num)
    data_result = await db.execute(data_query)
    data = data_result.scalars().first()

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


async def delete_match_on_db(request_user_id : int, match_num : int, db : AsyncSession):
    data_query = select(Match).filter(Match.id == match_num)
    data_result = await db.execute(data_query)
    data = data_result.scalars().first()
    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    if request_user_id not in [leader.id for leader in data.request_crew.leaders]:
        raise HTTPException(status_code = 403, detail = "삭제 권한은 리더에게만 있습니다.")
    await db.delete(data)
    await db.commit()
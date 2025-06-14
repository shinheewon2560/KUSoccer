from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.match import match_schema
from models import Match, Crew, MatchResult

win_point = int(10)
draw_point = int(5)
lose_point = int(0)


"""

"""
async def post_match_in_db(request : match_schema.MatchPostRequest, request_user_id : int, db : AsyncSession):
    crew_result= await db.execute(select(Crew).filter(Crew.id == request.request_crew_id))
    crew = crew_result.scalars().first()
    if crew is None:
        raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다.")

    if request_user_id not in [leader.id for leader in crew.leaders]:
        raise HTTPException(status_code=409, detail="팀장만 경기 신청을 할 수 있습니다..")

    data = Match(
        title = request.title,
        content = request.content,
        request_crew_id = request.request_crew_id,
        opponent_crew_id = None,
        status = "wait",
        when  = request.when,
        where = request.where
    )
    db.add(data)
    await db.flush()

    result_data = MatchResult()
    data.match_result = result_data
    
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
    match_data.status = "proceed"
    await db.commit()
    return {"message":"성공적으로 등록 되었습니다."}

async def get_match_list_from_db(page_num : int, search_mode : str, db : AsyncSession):
    number_of_post = 10
    skip = (page_num - 1) * number_of_post
    
    if search_mode == "wait":
        post_list_query  = select(Match).filter(Match.status == "wait").order_by(Match.id.asc()).offset(skip).limit(number_of_post)
    elif search_mode == "complete":
        post_list_query  = select(Match).filter(Match.status == "complete").order_by(Match.id.asc()).offset(skip).limit(number_of_post)
    elif search_mode == "proceed":
        post_list_query  = select(Match).filter(Match.status == "proceed").order_by(Match.id.asc()).offset(skip).limit(number_of_post)
    else:
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

async def end_match_in_db(request: match_schema.MatchEndRequest, match_num: int, db: AsyncSession):
    data = (await db.execute(select(MatchResult, Match).join(Match, MatchResult.id == Match.match_result_id).where(Match.id == match_num))).first()

    if not data:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")

    match_result, match_data = data

    if match_data.status == "complete":
        raise HTTPException(status_code=400, detail="이미 종료된 경기입니다.")
    if request.result not in {"win", "lose", "draw"}:
        raise HTTPException(status_code=400, detail="잘못된 경기 결과입니다.")

    if request.crew_id == match_data.request_crew_id:
        match_result.request_crew_result = request.result
    elif request.crew_id == match_data.opponent_crew_id:
        match_result.opponent_crew_result = request.result
    else:
        raise HTTPException(status_code=403, detail="경기 결과는 해당 팀들만 기록할 수 있습니다.")

    r = match_result.request_crew_result
    o = match_result.opponent_crew_result
    await db.commit()

    if r and o:
        if r == o:
            if r != "draw":
                raise HTTPException(status_code=403, detail="경기 결과가 상반됩니다. 다시 확인해 주세요.")

            # 무승부 처리
            match_result.draw = True
            match_data.status = "complete"

            crews = await db.execute(select(Crew).where(Crew.id.in_([match_data.request_crew_id, match_data.opponent_crew_id])))
            crew_dict = {crew.id: crew for crew in crews.scalars()}

            crew_dict[match_data.request_crew_id].score += draw_point
            crew_dict[match_data.opponent_crew_id].score += draw_point

        elif "draw" in [r, o]:
            raise HTTPException(status_code=403, detail="경기 결과가 상반됩니다. 다시 확인해 주세요.")

        else:
            # 승패 처리
            if r == "win":
                win_id = match_data.request_crew_id 
                lose_id = match_data.opponent_crew_id
            elif o == "win":
                win_id, lose_id = match_data.opponent_crew_id, match_data.request_crew_id
            else:
                raise HTTPException(status_code=403, detail="경기 결과가 상반됩니다. 다시 확인해 주세요.")

            match_result.win_crew = win_id
            match_result.lose_crew = lose_id
            match_data.status = "complete"

            crews = await db.execute(select(Crew).where(Crew.id.in_([win_id, lose_id])))
            crew_dict = {crew.id: crew for crew in crews.scalars()}

            crew_dict[win_id].score += win_point
            crew_dict[lose_id].score += lose_point
    await db.commit()
    
    return {"message": "등록되었습니다."}

async def cancel_match_in_db(match_id :int, crew_id : int , request_user_id : int, db : AsyncSession):
    match_query_result = await db.execute(select(Match).filter(Match.id == match_id))
    match_data = match_query_result.scalars().first()
    if match_data is None:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")

    if match_data.status == "complete":
        raise HTTPException(status_code = 403, detail = "종료된 경기는 포기,삭제가 불가능합니다.")

    if match_data.opponent_crew_id == crew_id:
        if request_user_id not in [leader.id for leader in match_data.opponent_crew.leaders]:
            raise HTTPException(status_code = 403, detail = "삭제 권한은 리더에게만 있습니다.")
        match_data.opponent_crew_id = None
        match_data.opponent_crew = None
        match_data.status = "wait"
        print("dddd")
    elif match_data.request_crew_id == crew_id:
        if request_user_id not in [leader.id for leader in match_data.request_crew.leaders]:
            raise HTTPException(status_code = 403, detail = "삭제 권한은 리더에게만 있습니다.")
        match_data.match_result = None
        await db.flush() 
        await db.delete(match_data)
    else:
        raise HTTPException(status_code=404, detail="친선전에 속한 팀이 아닙니다.")
    await db.commit()
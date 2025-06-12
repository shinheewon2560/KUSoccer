from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
#쿼리 생성(명시)함수
from sqlalchemy import select
from datetime import datetime

from models import Post, DeletedPost
from domain.post import post_schema

#안전성 증진을 위한 int 데이터 검증 함수
#파라미터 설정에서 옵셔널이 아닌 데이터형을 모두 설정했으니 데이터가 없으면 알아서 걸러줌
#그래서 음수인 값만 예외처리해주면 됨
def num_is_valid(num : int):
    if num < 0:
        raise HTTPException(status_code = 400, detail = "잘못된 접근")
    return num

"""
    router function
"""

async def get_post_list_from_db(page_num : int, db : AsyncSession):
    #pagination을 구현하기 위함
    #모든 값을 불러오지 않고 표시할 page만 가져오는 것
    number_of_post = 10
    skip = (page_num - 1) * number_of_post
    
    query = select(Post).order_by(Post.id.asc()).offset(skip).limit(number_of_post)
    post_list = await db.execute(query)
    return post_list.scalars().all()

async def get_post_from_db(post_num : int, db : AsyncSession):
    post_num = num_is_valid(post_num)
    
    query = select(Post).options(selectinload(Post.post_user)).filter(Post.id == post_num)
    result = await db.execute(query)
    data = result.scalars().first()

    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    
    _result = {
        "title" : data.title,
        "content" : data.content,
        "post_user_name" : data.post_user.user_name
    }

    return _result

async def add_post_on_db(request_user_id : int, request : post_schema.PostRequest, db : AsyncSession):
    request_user_id = num_is_valid(request_user_id)

    new_post = Post(
        post_user_id = request_user_id,
        **request.dict(),
        create_on = datetime.now()
    )

    #DB에 직접적인 영향을 (혹은 비슷한 역할을 하는) 메소드만 비동기 처리 필요
    db.add(new_post)
    await db.commit()
    return {"message":"성공적으로 등록되었습니다."}

#forntend에서 수정버튼을 누르면 원래 있었던 data를 보여줌
#그리고 나서 data를 수정하는데 안 바꾸면 그냥 원래 있던 애들 그대로를 집어넣음
async def modifing_post_in_db(request_user_id : int , post_num : int, request : post_schema.ModifyRequest, db : AsyncSession):
    request_user_id = num_is_valid(request_user_id)
    post_num = num_is_valid(post_num)

    query = select(Post).filter(Post.id == post_num)
    result = await db.execute(query)
    #scalar()는 row의 첫 열만 반환
    patch_db = result.scalars().first()

    if patch_db is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    
    if patch_db.post_user_id != request_user_id:
        raise HTTPException(status_code = 403, detail = "수정권한은 작성자에게만 있습니다.")

    patch_db.content = request.content + f"\n\n{datetime.now()}수정됨"
    patch_db.title = request.title
    
    #이미 DB에 있으니 굳이 add는 안해도 된다
    await db.commit()
    return {"message":"성공적으로 수정되었습니다."}

async def delete_post_on_db(request_user_id : int, post_num : int, db : AsyncSession):
    request_user_id = num_is_valid(request_user_id)

    query = select(Post).filter(Post.id == post_num)
    result = await db.execute(query)
    data = result.scalars().first()

    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    
    if data.post_user_id != request_user_id:
        raise HTTPException(status_code = 403, detail = "게시물은 작성자와 운영자 외에 삭제 불가능합니다.")
    
    deleted_data = DeletedPost(
        title = data.title,
        content = data.content,
        post_num = data.id,
        post_user_id = data.post_user_id,
        deleted_on = datetime.now()
    )

    db.add(deleted_data)
    await db.delete(data)
    
    await db.commit()
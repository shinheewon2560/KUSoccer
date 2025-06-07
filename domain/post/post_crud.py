from fastapi import HTTPException

from sqlalchemy.orm import Session
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

def get_post_list_from_db(page_num : int, db : Session):
    #pagination을 구현하기 위함
    #모든 값을 불러오지 않고 표시할 page만 가져오는 것
    number_of_post = 10
    skip = (page_num - 1) * number_of_post
    
    post_list = db.query(Post).order_by(Post.index.asc()).offset(skip).limit(number_of_post).all()
    return post_list

def get_post_by_id_from_db(post_num : int, db : Session):
    post_num = num_is_valid(post_num)
    
    data = db.query(Post).filter(Post.index == post_num).first()

    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    
    _result = {
        "title" : data.title,
        "when" : data.when,
        "where" : data.where,
        "content" : data.content,
        "post_user_name" : data.post_user.user_name
    }

    return _result

def add_post_on_db(request_user_id : int, request : post_schema.PostRequest, db : Session):
    request_user_id = num_is_valid(request_user_id)

    new_post = Post(
        post_user_id = request_user_id,
        **request.dict(),
        create_on = datetime.now()
    )

    db.add(new_post)
    db.commit()
    return {"message":"성공적으로 등록되었습니다."}

#forntend에서 수정버튼을 누르면 원래 있었던 data를 보여줌
#그리고 나서 data를 수정하는데 안 바꾸면 그냥 원래 있던 애들 그대로를 집어넣음
def modifing_post_in_db(request_user_id : int , post_num : int, request : post_schema.ModifyRequest, db : Session):
    request_user_id = num_is_valid(request_user_id)
    post_num = num_is_valid(post_num)

    patch_db = db.query(Post).filter(Post.index == post_num).first()
    if patch_db is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    
    if patch_db.post_user_id != request_user_id:
        raise HTTPException(status_code = 401, detail = "수정권한은 작성자에게만 있습니다.")

    patch_db.content = request.content + f"\n\n{datetime.now()}수정됨"
    patch_db.title = request.title
    patch_db.when = request.when
    patch_db.where = request.where
    
    #이미 DB에 있으니 굳이 add는 안해도 된다
    db.commit()
    return {"message":"성공적으로 수정되었습니다."}

def delete_post_on_db(request_user_id : int, post_num : int, db : Session):
    request_user_id = num_is_valid(request_user_id)

    data = db.query(Post).filter(Post.index == post_num).first()

    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 게시물을 찾을 수 없습니다.")
    
    if data.post_user_id != request_user_id:
        raise HTTPException(status_code = 401, detail = "게시물은 작성자와 운영자 외에 삭제 불가능합니다.")
    
    deleted_data = DeletedPost(
        title = data.title,
        content = data.content,
        post_num = data.index,
        post_user_id = data.post_user_id,
        deleted_on = datetime.now()
    )

    db.add(deleted_data)
    db.delete(data)
    
    db.commit()
    return {"message" : "성공적으로 삭제 되었습니다."}
from fastapi import HTTPException, Header, Depends
import os

import random, string
import hashlib
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from datetime import datetime, timedelta

from models import User
from domain.user import user_schema


"""
    essential function
"""

secret_key = os.getenv("JWT_SECRET")
alg = os.getenv("ALGORITHM")
exp_dalta =timedelta(days = 1)

#유효성 검사
def check_it_valid(data : user_schema.UserInformation) -> dict:
    if "@" not in data.e_mail:
        raise HTTPException(status_code = 400, detail = "올바른 형식이 아닙니다.")
    
    data_dict = data.dict()

    data_dict["phone_num"] = data.phone_num or "None"
    data_dict["user_info"] = data.user_info or "None"

    return data_dict

def hashing(password : str) -> str:
    data = hashlib.sha256(password.encode())
    return data.hexdigest()
"""
    JWT token
"""
def create_token(payload : dict, exp_delta : timedelta):
    data = payload.copy()
    exp = datetime.utcnow() + exp_delta
    data.update({"exp" : exp})
    encoded_jwt = jwt.encode(data,secret_key,algorithm=alg)
    return encoded_jwt

def get_jwt(authorization : str = Header(...)) -> str:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다.")
    return token

def decode_token(token : str = Depends(get_jwt)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[alg])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except JWTError:
        raise HTTPException(status_code = 403, detail = "유효하지 않은 토큰입니다.")

def get_id_from_token(payload : dict = Depends(decode_token)) -> int:
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="토큰에 사용자 정보가 없습니다.")
    return int(user_id)
    
def get_id_from_doubly_verified_token(payload : dict = Depends(decode_token)):
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="토큰에 사용자 정보가 없습니다.")
    if payload.get("password_verified") != True:
        raise HTTPException(status_code = 403, detail="비밀번호 확인이 필요한 작업입니다.")
    return int(user_id)


"""
    router function
"""

def sign_up_in_db(request : user_schema.UserCreate, db : Session):
    data_dic = check_it_valid(request)

    salt  = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    if db.query(User).filter(User.e_mail == data_dic["e_mail"]).first():
        raise HTTPException(status_code = 409, detail = "이미 등록된 이메일입니다.")

    new_user = User(
        e_mail = data_dic["e_mail"],
        hash = hashing(request.password + salt),
        salt = salt,
        user_name = data_dic["user_name"],
        phone_num = data_dic["phone_num"],
        user_info = data_dic["user_info"],
        
        create_on = datetime.now()
    )

    db.add(new_user)
    db.commit()

    return {"message":"성공적으로 등록되었습니다."}

def authenticate_user(request : user_schema.LogInInput, db : Session):
    data = db.query(User).filter(User.e_mail == request.e_mail).first()

    if data is None:
        raise HTTPException(status_code = 403, detail = "사용자가 존재하지 않습니다.")
    if hashing(request.password + data.salt) != data.hash:
        raise HTTPException(status_code = 403, detail = "비밀번호가 다릅니다.")

    Payload = {
        "sub" : str(data.id),
        "user_name" : "{}".format(data.user_name),
        "password_verified" : False
    }
    token = create_token(Payload, exp_dalta)

    _result = {
        "message" : "로그인에 성공했습니다.", 
        "token" : f"{token}",
    }

    if data.joined_crews is None:
        _result["alarm"] = "crew is empty"
    
    return _result

def check_password_in_db(password : str, payload : dict, db : Session):
    data = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if data is None:
        raise HTTPException(status_code = 403, detail = "No content")
    if data.hash != hashing(password + data.salt):
        raise HTTPException(status_code = 403, detail = "비밀번호가 일치하지 않습니다.")
    payload["password_verified"] = True
    token = create_token(payload, timedelta(minutes=5))
    return {"message" : "인증이 완료되었습니다.", "token" : f"{token}"}

def modify_info_in_db(request : user_schema.UserUpdate, user_id : int, db : Session):
    data = db.query(User).filter(User.id == user_id).first()

    new_salt  = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    existing = db.query(User).filter(User.e_mail == request.e_mail).first()

    if existing and existing.id != user_id:
        raise HTTPException(status_code = 409, detail = "이미 등록된 이메일입니다.")
    
    data.e_mail = request.e_mail
    data.hash = hashing(request.password + new_salt)
    data.salt = new_salt
    data.user_name = request.user_name
    data.phone_num = request.phone_num
    data.user_info = request.user_info

    db.commit()
    return {"message" : "성공적으로 수정되었습니다."}

def get_user_profile_from_db(request_user_id : int , id : int , db : Session):
    check = db.query(User).filter(User.id == request_user_id).first()
    if check is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다")
    data = db.query(User).filter(User.id == id).first()
    if data is None:
        raise HTTPException(status_code = 404, detail = "해당 유저는 존재하지 않습니다.")

    return user_schema.GetUserInfo.from_orm(data)

def get_my_profile_from_db(request_user_id : int, db : Session):
    data = db.query(User).filter(User.id == request_user_id).first()
    if data is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다")

    return user_schema.GetUserInfo.from_orm(data)

def delete_user_in_db(request_user_id : int, db : Session):
    data = db.query(User).filter(User.id == request_user_id).first()
    if data is None:
        raise HTTPException(status_code = 404, detail = "사용자를 찾을 수 없습니다.")
    db.delete(data)
    db.commit()
    return {"message": "성공적으로 삭제되었습니다."}
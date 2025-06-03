from fastapi import HTTPException, Header, Depends
import os

import random, string, time, json
import hashlib, base64, hmac

from sqlalchemy.orm import Session

from datetime import datetime

from models import User
from domain.user import user_schema

"""
    essential function
"""

exp = 60*60*3

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

def base64url_encode(data: dict) -> str:
    json_str = json.dumps(data, separators=(',', ':'))
    b64 = base64.urlsafe_b64encode(json_str.encode()).decode()
    return b64.rstrip('=')

def base64url_decode(input_str):
    padding = '=' * (-len(input_str) % 4)  # Base64 padding 복구
    return base64.urlsafe_b64decode(input_str + padding).decode()

#sign 생성 -> 단방향 해쉬로 사용
def sign(data: str, secret: str) -> str:
    signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode().rstrip('=')

def make_JWT(payload : dict, secret : str) -> str:
    header = {"alg" : "HS256", "typ" : "JWT"}
    Header_b64 = base64url_encode(header)
    payload_b64 = base64url_encode(payload)
    sign_input = f"{Header_b64}.{payload_b64}"
    signature_b64 = sign(sign_input, secret)
    
    return f"{sign_input}.{signature_b64}"

def get_jwt(authorization : str = Header(...)) -> str:
    schema, _, token = authorization.partition(" ")
    
    return token

def check_JWT_valid(token : str) -> dict:
    data = token.split(".")

    secret = os.getenv("JWT_SECRET")
    head_b64 = data[0]
    payload_64 = data[1]
    signature = data[2]

    # 1. signature 검사
    if signature != sign(f"{head_b64}.{payload_64}", secret):
        raise HTTPException(status_code = 403, detail = "위조된 토큰입니다.")

    # 2-1. payload 복호화 및 dictionary화
    payload= base64url_decode(payload_64)
    payload_json = json.loads(payload)

    now = int(time.time())  # 현재 시간 (초)
    exp = payload_json.get("exp")

    if exp is None:
        raise Exception("exp 값이 없습니다 (유효성 검증 실패)")

    if now > exp:
        raise HTTPException(status_code = 401, detail = "인증이 만료되었습니다.")

    return payload_json

def check_token_and_return_id(token : str = Depends(get_jwt)) -> int:
    json_data = check_JWT_valid(token)

    id = json_data["id"]

    return id

"""
    router function
"""

def sign_up_in_db(request : user_schema.UserInformation, db : Session):
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

def authenticate_user(email : str , password : str, db : Session):
    data = db.query(User).filter(User.e_mail == email).first()

    if data is None:
        raise HTTPException(status_code = 403, detail = "사용자가 존재하지 않습니다.")
    if hashing(password + data.salt) != data.hash:
        raise HTTPException(status_code = 403, detail = "비밀번호가 다릅니다.")

    Payload = {
        "id" : int(data.id),
        "user_name" : "{}".format(data.user_name),
        "exp" : int(time.time()) + exp #3시간 뒤 만료됨
    }

    secret = os.getenv("JWT_SECRET")

    token = make_JWT(Payload, secret)

    _result = {
        "message" : "로그인에 성공했습니다.", 
        "token" : f"{token}",
    }

    if data.crew is None:
        _result["alarm"] = "crew is empty"
    
    return _result

    #jwt 발금 완료
    #이걸 프론트에서 받아서 로컬에 저장한 후 게시물 작성시 이 jwt를 같이 본문에 넣어서 발송하도록 작용

def modify_info_in_db(request : user_schema.UserInformation, user_id : int, db : Session):
    data = db.query(User).filter(User.id == user_id).first()

    new_salt  = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    data.e_mail = request.e_mail
    data.hash = hashing(request.password + new_salt)
    data.salt = new_salt
    data.user_name = request.user_name
    data.phone_num = request.phone_num
    data.user_info = request.user_info

    db.commit()
    return {"message" : "성공적으로 수정되었습니다."}

def print_user_profile_from_db(request_user_id : int , id : int , db : Session):
    check = db.query(User).filter(User.id == request_user_id).first()
    if check is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다")
    data = db.query(User).filter(User.id == id).first()

    if data.crew is None:
        _result = user_schema.UserProfile(
        e_mail = data.e_mail,
        user_name = data.user_name,
        user_info = data.user_info,
        phone_num = data.phone_num,
        create_on = data.create_on
        )
    else: 
        _result = user_schema.UserProfileIncludeCrew(
        e_mail = data.e_mail,
        user_name = data.user_name,
        user_info = data.user_info,
        phone_num = data.phone_num,
        crew = data.crew,
        create_on = data.create_on
        )
    return _result

def print_my_profile_from_db(request_user_id : int, db : Session):
    data = db.query(User).filter(User.id == request_user_id).first()
    if data is None:
        raise HTTPException(status_code = 403, detail = "잘못된 접근입니다")

    if data.crew is None:
        _result = user_schema.UserProfile(
        e_mail = data.e_mail,
        user_name = data.user_name,
        user_info = data.user_info,
        phone_num = data.phone_num,
        create_on = data.create_on
        )
    else: 
        _result = user_schema.UserProfileIncludeCrew(
        e_mail = data.e_mail,
        user_name = data.user_name,
        user_info = data.user_info,
        phone_num = data.phone_num,
        crew = data.crew,
        create_on = data.create_on
        )
    return _result
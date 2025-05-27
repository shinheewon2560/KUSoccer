from fastapi import HTTPException
import hashlib, random, string

from sqlalchemy.orm import Session
from sqlalchemy import Integer, String
from datetime import datetime

from models import User
from domain.user import user_schema


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

def sign_on(request : user_schema.UserInformation, db : Session):
    data_dic = check_it_valid(request)

    salt  = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    new_user = User(
        e_mail = data_dic["e_mail"],
        hash = hashing(request.password + salt),
        salt = salt,
        user_name = data_dic["user_name"],
        crew = data_dic["crew"],
        phone_num = data_dic["phone_num"],
        user_info = data_dic["user_info"],
        
        create_on = datetime.now()
    )

    db.add(new_user)
    db.commit()

    return {"message":"성공적으로 등록되었습니다."}

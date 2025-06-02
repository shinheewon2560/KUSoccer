from pydantic import BaseModel

def check_length(v:str) -> str:
    if len(v) < 2 :
            raise ValueError("제목은 한 글자 이상이여야 합니다.")
    return v 

def check_empty(v:str) -> str:
    if not v or v.strip() == "" :
        raise ValueError("내용은 비어있을 수 없습니다.")
    return v

class UserInformation(BaseModel):

    e_mail : str
    password : str
    user_name : str
    crew : str
    phone_num : str
    user_info :str

class Password(BaseModel): 
    password : str

class SignInData(BaseModel):
    e_mail : str
    password : str
    
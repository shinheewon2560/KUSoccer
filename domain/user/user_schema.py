from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

def check_length(v:str) -> str:
    if len(v) < 2 :
            raise ValueError("제목은 한 글자 이상이여야 합니다.")
    return v 

def check_empty(v:str) -> str:
    if not v or v.strip() == "" :
        raise ValueError("내용은 비어있을 수 없습니다.")
    return v


"""
    Request schema
"""
class CrewSummary(BaseModel):
    id : int
    crew_name : str

    class Config:
        from_attributes = True

class UserInformation(BaseModel):
    e_mail : str
    user_name : str
    phone_num : str
    user_info : str
    create_on : datetime
    

class UserCreate(UserInformation):
    password : str

class UserUpdate(UserInformation):
    password : str

class LogInInput(BaseModel):
    e_mail : str
    password : str

class Password(BaseModel): 
    password : str

"""
    Response schema
"""
class GetUserInfo(UserInformation):
    joined_crews : List[CrewSummary] = Field(default_factory=list) # = 뒤에 부분은 default를 설정한 것
    leading_crews : List[CrewSummary] = Field(default_factory=list)

    class Config:
        from_attributes = True
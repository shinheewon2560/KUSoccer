from pydantic import BaseModel
from datetime import datetime

class LogInData(BaseModel):
    e_mail : str
    password : str

class PostRequest(BaseModel):
    title : str
    content : str

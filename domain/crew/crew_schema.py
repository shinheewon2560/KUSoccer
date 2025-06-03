from pydantic import BaseModel

class CreateCrewRequest(BaseModel):
    crew_name : str
    greetings : str

class UserName(BaseModel):
    user_name : str
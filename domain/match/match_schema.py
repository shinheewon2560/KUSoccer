from pydantic import BaseModel, Field
from datetime import datetime

class MatchPostRequest(BaseModel):
    title : str
    content : str
    when : str
    where : str
    request_crew_id : int
    opponent_crew_name : str

class MatchAcceptRequest(BaseModel):
    match_id : int
    accept_crew_id :int
from pydantic import BaseModel

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

#win 1 , draw 0, lose -1
class MatchEndRequest(BaseModel):
    crew_id : int
    result : str
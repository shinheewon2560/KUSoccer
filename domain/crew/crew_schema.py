from pydantic import BaseModel, Field
from typing import List, Optional

"""
    Unit schema
"""

class UserSummary(BaseModel):
    id : int
    user_name : str
    e_mail : str

    class Config:
        from_attributes = True

class CrewSummary(BaseModel):
    id : int
    crew_name :str

    class Config:
        from_attributes = True    

class MatchSummary(BaseModel):
    id : int
    when : str
    where : str
    
    #단일한 객체들 (갯수 1개)를 반환하니 optional로 받음
    request_crew : Optional[CrewSummary]
    opponent_crew : Optional[CrewSummary]

    class Config:
        from_attributes = True

"""
    Request schema
"""
class CreateCrewRequest(BaseModel):
    crew_name : str
    description : str


class UserEmail(BaseModel):
    e_mail : str

    
"""
    Response schema
"""

class CrewInformation(BaseModel):
    crew_name : str
    description : str
    
    leader : UserSummary
    members : list[UserSummary] = Field(default_factory=list)

    request_match : List[MatchSummary] = Field(default_factory=list)
    opponent_match : List[MatchSummary] = Field(default_factory=list)

    class Config:
        from_attributes =True
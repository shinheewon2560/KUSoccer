from pydantic import BaseModel, Field
from typing import List


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
    Where : str

    request_match : List[CrewSummary]
    opponent_match : List[CrewSummary]

    class Config:
        from_attributes = True


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
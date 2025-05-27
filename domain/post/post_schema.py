"""
    스키마는 프로그램의 안정성을 위해서 , 또한 프로그램의 가독성을 위해서 중요하다 (가독성은 클린코드의 파라미터를 적게 하라 와 부함함)
    데이터를 받을 때 어떤 작업을 하기에 앞서서 자동으로 데이터 형과 꼴을 분석해 걸러낼 수 있다.
    swagger문서가 스키마를 기반으로 작성되니 잘 작성하면 TDD에 유리하다. -> 가독성이 좋아지니 유지보수가 편하다

"""

#예외처리 완료
from pydantic import BaseModel, field_validator

def check_length(v:str) -> str:
    if len(v) < 2 :
            raise ValueError("제목은 한 글자 이상이여야 합니다.")
    return v 

def check_empty(v:str) -> str:
    if not v or v.strip() == "" :
        raise ValueError("내용은 비어있을 수 없습니다.")
    return v

#Request의 형식이 일관적이니 클래스화 하여 처리
class FormalRequest(BaseModel):
    title : str
    content : str

    when : str
    where : str

    #프로그램의 보안을 위한 처리
    #들어오면 안되는 값을 오류로 처리하기 위함
    #class자체에서 인스턴스가 형셩될 때 각 개별 항목마다 아래 함수가 실행되도록하는 데코레이터 형성
    @field_validator("title")
    def validation_length(cls, v):
        return check_length(v)
        
    @field_validator("content")
    def validation_empty(cls, v):
        return check_empty(v)

#schema의 구조를 명시하는 것이 좋으니 이렇게 상속시켜 다르게 분해
class PostRequest(FormalRequest):
    pass

class ModifyRequest(FormalRequest):
    pass
    
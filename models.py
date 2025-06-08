from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from database import Base

user_crew_table = Table(
    "user_crew",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id",ondelete="CASCADE"),primary_key = True),
    Column("crew_id", Integer, ForeignKey("crew.id",ondelete="CASCADE"), primary_key = True)
)

#사용자 정보 담기
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True, index = True)

    e_mail = Column(String, nullable = False, index = True)
    hash = Column(String, nullable = False)
    salt = Column(String, nullable = False)

    user_name = Column(String, nullable = False)
    phone_num = Column(String)
    user_info = Column(String)

    create_on = Column(DateTime, nullable = False)
    
    #중강테이블을 이용해 crew와 연결함을 명시
    #역참조가 가능하도록 해서 특정 user row를 참조하고 있는 모든 crew row를 참조할 수 있게 만듬 (중간table로 구현)
    #back_populates는 자기를 참조하는 column이 아니라 relationship을 지정해 줘야함
    joined_crews = relationship("Crew", secondary = user_crew_table, back_populates = "members",passive_deletes=True)
    leading_crews = relationship("Crew", back_populates = "leader")

    user_post = relationship("Post", back_populates = "post_user")

#소모임 게시판 내용
class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index  = True)

    title = Column(String, nullable = False)
    when = Column(String)
    where = Column(String)
    content = Column(Text, nullable = False)

    #post -> user 연결 (단방향 연결 / N:1)
    #table에 반영되는 부분
    post_user_id = Column(Integer, ForeignKey("user.id"), nullable= False)
    #table에 반영되지는 않지만 참조르 통해 data CRUD가 가능하게 연결해주는 부분
    #foreign_keys를 설정하면 어떤 row를 CRUD할지 알려주는 화살표를 달아준 것 (여기서는 post_user_id가 화살표)
    post_user = relationship("User", foreign_keys = [post_user_id], back_populates = "user_post")

    create_on = Column(DateTime, nullable = False)


#운영자 정보 담기
class Operator(Base):
    __tablename__ = "operator"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable = False)
    description = Column(Text , nullable = False)
    contact_info = Column(String)

    create_on = Column(DateTime)

#삭제한 게시물도 운영자는 볼 수 있도록
class DeletedPost(Base):
    __tablename__ = "deleted_post"

    index = Column(Integer, primary_key=True)

    title = Column(String, nullable = False)
    content = Column(Text, nullable = False)
    post_num = Column(Integer,nullable= False)
    post_user_id = Column(Integer, nullable = False)

    deleted_on = Column(DateTime, nullable = False)

#팀 정보
class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key = True, index = True)

    crew_name = Column(String, nullable = False, index = True)
    description = Column(String)

    #crew -> user 연결 (단방향연결/ N:1)
    #여러 crew들이 하나의 user을 참조가능함 
    leader_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    leader = relationship("User", foreign_keys = [leader_id], back_populates = "leading_crews")

    #crew <-> user 연결 (쌍방향연결 / N:N)
    #중간 테이블을 이용해서 연결(새로운 테이블 생성)
    members = relationship("User", secondary = user_crew_table, back_populates = "joined_crews", passive_deletes=True)

    #crew <- match 연결 (단방향 연결 / 1:N  2개)
    #
    request_match = relationship("Match", back_populates = "request_crew", foreign_keys = lambda : [Match.request_crew_id])
    opponent_match = relationship("Match", back_populates = "opponent_crew", foreign_keys = lambda : [Match.opponent_crew_id])

    create_on = Column(DateTime)

class Match(Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key = True, index = True)

    title = Column(String, nullable = False)
    content = Column(String)
    request_crew_id = Column(Integer, ForeignKey("crew.id",ondelete="CASCADE"), nullable = False)
    opponent_crew_id = Column(Integer,ForeignKey("crew.id",ondelete="CASCADE"), nullable = True)

    when = Column(String)
    where = Column(String)

    request_crew = relationship("Crew",foreign_keys = [request_crew_id], back_populates = "request_match",passive_deletes=True)
    opponent_crew =relationship("Crew",foreign_keys = [opponent_crew_id], back_populates = "opponent_match",passive_deletes=True)

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from database import Base

user_crew_apply_table = Table(
    "user_crew_apply",
    Base.metadata,
    #이런식으로 primary key를 설정하면 저 조합이 유일해짐
    Column("user_id",Integer, ForeignKey("user.id", ondelete="CASCADE"),primary_key=True),
    Column("crew_id",Integer, ForeignKey("crew.id", ondelete="CASCADE"),primary_key=True)
)

user_crew_table = Table(
    "user_crew",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id",ondelete="CASCADE"),primary_key = True),
    Column("crew_id", Integer, ForeignKey("crew.id",ondelete="CASCADE"), primary_key = True)
)

leader_crew_table = Table(
    "leader_crew_table",
    Base.metadata,
    Column("leader_id", Integer, ForeignKey("user.id",ondelete="CASCADE"),primary_key=True),
    Column("crew_id", Integer,ForeignKey("crew.id",ondelete="CASCADE"),primary_key=True)
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
    leading_crews = relationship("Crew", secondary= leader_crew_table ,back_populates = "leaders", passive_deletes=True)
    apply_crew = relationship("Crew", secondary = user_crew_apply_table, back_populates="apply_user",passive_deletes=True )

    user_post = relationship("Post", back_populates = "post_user")

#소모임 게시판 내용
class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index  = True)

    title = Column(String, nullable = False)
    content = Column(Text, nullable = False)

    #post -> user 연결 (단방향 연결 / N:1)
    #table에 반영되는 부분
    post_user_id = Column(Integer, ForeignKey("user.id"), nullable= False)
    #table에 반영되지는 않지만 참조르 통해 data CRUD가 가능하게 연결해주는 부분
    #foreign_keys를 설정하면 어떤 row를 CRUD할지 알려주는 화살표를 달아준 것 (여기서는 post_user_id가 화살표)
    post_user = relationship("User", foreign_keys = [post_user_id], back_populates = "user_post")

    create_on = Column(DateTime, nullable = False)


#운영자 정보 담기
class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable = False)
    salt = Column(String, nullable = False)

    name = Column(String, nullable = False)
    e_mail = Column(String, nullable = False)
    contact_info = Column(String)

    create_on = Column(DateTime)

#삭제한 게시물도 운영자는 볼 수 있도록
class DeletedPost(Base):
    __tablename__ = "deleted_post"

    index = Column(Integer, primary_key=True)

    title = Column(String, nullable = False)
    content = Column(Text, nullable = False)
    post_num = Column(Integer,nullable = False)
    post_user_id = Column(Integer, nullable = False)

    deleted_on = Column(DateTime, nullable = False)

#팀 정보
class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key = True, index = True)

    crew_name = Column(String, nullable = False, index = True)
    description = Column(String, default = "잘부탁 드립니다.")
    score = Column(Integer, nullable = False, default = 0)
    #crew <-> user 연결 (단방향연결/ N:N)
    leaders = relationship("User", secondary = leader_crew_table , back_populates = "leading_crews", passive_deletes=True, lazy="selectin")

    #crew <-> user 연결 (쌍방향연결 / N:N)
    #중간 테이블을 이용해서 연결(새로운 테이블 생성)
    members = relationship("User", secondary = user_crew_table, back_populates = "joined_crews", passive_deletes=True, lazy="selectin")
    apply_user = relationship("User",secondary=user_crew_apply_table, back_populates="apply_crew", passive_deletes=True, lazy="selectin")

    #crew <- match 연결 (단방향 연결 / 1:N  2개)
    #
    request_match = relationship("Match", back_populates = "request_crew", foreign_keys = lambda : [Match.request_crew_id], cascade="all, delete-orphan")
    opponent_match = relationship("Match", back_populates = "opponent_crew", foreign_keys = lambda : [Match.opponent_crew_id], cascade="all, delete-orphan")

    create_on = Column(DateTime)

class Match(Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key = True, index = True)

    title = Column(String, nullable = False)
    content = Column(String)
    request_crew_id = Column(Integer, ForeignKey("crew.id",ondelete="CASCADE"), nullable = False)
    opponent_crew_id = Column(Integer,ForeignKey("crew.id",ondelete="CASCADE"))
    match_result_id = Column(Integer, ForeignKey("matchresult.id",ondelete="CASCADE"), nullable=False)
    status = Column(String, default= "wait")

    when = Column(String)
    where = Column(String)

    match_result = relationship("MatchResult", foreign_keys=[match_result_id], back_populates="match",passive_deletes=True)
    request_crew = relationship("Crew",foreign_keys = [request_crew_id], back_populates = "request_match",passive_deletes=True, lazy="selectin")
    opponent_crew = relationship("Crew",foreign_keys = [opponent_crew_id], back_populates = "opponent_match",lazy="selectin")

class MatchResult(Base):
    __tablename__ = "matchresult"

    id = Column(Integer, primary_key=True)
    win_crew = Column(Integer, ForeignKey("crew.id"))
    lose_crew = Column(Integer,ForeignKey("crew.id"))
    draw = Column(Boolean, default=False)
    match = relationship("Match",back_populates="match_result",passive_deletes=True, cascade="all, delete-orphan")
    request_crew_result = Column(String)
    opponent_crew_result = Column(String)
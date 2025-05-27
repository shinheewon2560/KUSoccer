from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

#사용자 정보 담기
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True, index = True)

    e_mail = Column(String, nullable = False)
    hash = Column(String, nullable = False)
    salt = Column(String, nullable = False)

    user_name = Column(String, nullable = False)
    crew = Column(String, nullable = False)
    phone_num = Column(String)
    user_info = Column(String)

    create_on = Column(DateTime, nullable = False)


#소모임 게시판 내용
class Post(Base):
    __tablename__ = "post"

    index = Column(Integer, primary_key=True, index  = True)

    title = Column(String, nullable = False)
    when = Column(String)
    where = Column(String)
    content = Column(Text, nullable = False)

    post_user_id = Column(Integer, nullable= False)

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
    post_num = Column(Integer, nullable= False)
    post_user_id = Column(Integer, nullable = False)

    deleted_on = Column(DateTime, nullable = False)
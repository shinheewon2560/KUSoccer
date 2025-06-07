# init_db.py
#데이터 베이스에 조그마한 수정이 있어도 다시 생성해야함
from database import Base, engine, SessionLocal
from models import Post,User,Operator
from datetime import datetime

# 테이블 생성
Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = User(user_name = "신희원", hash = "1e8f829e49a1974b9ae18b2c6119d34f90067f25659ffbb0268d83b085a312ca", salt = "", user_info = "제가 이 프로그램 재작자입니다,\n히힣,,,,,,저 좀 멋지죠?ㅎ", e_mail = "shinheewon@korea.ac.kr", 
     phone_num = "010-2560-1798", create_on = datetime.now())
post = Post(title = "test", content = "networking ok", when = "now", where = "anam", create_on = datetime.now(),post_user_id = 1)
operator = Operator(name = "신희원",description = "프로젝트 창시자\n프로젝트 PL",create_on = None)

db.add(user)
db.add(post)
db.add(operator)

db.commit()
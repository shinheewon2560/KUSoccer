from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

#foreignkey생성을 위함
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

#DB위치 설정
#이걸 engine에 전달해 줘야함 (DB생성, 연결을 위해서)
#앞에 데이터베이스 명시를 해줘야함 (DB랑 드라이버까지)
SQLALCHMY_DATABASE_URL = "sqlite+aiosqlite:///./KU.db"


engine = create_async_engine(
    SQLALCHMY_DATABASE_URL, 
    #single_thread로 작동하는 것을 멈추기 위해(비동기 추가를 위해서)
    connect_args={"check_same_thread":False}
)

# SQLite 외래 키 제약 조건 활성화
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):  # SQLite일 경우만 해당 작동을 하도록 드라이버로 설정
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

#비동기 새션 설정
AsyncSessionLocal = sessionmaker(
    autocommit = False, 
    autoflush = False,
    #위에서 만든 엔진을 사용한다는 의미
    bind = engine,
    #비동기 새션 클래스를 쓸거라고 명시
    class_ = AsyncSession,
    #커밋 이후 객체가 expire(무효화)되지 않도록 설정 -> 다시 질문 필요
    expire_on_commit = False,
    )

#모든 orm클래스가 상속받는 기반 클래스 생성 -> 모든 orm은 이 클래스를 기준으로 생성됨
Base = declarative_base()

#fastapi에서는 yield가 db반환까지 알아서 처리해 주도록 기능을 확장함
async def get_DB():
    async with AsyncSessionLocal() as db:
        yield db

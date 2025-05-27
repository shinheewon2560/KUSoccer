from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
import sqlite3

SQLALCHMY_DATABASE_URL = "sqlite:///./KU.db"

engine = create_engine(
    SQLALCHMY_DATABASE_URL, connect_args={"check_same_thread":False}
)

# SQLite 외래 키 제약 조건 활성화
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):  # SQLite일 경우만
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()

def get_DB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


'''
=================================================================================
database/db_connection.py

PostgreSQL DB 연결 설정 + 라우터에서 사용할 세션 의존성(get_session) 제공
=================================================================================
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# moviedb 데이터베이스가 먼저 생성되어 있어야 한다.
# 팀원마다 계정/비밀번호가 다르면 이 줄만 각자 맞게 수정하면 됨
DATABASE_URL = 'postgresql+psycopg2://postgres:1234@localhost:5432/moviedb'

engine = create_engine(DATABASE_URL, echo=True)

SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def get_session():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()

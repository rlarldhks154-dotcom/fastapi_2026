'''
=================================================================================
main.py

FastAPI 애플리케이션의 진입점
=================================================================================
'''
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.db_connection import engine
from database.orm import Base
from routers.movie import router as movie_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 1회: models.py에 정의된 테이블을 DB에 생성 (이미 있으면 아무 일도 안 함)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(movie_router)
'''
=================================================================================
schema/response.py

서버가 클라이언트에게 돌려주는 데이터의 형태를 정의
=================================================================================
'''
from pydantic import BaseModel, ConfigDict


class MovieSummaryResponse(BaseModel):
    """목록 조회용 - 가벼운 필드만"""
    model_config = ConfigDict(from_attributes=True)

    movie_cd: str
    movie_nm: str
    open_dt: str | None
    genre: str | None
    nation: str | None
    watch_grade: str | None


class MovieDetailResponse(BaseModel):
    """상세 조회용 - 감독/배우까지 포함"""
    model_config = ConfigDict(from_attributes=True)

    movie_cd: str
    movie_nm: str
    movie_nm_en: str | None
    prdt_year: int | None
    open_dt: str | None
    show_tm: int | None
    prdt_stat_nm: str | None
    type_nm: str | None
    nation: str | None
    genre: str | None
    watch_grade: str | None
    directors: list[str] = []
    actors: list[str] = []

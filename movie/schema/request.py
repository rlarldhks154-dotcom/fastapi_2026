'''
=================================================================================
schema/request.py

클라이언트가 서버로 보내는 데이터의 형태를 정의
POST(추가), PATCH(수정) 담당자가 이 파일에 필요한 필드를 이어서 채우면 됨
=================================================================================
'''
from pydantic import BaseModel, Field


class MovieCreateRequest(BaseModel):
    """POST /movies 요청 body - 담당자가 프로젝트 상황에 맞게 필드/검증 규칙 조정"""
    movie_cd: str = Field(..., description='영화 코드 (직접 부여하거나 KOBIS 코드 그대로 사용)')
    movie_nm: str = Field(..., description='영화명')
    movie_nm_en: str | None = None
    prdt_year: int | None = None
    open_dt: str | None = Field(None, description='YYYYMMDD 형식')
    show_tm: int | None = None
    prdt_stat_nm: str | None = None
    type_nm: str | None = None
    nation: str | None = None
    genre: str | None = None
    watch_grade: str | None = None
    directors: list[str] = []
    actors: list[str] = []


class MovieUpdateRequest(BaseModel):
    """
    PATCH /movies/{movie_cd} 요청 body
    전부 Optional로 둬서 "일부 필드만 수정"이 가능하게 함
    (참고 프로젝트 TodoUpdateRequest와 같은 패턴 - PUT으로 만들면 전체 필드 필수라 422 나기 쉬움)
    """
    movie_nm: str | None = None
    movie_nm_en: str | None = None
    open_dt: str | None = None
    show_tm: int | None = None
    genre: str | None = None
    watch_grade: str | None = None

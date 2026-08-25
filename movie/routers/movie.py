'''
=================================================================================
routers/movie.py

HTTP 요청/응답만 담당. 로직은 전부 MovieService에게 위임한다.
=================================================================================
'''
from fastapi import APIRouter, Depends, Query
from starlette import status
from database.db_connection import get_session
from repositories.movie_repository import MovieRepository
from services.movie_service import MovieService
from schema.request import MovieCreateRequest, MovieUpdateRequest
from schema.response import MovieSummaryResponse, MovieDetailResponse

router = APIRouter(prefix='/movies', tags=['Movie'])


def get_movie_service(session=Depends(get_session)) -> MovieService:
    return MovieService(MovieRepository(session))


# ------------------ 조회 (팀원 A 담당) ------------------
@router.get('', response_model=MovieListResponse, status_code=status.HTTP_200_OK)
def get_movies_handler(
    genre: str | None = Query(None, description='장르로 필터 (부분일치)'),
    nation: str | None = Query(None, description='제작국가로 필터 (부분일치)'),
    keyword: str | None = Query(None, description='영화명 검색 (부분일치)'),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MovieService = Depends(get_movie_service),
):
    return service.get_movies(genre, nation, keyword, limit, offset)


@router.get('/{movie_cd}', response_model=MovieDetailResponse, status_code=status.HTTP_200_OK)
def get_movie_detail_handler(
    movie_cd: str,
    service: MovieService = Depends(get_movie_service),
):
    return service.get_movie_detail(movie_cd)


# ------------------ 추가 (팀원 B 담당) ------------------
@router.post('', response_model=MovieDetailResponse, status_code=status.HTTP_201_CREATED)
def create_movie_handler(
    body: MovieCreateRequest,
    service: MovieService = Depends(get_movie_service),
):
    movie = service.create_movie(body)
    return service.get_movie_detail(movie.movie_cd)


# ------------------ 수정/삭제 (팀원 C 담당) ------------------
@router.patch('/{movie_cd}', response_model=MovieDetailResponse, status_code=status.HTTP_200_OK)
def update_movie_handler(
    movie_cd: str,
    body: MovieUpdateRequest,
    service: MovieService = Depends(get_movie_service),
):
    service.update_movie(movie_cd, body)
    return service.get_movie_detail(movie_cd)


@router.delete('/{movie_cd}', status_code=status.HTTP_204_NO_CONTENT)
def delete_movie_handler(
    movie_cd: str,
    service: MovieService = Depends(get_movie_service),
):
    service.delete_movie(movie_cd)

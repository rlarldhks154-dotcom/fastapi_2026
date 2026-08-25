'''
=================================================================================
services/movie_service.py

Movie 관련 "업무 규칙"을 담당하는 계층
DB 쿼리 자체는 하지 않고 MovieRepository에게 위임한다.
없으면 404를 낸다, 응답 형태로 변환한다 같은 판단이 여기 들어간다.
=================================================================================
'''
from fastapi import HTTPException, status
from models import Movie, Actor, Director
from repositories.movie_repository import MovieRepository
from schema.request import MovieCreateRequest, MovieUpdateRequest
from schema.response import MovieDetailResponse


class MovieService:
    def __init__(self, repository: MovieRepository):
        self.repository = repository

    # ------------------ 조회 (팀원 A 담당 영역) ------------------
    def get_movies(self, genre, nation, keyword, limit, offset):
        return self.repository.find_all(genre, nation, keyword, limit, offset)

    def get_movie_detail(self, movie_cd: str) -> MovieDetailResponse:
        movie = self.repository.find_by_id(movie_cd)
        if movie is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='영화를 찾을 수 없습니다.')

        # ORM 객체(Actor, Director)를 이름 문자열 리스트로 변환해서 응답 형태에 맞춘다
        return MovieDetailResponse(
            movie_cd=movie.movie_cd,
            movie_nm=movie.movie_nm,
            movie_nm_en=movie.movie_nm_en,
            prdt_year=movie.prdt_year,
            open_dt=movie.open_dt,
            show_tm=movie.show_tm,
            prdt_stat_nm=movie.prdt_stat_nm,
            type_nm=movie.type_nm,
            nation=movie.nation,
            genre=movie.genre,
            watch_grade=movie.watch_grade,
            directors=[d.director_name for d in movie.directors],
            actors=[a.actor_name for a in movie.actors],
        )

    # ------------------ 추가 (팀원 B 담당 영역) ------------------
    def create_movie(self, body: MovieCreateRequest) -> Movie:
        """
        담당자 TODO:
        - movie_cd 중복이면 어떤 에러를 낼지 (409 Conflict 추천)
        - directors/actors 리스트를 Director/Actor 객체로 변환해서 movie에 연결하는 로직
        """
        if self.repository.exists(body.movie_cd):
            raise HTTPException(status.HTTP_409_CONFLICT, detail='이미 존재하는 movie_cd 입니다.')

        movie = Movie(
            movie_cd=body.movie_cd,
            movie_nm=body.movie_nm,
            movie_nm_en=body.movie_nm_en,
            prdt_year=body.prdt_year,
            open_dt=body.open_dt,
            show_tm=body.show_tm,
            prdt_stat_nm=body.prdt_stat_nm,
            type_nm=body.type_nm,
            nation=body.nation,
            genre=body.genre,
            watch_grade=body.watch_grade,
        )
        movie.directors = [Director(director_name=name, movie_cd=body.movie_cd) for name in body.directors]
        movie.actors = [Actor(actor_name=name, movie_cd=body.movie_cd) for name in body.actors]

        return self.repository.save(movie)

    # ------------------ 수정/삭제 (팀원 C 담당 영역) ------------------
    def update_movie(self, movie_cd: str, body: MovieUpdateRequest) -> Movie:
        """
        담당자 TODO:
        - body에서 None이 아닌 필드만 movie 객체에 반영 (참고 프로젝트의 TodoService.update_todo 패턴)
        """
        movie = self.repository.find_by_id(movie_cd)
        if movie is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='영화를 찾을 수 없습니다.')

        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(movie, field, value)

        return self.repository.save(movie)

    def delete_movie(self, movie_cd: str) -> None:
        movie = self.repository.find_by_id(movie_cd)
        if movie is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail='영화를 찾을 수 없습니다.')
        self.repository.delete(movie)

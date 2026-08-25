'''
=================================================================================
repositories/movie_repository.py

movie(+actor, director) 테이블에 대한 DB쿼리만 담당하는 계층
HTTP 관련 개념(에러코드 등)은 모르고, 조회/저장/삭제만 책임진다.
=================================================================================
'''
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from models import Movie, Actor, Director


class MovieRepository:
    def __init__(self, session: Session):
        self.session = session

    # ------------------ 조회 (팀원 A 담당 영역) ------------------
    def find_all(
        self,
        genre: str | None = None,
        nation: str | None = None,
        keyword: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Movie]:
        """
        필터(genre, nation) + 검색(keyword: 제목 부분일치) + 페이지네이션(limit/offset)
        조회 담당자가 필요에 따라 정렬 옵션 등을 여기에 추가하면 됨
        """
        stmt = select(Movie)
        if genre:
            stmt = stmt.where(Movie.genre.ilike(f'%{genre}%'))
        if nation:
            stmt = stmt.where(Movie.nation.ilike(f'%{nation}%'))
        if keyword:
            stmt = stmt.where(Movie.movie_nm.ilike(f'%{keyword}%'))
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def find_by_id(self, movie_cd: str) -> Movie | None:
        """상세 조회 - directors/actors까지 한 번에 로드(selectinload로 N+1 문제 방지)"""
        stmt = (
            select(Movie)
            .where(Movie.movie_cd == movie_cd)
            .options(selectinload(Movie.directors), selectinload(Movie.actors))
        )
        return self.session.execute(stmt).scalars().first()

    def count_all(self, genre: str | None = None, nation: str | None = None, keyword: str | None = None) -> int:
        """페이지네이션 응답에 total 개수를 같이 줄 때 사용"""
        stmt = select(Movie)
        if genre:
            stmt = stmt.where(Movie.genre.ilike(f'%{genre}%'))
        if nation:
            stmt = stmt.where(Movie.nation.ilike(f'%{nation}%'))
        if keyword:
            stmt = stmt.where(Movie.movie_nm.ilike(f'%{keyword}%'))
        return len(list(self.session.execute(stmt).scalars().all()))

    # ------------------ 추가 (팀원 B 담당 영역) ------------------
    def save(self, movie: Movie) -> Movie:
        self.session.add(movie)
        self.session.commit()
        self.session.refresh(movie)
        return movie

    def exists(self, movie_cd: str) -> bool:
        return self.session.get(Movie, movie_cd) is not None

    # ------------------ 수정/삭제 (팀원 C 담당 영역) ------------------
    def delete(self, movie: Movie) -> None:
        self.session.delete(movie)
        self.session.commit()

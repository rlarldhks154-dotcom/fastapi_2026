'''
=================================================================================
models.py

SQLAlchemy ORM 모델 정의 파일
파이썬 클래스와 DB 테이블을 매핑(Mapping)하는 부분

- Movie: 영화 기본정보 (1)
- Actor: 영화별 배우 (N) - movie_cd로 Movie를 참조
- Director: 영화별 감독 (N) - movie_cd로 Movie를 참조

Actor/Director를 분리한 이유:
    감독/배우가 여러 명인 영화가 있어서, 문자열 하나에 다 넣으면
    "이 배우가 나온 다른 영화 찾기" 같은 조회가 불가능해진다.
    별도 테이블로 정규화하면 관계형 쿼리(JOIN)가 자연스러워진다.
=================================================================================
'''
from sqlalchemy import Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.orm import Base


class Movie(Base):
    __tablename__ = 'movie'

    movie_cd: Mapped[str] = mapped_column(String(20), primary_key=True)  # KOBIS 영화 코드
    movie_nm: Mapped[str] = mapped_column(String(200), nullable=False)
    movie_nm_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    prdt_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    open_dt: Mapped[str | None] = mapped_column(String(8), nullable=True)  # 결측 있어서 문자열로 보관(YYYYMMDD)
    show_tm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prdt_stat_nm: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 개봉/기타
    type_nm: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 장편/단편/옴니버스
    nation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(200), nullable=True)
    watch_grade: Mapped[str | None] = mapped_column(String(300), nullable=True)  # 관람등급 (등급 변경 이력이 여러 개 붙어 길어지는 경우가 있어 넉넉하게 잡음)

    actors: Mapped[list['Actor']] = relationship(
        back_populates='movie',
        cascade='all, delete-orphan',
    )
    directors: Mapped[list['Director']] = relationship(
        back_populates='movie',
        cascade='all, delete-orphan',
    )


class Actor(Base):
    __tablename__ = 'actor'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_cd: Mapped[str] = mapped_column(ForeignKey('movie.movie_cd'), nullable=False)
    actor_name: Mapped[str] = mapped_column(String(100), nullable=False)

    movie: Mapped['Movie'] = relationship(back_populates='actors')


class Director(Base):
    __tablename__ = 'director'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_cd: Mapped[str] = mapped_column(ForeignKey('movie.movie_cd'), nullable=False)
    director_name: Mapped[str] = mapped_column(String(100), nullable=False)

    movie: Mapped['Movie'] = relationship(back_populates='directors')
'''
=================================================================================
load_data.py

kobis_movie_details_2025.csv를 읽어서 movie / actor / director 테이블에 적재한다.
actors, directors 컬럼은 '|'로 구분된 여러 명이 한 셀에 들어있어서,
split해서 각각 별도 행으로 나눠 저장한다. (정규화)

실행 방법:
    1. PostgreSQL에 moviedb 데이터베이스가 미리 생성되어 있어야 함
    2. uv run python load_data.py
=================================================================================
'''
import math
import pandas as pd
from database.db_connection import engine, SessionFactory
from database.orm import Base
from models import Movie, Actor, Director

CSV_PATH = 'kobis_movie_details_2025.csv'


def clean(value):
    """NaN이면 None으로, 아니면 그대로 반환 (DB에 NaN이 그대로 들어가는 것 방지)"""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def to_open_dt_str(value):
    """openDt가 20250101.0 같은 float으로 읽히는 문제를 'YYYYMMDD' 문자열로 정리"""
    value = clean(value)
    if value is None:
        return None
    return str(int(value))


def split_names(value):
    """'김성제' 또는 '우민호|박찬욱' 형태를 리스트로 분리. 결측이면 빈 리스트."""
    value = clean(value)
    if value is None:
        return []
    return [name.strip() for name in str(value).split('|') if name.strip()]


def main():
    print('[1단계] 테이블 생성 중...')
    Base.metadata.create_all(bind=engine)

    print('[2단계] CSV 로드 중...')
    df = pd.read_csv(CSV_PATH)
    print(f'-> {len(df)}행 로드 완료')

    session = SessionFactory()
    inserted, skipped = 0, 0

    try:
        for _, row in df.iterrows():
            movie_cd = str(row['movieCd'])

            # 이미 있는 movie_cd면 건너뜀 (재실행해도 중복 안 생기게)
            existing = session.get(Movie, movie_cd)
            if existing:
                skipped += 1
                continue

            movie = Movie(
                movie_cd=movie_cd,
                movie_nm=row['movieNm'],
                movie_nm_en=clean(row.get('movieNmEn')),
                prdt_year=clean(row.get('prdtYear')),
                open_dt=to_open_dt_str(row.get('openDt')),
                show_tm=clean(row.get('showTm')),
                prdt_stat_nm=clean(row.get('prdtStatNm')),
                type_nm=clean(row.get('typeNm')),
                nation=clean(row.get('nations')),
                genre=clean(row.get('genres')),
                watch_grade=clean(row.get('audits')),
            )
            session.add(movie)

            for actor_name in split_names(row.get('actors')):
                session.add(Actor(movie_cd=movie_cd, actor_name=actor_name))

            for director_name in split_names(row.get('directors')):
                session.add(Director(movie_cd=movie_cd, director_name=director_name))

            inserted += 1

        session.commit()
        print(f'[완료] 신규 삽입 {inserted}건, 이미 있어서 건너뜀 {skipped}건')

    except Exception as e:
        session.rollback()
        print(f'[에러] 적재 중 실패, 롤백함: {e}')
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()

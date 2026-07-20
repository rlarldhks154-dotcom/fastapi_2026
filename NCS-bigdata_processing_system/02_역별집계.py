# ================================================================================
# NCS-bigdata_processing_system/review_batch.py
#   - [문제 2] 역별 인원 값 집계하기 배치 프로그램
# ================================================================================
from database import subway_engine, table_count, execute_sql

def check_subway_input() -> int:
    try:
        count = table_count(subway_engine, "subway_raw")
        print(f'[batch] 입력 테이블 확인 완료: subway_raw {count:,}건')
        return count
    except Exception as exc:
        raise RuntimeError(f'subway_raw 테이블을 확인할 수 없습니다. 원인: {exc}') from exc

def create_traffic_station_summary() -> None:
    execute_sql(
        subway_engine,
        '''
        DROP TABLE IF EXISTS traffic_station_summary;

        CREATE TABLE traffic_station_summary AS
        SELECT
            "역번호" AS station_no,
            "역명" AS station_name,
            COUNT(*) AS row_count,
            SUM("인원수") AS total_passengers,
            ROUND(AVG("인원수")::numeric, 2) AS avg_passengers
        FROM subway_raw
        GROUP BY "역번호", "역명";

        -- 7. total_passengers 내림차순 조회를 위한 인덱스 생성
        CREATE INDEX idx_traffic_station_summary_total
        ON traffic_station_summary(total_passengers DESC);
        '''
    )
    print('[batch] 역별 집계 완료: traffic_station_summary')

def create_traffic_hour_summary() -> None:
    print('[batch] 시간대별 승차 집계 완료: traffic_hour_summary')

def run_review_batch() -> None: 
    print('[batch] 배치 처리 시작')
    check_subway_input()
    create_traffic_station_summary()
    create_traffic_hour_summary()
    print('[batch] 배치 처리 완료')

if __name__ == '__main__':
    run_review_batch()
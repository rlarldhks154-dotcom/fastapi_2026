from database import subway_engine, table_count, execute_sql

def check_subway_input() -> int:
    try:
        count = table_count(subway_engine, "subway_raw")
        print(f'[batch] 입력 테이블 확인 완료: subway_raw {count:,}건')
        return count
    except Exception as exc:
        raise RuntimeError(f'subway_raw 테이블을 확인할 수 없습니다. 원인: {exc}') from exc

def create_hour_summary() -> None:
    execute_sql(
        subway_engine,
        '''
        DROP TABLE IF EXISTS traffic_hour_summary;

        CREATE TABLE traffic_hour_summary AS
        SELECT
            "시작시" AS start_hour,
            COUNT(*) AS row_count,
            COUNT(DISTINCT "역번호") AS station_count,
            SUM("인원수") AS total_ride_passengers,
            ROUND(AVG("인원수")::numeric, 2) AS avg_ride_passengers
        FROM subway_raw
        WHERE "승하차" = '승차'
        GROUP BY "시작시";

        CREATE INDEX idx_traffic_hour_summary_total
        ON traffic_hour_summary(total_ride_passengers DESC);
        '''
    )
    print('[batch] 시간대별 승차 집계 완료: traffic_hour_summary')

def main() -> None:
    print('[batch] 시간대별 배치 처리 시작')
    check_subway_input()
    create_hour_summary()
    print('[batch] 시간대별 배치 처리 완료')

if __name__ == '__main__':
    main()
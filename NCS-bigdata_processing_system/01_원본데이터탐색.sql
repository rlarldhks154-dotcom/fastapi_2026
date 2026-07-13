-- 1. subway_raw의 컬럼명과 데이터 형식 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'subway_raw'
ORDER BY ordinal_position;


-- 2. 전체 행 수
SELECT COUNT(*) AS total_rows 
FROM subway_raw;


-- 3. 지하철역의 개수 (역번호 또는 역명 기준 고유값 조회)
SELECT COUNT(DISTINCT "역번호") AS station_id_count,
       COUNT(DISTINCT "역명") AS station_name_count
FROM subway_raw;


-- 4. 승하차 구분에 저장된 값의 종류 (예: 승차, 하차 등)
SELECT DISTINCT "승하차" AS ride_types 
FROM subway_raw;


-- 5. 승하차 구분별 행 수
SELECT "승하차", COUNT(*) AS row_count 
FROM subway_raw 
GROUP BY "승하차";


-- 6. 인원 값이 가장 큰 데이터 10건 (내림차순 정렬 상위 10건)
SELECT * FROM subway_raw 
ORDER BY "인원수" DESC 
LIMIT 10;


-- 7. 날짜의 최소값과 최대값 (수집 기간 확인)
-- ※ 만약 테이블에 날짜/일자 전용 컬럼이 없을 경우, 수집 주기나 기준 시각 컬럼("시작시" 등)으로 대체 가능합니다.
SELECT MIN("시작시") AS min_time, 
       MAX("시작시") AS max_time 
FROM subway_raw;


-- 8. 인원 값이 NULL인 행의 수 (결측치 검사)
SELECT COUNT(*) AS null_passenger_count 
FROM subway_raw 
WHERE "인원수" IS NULL;
SELECT COUNT(*) FROM traffic_station_summary;

SELECT *
FROM traffic_station_summary
ORDER BY total_passengers DESC
LIMIT 10;

SELECT COUNT(*) FROM traffic_hour_summary;

SELECT *
FROM traffic_hour_summary
ORDER BY total_ride_passengers DESC
LIMIT 3;
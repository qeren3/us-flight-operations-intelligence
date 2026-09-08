SELECT 
    ap.airport,
    ap.city,
    COUNT(*) AS total_departures,
    ROUND(AVG(f.departure_delay), 2) AS avg_dep_delay
FROM flights f
INNER JOIN airports ap ON f.origin_airport = ap.iata_code
GROUP BY ap.airport, ap.city
HAVING COUNT(*) > 50000
ORDER BY avg_dep_delay DESC;


SELECT 
    f.flight_number,
    f.airline,
    f.departure_delay,
    CASE 
        WHEN f.departure_delay <= 0 THEN 'Zamanında / Erken'
        WHEN f.departure_delay BETWEEN 1 AND 15 THEN 'Küçük Rötar'
        WHEN f.departure_delay BETWEEN 16 AND 60 THEN 'Ciddi Rötar'
        WHEN f.departure_delay > 60 THEN 'Büyük Rötar'
        ELSE 'Bilinmiyor / İptal'
    END AS delay_category
FROM flights f
LIMIT 20;


SELECT 
    CASE 
        WHEN departure_delay <= 0 THEN 'Zamanında / Erken'
        WHEN departure_delay BETWEEN 1 AND 15 THEN 'Küçük Rötar'
        WHEN departure_delay BETWEEN 16 AND 60 THEN 'Ciddi Rötar'
        WHEN departure_delay > 60 THEN 'Büyük Rötar'
        ELSE 'Bilinmiyor / İptal'
    END AS delay_category,
    COUNT(*) AS flight_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flights), 2) AS percentage
FROM flights
GROUP BY delay_category
ORDER BY flight_count DESC;


SELECT 
    ROUND(SUM(airline_delay) / 60.0, 0) AS total_airline_delay_hours,
    ROUND(SUM(weather_delay) / 60.0, 0) AS total_weather_delay_hours,
    ROUND(SUM(air_system_delay) / 60.0, 0) AS total_nas_delay_hours,
    ROUND(SUM(late_aircraft_delay) / 60.0, 0) AS total_late_aircraft_hours,
    ROUND(SUM(security_delay) / 60.0, 0) AS total_security_delay_hours
FROM flights
WHERE departure_delay > 0;


SELECT 
    scheduled_departure / 100 AS departure_hour,
    COUNT(*) AS total_flights,
    ROUND(AVG(departure_delay), 2) AS avg_delay_minutes
FROM flights
WHERE scheduled_departure IS NOT NULL
GROUP BY departure_hour
ORDER BY departure_hour ASC;

SELECT 
    f.origin_airport || ' -> ' || f.destination_airport AS route,
    dep_ap.city AS origin_city,
    arr_ap.city AS dest_city,
    COUNT(*) AS total_flights,
    ROUND(AVG(f.departure_delay), 2) AS avg_dep_delay
FROM flights f
INNER JOIN airports dep_ap ON f.origin_airport = dep_ap.iata_code
INNER JOIN airports arr_ap ON f.destination_airport = arr_ap.iata_code
GROUP BY route, dep_ap.city, arr_ap.city
HAVING COUNT(*) > 5000
ORDER BY avg_dep_delay DESC
LIMIT 10;

UPDATE flights
SET origin_airport = CASE origin_airport
    WHEN '10397' THEN 'ATL'
    WHEN '13930' THEN 'ORD'
    WHEN '11298' THEN 'DFW'
    WHEN '11292' THEN 'DEN'
    WHEN '12892' THEN 'LAX'
    WHEN '14771' THEN 'SFO'
    WHEN '12266' THEN 'IAH'
    WHEN '14107' THEN 'PHX'
    WHEN '12889' THEN 'LAS'
    WHEN '13487' THEN 'MSP'
    ELSE origin_airport
END
WHERE month = 10 
  AND origin_airport IN ('10397', '13930', '11298', '11292', '12892', '14771', '12266', '14107', '12889', '13487');


  SELECT origin_airport, COUNT(*) 
FROM flights 
WHERE month = 10 
GROUP BY origin_airport 
ORDER BY count DESC 
LIMIT 10;
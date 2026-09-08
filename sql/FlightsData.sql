-- Varsa eski deneme tablolarını temizle
DROP TABLE IF EXISTS flights CASCADE;
DROP TABLE IF EXISTS airlines CASCADE;
DROP TABLE IF EXISTS airports CASCADE;

-- 1. Airlines Tablosu
CREATE TABLE airlines (
    iata_code VARCHAR(10) PRIMARY KEY,
    airline VARCHAR(150) NOT NULL
);

-- 2. Airports Tablosu
CREATE TABLE airports (
    iata_code VARCHAR(10) PRIMARY KEY,
    airport VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(10),
    country VARCHAR(50),
    latitude NUMERIC,
    longitude NUMERIC
);

-- 3. Flights Tablosu (Tüm operasyonel detaylar)
CREATE TABLE flights (
    year INT,
    month INT,
    day INT,
    day_of_week INT,
    airline VARCHAR(10),
    flight_number INT,
    tail_number VARCHAR(20),
    origin_airport VARCHAR(10),
    destination_airport VARCHAR(10),
    scheduled_departure INT,
    departure_time INT,
    departure_delay NUMERIC,
    taxi_out NUMERIC,
    wheels_off INT,
    scheduled_time NUMERIC,
    elapsed_time NUMERIC,
    air_time NUMERIC,
    distance NUMERIC,
    wheels_on INT,
    taxi_in NUMERIC,
    scheduled_arrival INT,
    arrival_time INT,
    arrival_delay NUMERIC,
    diverted INT,
    cancelled INT,
    cancellation_reason VARCHAR(10),
    air_system_delay NUMERIC,
    security_delay NUMERIC,
    airline_delay NUMERIC,
    late_aircraft_delay NUMERIC,
    weather_delay NUMERIC
);




-- 1. Airlines tablosunu doldur
COPY airlines(iata_code, airline)
FROM 'C:/airline_data/airlines.csv'
DELIMITER ','
CSV HEADER;

-- 2. Airports tablosunu doldur
COPY airports(iata_code, airport, city, state, country, latitude, longitude)
FROM 'C:/airline_data/airports.csv'
DELIMITER ','
CSV HEADER;

COPY flights (
    year, month, day, day_of_week, airline, flight_number, tail_number,
    origin_airport, destination_airport, scheduled_departure, departure_time,
    departure_delay, taxi_out, wheels_off, scheduled_time, elapsed_time,
    air_time, distance, wheels_on, taxi_in, scheduled_arrival, arrival_time,
    arrival_delay, diverted, cancelled, cancellation_reason, air_system_delay,
    security_delay, airline_delay, late_aircraft_delay, weather_delay
)
FROM 'C:/airline_data/flights.csv'
DELIMITER ','
CSV HEADER;

SELECT COUNT(*) AS total_flights FROM flights;


SELECT 
    a.airline,
    COUNT(*) AS total_flights,
    ROUND(AVG(f.departure_delay), 2) AS avg_delay_minutes
FROM flights f
INNER JOIN airlines a ON f.airline = a.iata_code
GROUP BY a.airline
ORDER BY avg_delay_minutes DESC;

SELECT 
    a.airline,
    COUNT(*) AS total_flights,
    SUM(f.cancelled) AS cancelled_flights,
    ROUND(SUM(f.cancelled) * 100.0 / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(AVG(f.departure_delay), 2) AS avg_delay_minutes
FROM flights f
INNER JOIN airlines a ON f.airline = a.iata_code
GROUP BY a.airline
ORDER BY cancellation_rate_pct DESC;

select * from flights;
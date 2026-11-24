-- Monthly route volumes and delays for before/after impact analysis.
-- Counts include all flight rows; AVG ignores NULL delay values, as in the source KPIs.
SELECT
    f.year,
    f.month,
    f.origin_airport_iata AS origin_iata,
    f.destination_airport_iata AS destination_iata,
    dep_ap.city AS origin_city,
    arr_ap.city AS destination_city,
    COUNT(*) AS total_flights,
    COUNT(f.departure_delay) AS departure_delay_observations,
    ROUND(AVG(f.departure_delay), 2) AS avg_departure_delay,
    COUNT(f.arrival_delay) AS arrival_delay_observations,
    ROUND(AVG(f.arrival_delay), 2) AS avg_arrival_delay
FROM public.flights_normalized AS f
LEFT JOIN public.airports AS dep_ap
    ON f.origin_airport_iata = dep_ap.iata_code
LEFT JOIN public.airports AS arr_ap
    ON f.destination_airport_iata = arr_ap.iata_code
GROUP BY f.year, f.month, f.origin_airport_iata, f.destination_airport_iata, dep_ap.city, arr_ap.city
ORDER BY f.year, f.month, total_flights DESC, origin_iata, destination_iata;

-- Highest-volume routes across the full dataset; volume includes all statuses.
SELECT
    f.origin_airport_iata || ' -> ' || f.destination_airport_iata AS route,
    dep_ap.city AS origin_city,
    arr_ap.city AS destination_city,
    COUNT(*) AS total_flights,
    COUNT(f.departure_delay) AS departure_delay_observations,
    ROUND(AVG(f.departure_delay), 2) AS avg_departure_delay,
    COUNT(f.arrival_delay) AS arrival_delay_observations,
    ROUND(AVG(f.arrival_delay), 2) AS avg_arrival_delay
FROM public.flights_normalized AS f
LEFT JOIN public.airports AS dep_ap
    ON f.origin_airport_iata = dep_ap.iata_code
LEFT JOIN public.airports AS arr_ap
    ON f.destination_airport_iata = arr_ap.iata_code
GROUP BY route, dep_ap.city, arr_ap.city
ORDER BY total_flights DESC
LIMIT 10;

-- Parallel of the two-endpoint route ranking in airline_queries.sql and process_of_analyst.sql.
-- Preserves the original KPI and filters: route, COUNT(*), AVG(departure_delay),
-- HAVING > 5,000, descending average delay, top 10. LEFT JOINs avoid silent loss.
SELECT
    f.origin_airport_iata || ' -> ' || f.destination_airport_iata AS route,
    dep_ap.city AS origin_city,
    arr_ap.city AS dest_city,
    COUNT(*) AS total_flights,
    ROUND(AVG(f.departure_delay), 2) AS avg_dep_delay
FROM public.flights_normalized AS f
LEFT JOIN public.airports AS dep_ap
    ON f.origin_airport_iata = dep_ap.iata_code
LEFT JOIN public.airports AS arr_ap
    ON f.destination_airport_iata = arr_ap.iata_code
GROUP BY route, dep_ap.city, arr_ap.city
HAVING COUNT(*) > 5000
ORDER BY avg_dep_delay DESC
LIMIT 10;

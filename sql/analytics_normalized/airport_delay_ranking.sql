-- Parallel of the origin airport ranking in airline_queries.sql and process_of_analyst.sql.
-- Preserves the original KPI: COUNT(*), AVG(departure_delay), HAVING > 50,000,
-- and descending average departure delay. LEFT JOIN retains unresolved groups.
SELECT
    ap.airport,
    ap.city,
    COUNT(*) AS total_departures,
    ROUND(AVG(f.departure_delay), 2) AS avg_dep_delay
FROM public.flights_normalized AS f
LEFT JOIN public.airports AS ap
    ON f.origin_airport_iata = ap.iata_code
GROUP BY ap.airport, ap.city
HAVING COUNT(*) > 50000
ORDER BY avg_dep_delay DESC;

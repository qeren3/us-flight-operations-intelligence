-- Monthly airport volumes and delay metrics for impact analysis.
-- Counts include each flight row. AVG preserves SQL's existing NULL treatment:
-- cancelled/diverted rows with NULL delay do not enter the average denominator.

-- Origin airport: departure delay
SELECT
    f.year,
    f.month,
    f.origin_airport_iata AS origin_iata,
    ap.airport,
    ap.city,
    COUNT(*) AS departure_flights,
    COUNT(f.departure_delay) AS departure_delay_observations,
    ROUND(AVG(f.departure_delay), 2) AS avg_departure_delay
FROM public.flights_normalized AS f
LEFT JOIN public.airports AS ap
    ON f.origin_airport_iata = ap.iata_code
GROUP BY f.year, f.month, f.origin_airport_iata, ap.airport, ap.city
ORDER BY f.year, f.month, f.origin_airport_iata;

-- Destination airport: arrival delay
SELECT
    f.year,
    f.month,
    f.destination_airport_iata AS destination_iata,
    ap.airport,
    ap.city,
    COUNT(*) AS arrival_flights,
    COUNT(f.arrival_delay) AS arrival_delay_observations,
    ROUND(AVG(f.arrival_delay), 2) AS avg_arrival_delay
FROM public.flights_normalized AS f
LEFT JOIN public.airports AS ap
    ON f.destination_airport_iata = ap.iata_code
GROUP BY f.year, f.month, f.destination_airport_iata, ap.airport, ap.city
ORDER BY f.year, f.month, f.destination_airport_iata;

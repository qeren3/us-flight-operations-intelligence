-- Normalized airport aliases; original columns remain untouched.
-- October 2015 DOT IDs are reconciled only through the verified crosswalk.
BEGIN;
CREATE OR REPLACE VIEW public.flights_normalized AS
SELECT f.*,
 CASE WHEN f.year=2015 AND f.month=10 AND f.origin_airport ~ '^[0-9]+$' THEN COALESCE(om.iata_code,f.origin_airport) ELSE f.origin_airport END AS origin_airport_iata,
 CASE WHEN f.year=2015 AND f.month=10 AND f.origin_airport ~ '^[0-9]+$' THEN CASE WHEN om.iata_code IS NOT NULL THEN 'mapped_from_dot_id' ELSE 'unresolved' END
      WHEN orf.iata_code IS NOT NULL THEN CASE WHEN f.year=2015 AND f.month=10 THEN 'existing_iata' ELSE 'passed_through' END ELSE 'unresolved' END AS origin_airport_mapping_status,
 CASE WHEN f.year=2015 AND f.month=10 AND f.destination_airport ~ '^[0-9]+$' THEN COALESCE(dm.iata_code,f.destination_airport) ELSE f.destination_airport END AS destination_airport_iata,
 CASE WHEN f.year=2015 AND f.month=10 AND f.destination_airport ~ '^[0-9]+$' THEN CASE WHEN dm.iata_code IS NOT NULL THEN 'mapped_from_dot_id' ELSE 'unresolved' END
      WHEN drf.iata_code IS NOT NULL THEN CASE WHEN f.year=2015 AND f.month=10 THEN 'existing_iata' ELSE 'passed_through' END ELSE 'unresolved' END AS destination_airport_mapping_status
FROM public.flights f
LEFT JOIN public.airport_id_iata_crosswalk om
 ON f.year=2015 AND f.month=10 AND om.source_dataset_month=DATE '2015-10-01'
 AND om.airport_id=CASE WHEN f.year=2015 AND f.month=10 AND f.origin_airport ~ '^[0-9]{1,5}$' THEN f.origin_airport::INTEGER ELSE NULL END
LEFT JOIN public.airport_id_iata_crosswalk dm
 ON f.year=2015 AND f.month=10 AND dm.source_dataset_month=DATE '2015-10-01'
 AND dm.airport_id=CASE WHEN f.year=2015 AND f.month=10 AND f.destination_airport ~ '^[0-9]{1,5}$' THEN f.destination_airport::INTEGER ELSE NULL END
LEFT JOIN public.airports orf ON orf.iata_code=CASE WHEN f.year=2015 AND f.month=10 AND f.origin_airport ~ '^[0-9]+$' THEN COALESCE(om.iata_code,f.origin_airport) ELSE f.origin_airport END
LEFT JOIN public.airports drf ON drf.iata_code=CASE WHEN f.year=2015 AND f.month=10 AND f.destination_airport ~ '^[0-9]+$' THEN COALESCE(dm.iata_code,f.destination_airport) ELSE f.destination_airport END;
COMMIT;

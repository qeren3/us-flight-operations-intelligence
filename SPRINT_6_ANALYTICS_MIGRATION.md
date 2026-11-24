# Sprint 6 — Analytics Migration & Impact Analysis

## Executive summary

**Verdict: PASS for the Sprint 6 investigation and SQL deliverables.** The inventory is complete, normalized parallel queries were added, and read-only comparisons against the configured PostgreSQL database verified October coverage recovery, unchanged non-October airport coverage, and unchanged airport-independent KPIs. October airport and route reporting is now complete for all 486,165 flights where the metric permits. This pass does not imply that existing dashboards or scripts have been migrated; they were expressly out of scope.

## Analytical SQL inventory

| File / query family | Existing source and joins | KPI definition / filters | October status before normalization | Action |
|---|---|---|---|---|
| `sql/airline_queries.sql`: origin airport ranking | `flights` INNER JOIN `airports` on origin code | `COUNT(*)`, `AVG(departure_delay)`, group by airport/city, `HAVING COUNT(*) > 50000`, order average delay descending | Numeric origin identifiers not matching the airport reference were dropped | Parallel normalized version created |
| `sql/airline_queries.sql`: route delay ranking | `flights` INNER JOIN airport reference on origin and destination | Route, `COUNT(*)`, `AVG(departure_delay)`, `HAVING COUNT(*) > 5000`, descending delay, top 10 | October flights with an unmatched endpoint were dropped; original raw join returned no October route rows | Parallel normalized version created |
| `sql/process_of_analyst.sql`: origin and route rankings | Same joins and definitions as above | Duplicates the two ranking query families | Same loss as above | Covered by the same parallel queries; original file, including its UPDATE statement, was not executed or changed |
| `sql/airline_queries.sql`, `sql/process_of_analyst.sql`: delay categories, cause totals, scheduled-hour analysis | Flight fields only | Existing expressions and filters; no airport reference join | Not affected by airport codes | Left unchanged |
| `sql/airline_queries.sql`: airline summaries | Flights joined to `airlines` | Airline-level count, cancellation count/rate, average departure delay | No airport dependency | Left unchanged; overall cancellation KPI independently compared below |
| `sql/create_tables.sql`, `sql/FlightsData.sql` | DDL/COPY and broad count/carrier queries | Setup and non-airport summaries | No airport-dependent analytical join in the summary queries | Not run or changed |
| `sql/validate_airport_reconciliation.sql` and Sprint 5 object scripts | Reconciliation validation / database setup | Not analytical reports | Not an analytics query family | Not modified or executed for this sprint |

There were two airport-dependent analytical query families (origin ranking and two-endpoint route ranking), duplicated across two files. No destination-only airport ranking existed. Destination arrival metrics and monthly airport/route breakdowns are included as new supplemental analyses, not represented as pre-existing KPIs.

## Normalized queries created

- `sql/analytics_normalized/airport_delay_ranking.sql`: parallel origin ranking, preserving the original count, delay average, threshold and ordering.
- `sql/analytics_normalized/route_delay_ranking.sql`: parallel top-10 route delay ranking, preserving the original count, threshold, delay average and sort order.
- `sql/analytics_normalized/monthly_airport_metrics.sql`: monthly origin volumes/departure delay and destination volumes/arrival delay.
- `sql/analytics_normalized/monthly_route_metrics.sql`: monthly route volume and delays, plus top ten routes by full-dataset volume.

The files use `public.flights_normalized` and LEFT JOIN the airport reference. Flight counts include every source row. `AVG` uses SQL's original NULL behavior, so only non-NULL delay values enter that metric's denominator; no cancelled, diverted, or missing-delay rows were filtered out.

## Before/after coverage comparison

Endpoint coverage was compared by month using the raw flight codes and airport reference versus normalized IATA codes and the same reference. Every month from January through September and November through December had 100% origin, destination, and both-endpoint reference coverage in both versions. October was the only change:

| October 2015 measure | Original raw-code airport join | Normalized airport join |
|---|---:|---:|
| Flight rows in cohort | 486,165 | 486,165 |
| Origin endpoint joined to airport reference | 180,722 | 486,165 |
| Destination endpoint joined to airport reference | 0 | 486,165 |
| Both endpoints joined | 0 | 486,165 |
| Unresolved normalized origin / destination codes | — | 0 / 0 |
| Distinct origins / destinations / routes | — | 306 / 307 / 3,916 |

Thus the old origin-only join omitted 305,443 October records, while old destination and route inner joins omitted all 486,165. The normalized view restores full endpoint and route coverage. The monthly SQL files expose airport- and route-level results for each month; the figures above summarize the full-flight coverage comparison.

## Airport and route impact

The origin ranking used identical grouping and filters before and after. The original top ten all remain eligible. All ten airports in the original top ten remain in the normalized top ten, but their ordering changes, and October-restored volumes and delay averages change for airports serving the affected cohort. For example, Newark goes from 101,772 departures at 13.64 minutes to 111,394 at 13.18 minutes; Baltimore-Washington goes from 86,079 at 13.34 to 94,101 at 12.89. Chicago O'Hare rises from third to first (313,536; 13.31), as its count and average are unchanged while other airports' October results change. These are expected mapping-coverage effects, not KPI definition changes.

For the existing route delay ranking, all original filters were retained. Eight routes are common to the two top tens; eligible route counts and ordering changed with the restored October flights. The normalized ranking includes routes such as EWR–LAX (5,029 flights) and MCO–EWR (5,202) that were absent from the old top ten. The old raw route joins had zero October coverage, while the normalized route join includes all 486,165 rows.

The new full-dataset top routes by volume are led by SFO–LAX (15,116 flights), LAX–SFO (14,799), JFK–LAX (13,113), and LAX–JFK (13,106). The monthly route query also reports departure and arrival delay averages and observation counts using non-NULL delay denominators. Its October cohort covers 3,916 distinct normalized routes.

Airport-level arrival delay and destination volumes are supplemental outputs because no corresponding destination-only query existed in the original SQL. The new monthly airport query reports per-airport counts, delay observation counts, and averages without excluding unmapped groups.

## General KPI comparison

The following aggregates were computed separately from `public.flights` and `public.flights_normalized` with identical expressions and no airport joins:

| KPI | Original | Normalized | Difference |
|---|---:|---:|---:|
| Total flights | 5,819,079 | 5,819,079 | 0 |
| Cancelled flights | 89,884 | 89,884 | 0 |
| Cancellation rate (`cancelled / all flights`) | 1.5446% | 1.5446% | 0.0000 pp |
| Diverted flights | 15,187 | 15,187 | 0 |
| Diversion rate (`diverted / all flights`) | 0.2610% | 0.2610% | 0.0000 pp |
| Departure-delay observations | 5,732,926 | 5,732,926 | 0 |
| Average departure delay | 9.370158 min | 9.370158 min | 0 |
| Arrival-delay observations | 5,714,008 | 5,714,008 | 0 |
| Average arrival delay | 4.407057 min | 4.407057 min | 0 |

## Validation, limitations, and recommendation

- All database analysis used read-only transactions. No database records, schema, or objects were changed.
- The base table and normalized view each returned 5,819,079 rows. Joins to `public.airports`, whose `iata_code` is the reference key, retained each row in the normalized origin, destination, and dual-endpoint coverage counts; no row multiplication or normalized join loss was observed.
- October returned 486,165 rows, with no unresolved normalized endpoint codes and all rows resolving at both airport references.
- Non-October endpoint coverage matched exactly between raw and normalized versions. Overall airport-independent metrics and their observation counts matched exactly.
- Existing SQL and Python/chart/dashboard files were not changed. This sprint creates parallel SQL only. Each SELECT statement in the four new SQL files was executed successfully in a read-only transaction; the monthly airport statements returned 3,722 origin groups and 3,724 destination groups, the monthly route statement returned 48,797 groups, and the ranking/top-route statements returned 32, 10, and 10 rows.
- Sprint 5 context notes that ten October origin codes had already been converted in the base table and their original numeric strings are not retained there. This sprint compares the current raw base values with the normalized view and cannot reconstruct those lost source strings. The normalized view reports these as already-existing IATA values; this does not affect row counts or the verified October endpoint coverage.

**Recommended next step:** review the changed airport and route rankings with the analytics owner, then migrate dashboard or Python consumers in a separate authorized sprint if desired. Keep the original SQL intact as the pre-normalization baseline until that review is complete.

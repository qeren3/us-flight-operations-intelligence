# Sprint 5 — Airport Code Reconciliation Implementation

**Status:** PASS  
**Scope:** Implemented the verified 2015-10 DOT Airport ID crosswalk and a normalized view. No existing flight values, reference rows, project SQL/Python scripts, charts, KPIs, or dashboard files were changed.

## Summary

Loaded 307 verified crosswalk rows into `public.airport_id_iata_crosswalk` and created `public.flights_normalized`. The view preserves all 31 original flight columns and adds normalized origin/destination IATA codes plus a mapping status for each endpoint. It uses `LEFT JOIN`s and only applies the DOT ID crosswalk to October 2015.

The full validation SQL returned **20 PASS / 0 FAIL**. It verified all 5,819,079 base rows are represented exactly once in the view, all 486,165 October rows remain, both October endpoint references have 100% coverage, and an inner join on both normalized airport codes retains all October rows.

## Files created

- `data/reference/airport_id_iata_crosswalk_2015_10.csv` — 307 official ID, sequence ID, and IATA mappings plus source metadata.
- `sql/create_airport_id_crosswalk.sql` — transactional, repeatable crosswalk table creation and load. It compares existing values and raises an exception on conflicts; it does not silently replace them.
- `sql/create_flights_normalized_view.sql` — creates/replaces the normalized view without changing base flight rows.
- `sql/validate_airport_reconciliation.sql` — read-only checks, including `EXCEPT ALL` comparisons for exact base/view row preservation.
- `SPRINT_5_RECONCILIATION_IMPLEMENTATION.md` — this implementation report.

## Database objects

### `public.airport_id_iata_crosswalk`

Contains 307 rows scoped to `source_dataset_month = 2015-10-01`. The primary key is `(source_dataset_month, airport_id)`; the month/sequence pair is also unique, and `iata_code` references `public.airports(iata_code)`. Each row stores the source identifier system, official archive and CSV member names, URL, SHA-256, and download date.

The loader is safe to rerun: identical existing rows are retained; a different value for an existing key or sequence raises an exception and rolls back the transaction. The loader was run twice successfully; the count remained 307.

### `public.flights_normalized`

The view selects `f.*` and adds:

- `origin_airport_iata`
- `origin_airport_mapping_status`
- `destination_airport_iata`
- `destination_airport_mapping_status`

For October 2015, numeric values are looked up through the October crosswalk. Existing alphabetic airport codes are passed through when present in `airports`; unmatched values are retained and marked `unresolved`. Other months and years are passed through without using the October crosswalk; invalid reference values are marked `unresolved` but not filtered out. Both mapping joins and airport-reference joins are `LEFT JOIN`s.

The status values used are `mapped_from_dot_id`, `existing_iata`, `passed_through`, and `unresolved`.

**Preserved historical limitation:** ten origin values were already converted to IATA codes before Sprint 5. Their original numeric strings are absent from the current `flights.origin_airport` column. The view preserves those current values and marks them `existing_iata`; it does not claim to reconstruct the lost raw strings. The verified crosswalk still contains their DOT IDs and codes and is used for numeric destination IDs and remaining numeric origins.

## Before and after airport-join coverage

| October 2015 measure | Before | After |
|---|---:|---:|
| Base flight rows | 486,165 | 486,165 |
| Origin rows matching `airports` | 180,722 (37.17%) | 486,165 (100%) |
| Destination rows matching `airports` | 0 (0%) | 486,165 (100%) |
| Rows retained by inner joins to both airport endpoints | 0 (0%) | 486,165 (100%) |
| Numeric airport endpoints left unresolved | 791,608 endpoint values | 0 |

After normalization, October origin statuses are 305,443 `mapped_from_dot_id` and 180,722 `existing_iata`; all 486,165 destinations are `mapped_from_dot_id`. DOT Airport ID 10666 occurs once as a destination and maps to BLI.

## Validation results

The validation script was executed in a read-only transaction after creating the table and view. All 20 checks passed:

| Check | Actual result |
|---|---:|
| Crosswalk rows | 307 |
| Crosswalk CSV compared row-for-row with database table (including source metadata) | 307 / 307 exact match |
| Duplicate crosswalk keys | 0 |
| Null crosswalk fields | 0 |
| Conflicting ID/code or sequence groups | 0 |
| Codes missing from airport reference | 0 |
| Base flight rows | 5,819,079 |
| Base October rows | 486,165 |
| Normalized view rows | 5,819,079 |
| Base rows missing from view (`EXCEPT ALL`) | 0 |
| Extra/multiplied view rows (`EXCEPT ALL`) | 0 |
| October origin coverage | 486,165 / 486,165 (100%) |
| October destination coverage | 486,165 / 486,165 (100%) |
| October rows retained by both endpoint inner joins | 486,165 |
| Unresolved numeric October endpoints | 0 |
| Destination ID 10666 → BLI | 1 / 1 |
| Non-October airport values changed | 0 |
| Existing alphabetic October values changed | 0 |
| Crosswalk rows outside October | 0 |
| DOT-ID mapping status outside October | 0 |

The exact-row comparison uses `EXCEPT ALL` across every base flight column in both directions, so it also checks duplicate multiplicity and detects either dropped or added/multiplied rows.

## How to query

```sql
SELECT
    year, month, origin_airport, origin_airport_iata,
    origin_airport_mapping_status,
    destination_airport, destination_airport_iata,
    destination_airport_mapping_status
FROM public.flights_normalized
WHERE year = 2015 AND month = 10
LIMIT 20;
```

For airport analysis, join using the normalized fields:

```sql
SELECT a.airport, COUNT(*) AS departures
FROM public.flights_normalized f
JOIN public.airports a ON a.iata_code = f.origin_airport_iata
WHERE f.year = 2015 AND f.month = 10
GROUP BY a.airport
ORDER BY departures DESC;
```

## Known limitations

- The crosswalk is valid for the verified October 2015 BTS snapshot only. It must not be reused for other periods or identifier systems without source validation.
- Raw numeric origin values for the ten previously converted IDs were not preserved in the existing base column. No attempt was made to reconstruct or overwrite them.
- The view exposes unresolved codes rather than dropping rows. Future source months with unfamiliar identifiers will need their own verified crosswalk before airport joins can be expected to reach full coverage.
- Validation confirms the created view and table in the connected local database. Rebuilding a database from the original import scripts may recreate the base tables; apply the new crosswalk loader and view scripts afterward.

## Final verdict

**Sprint 5: PASS.** All 307 verified mappings were loaded, the crosswalk and view validations passed, all 5,819,079 flight rows are preserved, and all 486,165 October flights have both airport endpoints resolved. No existing flight records or project scripts were changed.

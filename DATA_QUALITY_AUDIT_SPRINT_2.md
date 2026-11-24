# Sprint 2 — Flight Data Quality Audit

**Audit date:** 2026-11-20  
**Scope:** Read-only review of the project files and PostgreSQL `public` schema. No database records, schema objects, SQL files, Python files, datasets, KPIs, or charts were modified.

## 1. Executive summary

The database is reachable and contains 5,819,079 flight rows spanning every day and month of 2015, plus 14 airline reference rows and 322 airport reference rows. Deterministic checks found complete flight identity/schedule fields, valid date/day/time encodings, binary status flags, nonnegative distance and duration values, no exact duplicate flight rows, and no unmapped airline codes.

The main material issue is concentrated in October: every one of its 486,165 flight rows has an airport destination code that does not match `airports.iata_code`; 305,443 October origin codes also fail the airport lookup. The project’s airport/route inner joins consequently drop all October rows for two-endpoint analyses and 305,443 rows in origin-only joins. The database does contain an existing analyst SQL update for a subset of October origin codes, but it does not repair the destination codes and was not executed during this audit.

A proposed composite score is **97.62/100**, using measured global metrics and the explicitly stated weights below. This high global score hides the concentrated October failure, so it is not a release-readiness signal. **Overall status: mixed; suitable for airline/delay analyses with caveats, but not currently reliable for airport/route analyses that require the airport reference table.**

## 2. Dataset and database overview

### Observed database tables

| Table | Rows | Structure and constraints |
|---|---:|---|
| `flights` | 5,819,079 | 31 columns for date, carrier, flight, airports, scheduled/actual times, delays, duration, distance, cancellation/diversion and delay causes. No primary key or foreign keys; columns are nullable in the declared table definition. |
| `airlines` | 14 | `iata_code` primary key and non-null; airline name non-null. |
| `airports` | 322 | `iata_code` primary key and non-null; airport name non-null; city/state/country and coordinates. |

The observed flight dates run from 2015-01-01 through 2015-12-31, cover all 365 calendar dates and all 12 months, and have no invalid calendar dates or day-of-week mismatches. The dataset’s flight table is therefore the primary analytical dataset; `airlines` and `airports` are local lookup tables.

The SQL files describe PostgreSQL `COPY` imports from `C:/airline_data/{airlines,airports,flights}.csv`. Those CSVs are not present in the workspace, so their contents, provenance, and repeatability could not be independently checked. `create_tables.sql`, `FlightsData.sql`, and `airline_queries.sql` contain overlapping table/load setup; `process_of_analyst.sql` includes an `UPDATE`. None of these scripts was executed. The audit used `SELECT` aggregates in a read-only transaction only.

### Current analytical scripts reviewed

- `airline_delays_chart.py`: average departure delay by airline, joined to `airlines`.
- `root_cause_chart.py`: delay-cause sums, filtered by positive departure delay.
- `hourly_delay_chart.py`: average departure delay by scheduled departure hour.
- `airport_heatmap.py`: monthly average departure delay for a fixed set of ten origin airports.
- `tempCodeRunnerFile.py`: duplicate of the hourly-delay chart logic.

## 3. Data quality findings

Percentages below use 5,819,079 flight rows unless the table or denominator is stated. An affected record can appear in more than one finding.

| Issue | Affected column/table | Affected records | % of records | Severity | Analytical impact | Recommended remediation |
|---|---|---:|---:|---|---|---|
| October airport codes fail the local airport lookup | `flights.origin_airport` / `airports.iata_code` | 305,443 flight rows | 5.25% | **High** | Origin-only airport joins omit these rows. October has a mixture of IATA-like and numeric codes. | Verify source code system and apply a complete, authoritative FAA/IATA crosswalk or reload from a consistent source. Reconcile every code before analysis. |
| Every October destination code fails the airport lookup | `flights.destination_airport` / `airports.iata_code` | 486,165 flight rows | 8.35% | **Critical** | All October rows disappear from analyses joining both origin and destination to `airports`, including route analyses. This is a whole-month cohort gap. | Resolve destination mapping at source; validate both endpoints for all rows and months before relying on airport/route outputs. |
| One candidate flight-key collision | Proposed key: date, airline, flight number, origin, scheduled departure | 2 rows in 1 group (1 excess row) | <0.01% | **Low** | The proposed key is not unique. The pair is both marked cancelled and has different destinations (CLT/SJU); no actual departure times are recorded. It may be a conflicting duplicate or two legitimate scheduled records. | Review against source records; do not deduplicate automatically. Define and enforce a natural/surrogate key only after source semantics are confirmed. |
| Cancellation flag with actual operational fields | `flights.cancelled`, actual time fields | 3,731 cancelled rows have `departure_time`; 837 have `wheels_off` | 0.064% / 0.014% | **Medium** | These are potential status/operations conflicts. Cancellation can occur after pushback, so the values alone do not prove an error. | Confirm cancellation and wheels-off semantics with the source documentation; classify post-pushback cancellations explicitly if supported. |
| Root-cause filter excludes cause-bearing records | `root_cause_chart.py` query and five delay-cause columns | 112,566 rows with at least one cause value have nonpositive or missing `departure_delay` | 1.93% | **Medium** | The `departure_delay > 0` predicate excludes these records and 2,996,639 recorded cause minutes (4.78% of all cause-component minutes). Cause shares therefore depend on this filter choice. | Confirm whether the intended population is departure-delayed flights or all flights with cause attribution; document the denominator before changing the KPI. |
| Missing tail numbers | `flights.tail_number` | 14,721 | 0.253% | **Low** | Limits aircraft-level grouping; does not directly change current chart aggregations. | Determine whether absent tail numbers are expected in source data, especially for cancellations, before imputing or excluding. |
| Missing airport coordinates | `airports.latitude`, `airports.longitude` | 3 airport rows | 0.93% of airport rows | **Low** | Affects maps or geographic calculations for those airports; no current chart uses coordinates. | Resolve from an authoritative airport reference if geographic analysis is planned. |

There were **zero exact duplicate rows** across all 31 `flights` columns. The one candidate-key group is not an exact duplicate. Airlines and airports use primary-key constraints; the flight table has no declared primary or foreign keys.

## 4. Missing values

For text fields, the audit checked empty/whitespace-only strings and common placeholders (`NA`, `N/A`, `NULL`, `NONE`, `UNKNOWN`, `?`, `-`); none were found. The counts below list all columns with at least one NULL. Unlisted columns had zero NULLs.

### `flights` (5,819,079 rows)

| Column(s) | NULL rows | NULL % | Interpretation |
|---|---:|---:|---|
| `tail_number` | 14,721 | 0.253% | Not explained by flight status in this audit; review if aircraft analysis is needed. |
| `departure_time`, `departure_delay` | 86,153 each | 1.481% | Exactly the cancelled rows without an actual departure time; the remaining cancelled rows have departure-time/delay values. |
| `taxi_out`, `wheels_off` | 89,047 each | 1.530% | Consistent with cancelled rows without a wheels-off event. |
| `wheels_on`, `taxi_in`, `arrival_time` | 92,513 each | 1.590% | Equals 89,884 cancelled rows plus 2,629 diverted rows without these arrival-side fields. |
| `scheduled_time` | 6 | 0.0001% | Small isolated gap; assess if scheduled duration is used. |
| `elapsed_time`, `air_time`, `arrival_delay` | 105,071 each | 1.806% | Exactly the 89,884 cancelled plus 15,187 diverted rows; expected for these outcomes. |
| `cancellation_reason` | 5,729,195 | 98.455% | Expected: all 89,884 cancelled rows have a reason; noncancelled rows do not. Observed reason codes are A/B/C/D. |
| Each of `air_system_delay`, `security_delay`, `airline_delay`, `late_aircraft_delay`, `weather_delay` | 4,755,640 each | 81.725% | Cause components are sparse and not general-purpose flight fields. All 1,063,439 rows with at least one cause component had an attribution value; NULLs should not be treated as zero without an explicit KPI rule. |

The cancellation and diversion counts were 89,884 (1.545%) and 15,187 (0.261%), respectively. Actual departure-side fields were populated for every noncancelled flight. Arrival-side fields were absent for cancelled and diverted flights as indicated above. This pattern supports treating much of the missingness as outcome-dependent and expected, rather than blanket data loss.

### Reference tables

- `airlines`: no NULLs in either column.
- `airports`: 3 NULL latitude values and 3 NULL longitude values; the same number of rows is missing one or both coordinates. No non-NULL latitude/longitude was outside geographic bounds.

## 5. Validity and logical consistency

Executed checks found zero rows with:

- Invalid year/month/day parts or a weekday that disagrees with the calendar date.
- Invalid HHMM encodings in scheduled/actual departure, arrival, wheels-off, or wheels-on fields (audit accepted `2400` as a valid midnight encoding).
- Nonbinary `cancelled` or `diverted` values.
- Negative distance, scheduled/elapsed/air/taxi duration, or delay-cause component values.
- Identical non-NULL origin and destination codes.
- A cancellation reason on a noncancelled flight, or a cancelled flight without a reason.
- A row marked both cancelled and diverted.

For 5,714,008 noncancelled, nondiverted flights with all component fields, `elapsed_time = air_time + taxi_out + taxi_in` exactly; there were no mismatches. The 3,731 cancellations with actual departure fields and 837 with `wheels_off` remain a review item because their business meaning cannot be established from schema and values alone.

## 6. Referential integrity and categorical validation

All 14 distinct airline codes in `flights` match `airlines.iata_code`; no airline reference misses were found. The airport codes are consistent with the reference table outside October. In October alone:

- 305,443 origin values fail the airport lookup (62.83% of October rows).
- All 486,165 destination values fail the airport lookup (100% of October rows).
- The `airports` table stores alphabetic IATA-like codes; the October flight values include numeric codes. The two endpoint columns have 791,608 unmatched references combined (6.80% of all 11,638,158 endpoint references).
- An origin-only airport join retains 180,722 October rows and omits 305,443. A join requiring both airport endpoints retains zero October rows.

Status values are consistently binary; cancellation reasons are A/B/C/D only. No external code list was supplied, so their official labels were not independently validated. The October code pattern is strongly suspicious but the exact mapping must come from an authoritative source, not an assumed conversion.

## 7. Duplicate and natural-key analysis

The flight table has no declared key. A whole-row comparison across all 31 columns found zero excess duplicate rows. A plausible candidate key—`year, month, day, airline, flight_number, origin_airport, scheduled_departure`—found one two-row group. Those two rows share date/carrier/flight/origin/scheduled time, are both cancelled, but have different destinations. This establishes that the proposed key is not unique; it does **not** establish that either row is erroneous. The source does not provide a stable flight-record identifier, so a reliable natural key remains unconfirmed.

Airline and airport reference tables have primary keys on `iata_code`, so duplicate codes cannot be present under the observed constraints.

## 8. Numeric distributions and anomalies

Values are in the source’s apparent minutes/miles conventions; the project does not include a separate data dictionary. Extreme values are observations to review, not automatically errors.

| Field | Non-NULL n | Min | Median | P95 | P99 | Max | Mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| `distance` | 5,819,079 | 21 | 647 | 2,227 | 2,588 | 4,983 | 822.36 |
| `departure_delay` | 5,732,926 | -82 | -2 | 67 | 168 | 1,988 | 9.37 |
| `arrival_delay` | 5,714,008 | -87 | -5 | 66 | 167 | 1,971 | 4.41 |
| `scheduled_time` | 5,819,073 | 18 | 123 | 308 | 377 | 718 | 141.69 |
| `elapsed_time` | 5,714,008 | 14 | 118 | 299 | 367 | 766 | 137.01 |
| `air_time` | 5,714,008 | 7 | 94 | 273 | 337 | 690 | 113.51 |
| `taxi_out` | 5,730,032 | 1 | 14 | 31 | 50 | 225 | 16.07 |
| `taxi_in` | 5,726,566 | 1 | 6 | 16 | 30 | 248 | 7.43 |

Delay distributions are right-skewed, with operationally plausible early flights (negative delay) and rare long delays. The 1,988-minute departure delay, 1,971-minute arrival delay, and high taxi-time maxima merit source-level review if tail behavior drives decisions; no rule in the available project material proves them invalid. Distance ranges are nonnegative and plausible for domestic operations.

## 9. Impact on existing analyses

- **Airline delay chart and cancellation-rate query:** all airline references resolve. Departure-delay averages omit NULL values by SQL `AVG`; cancelled rows without departure delays are excluded implicitly. The cancellation flag has no NULL/invalid values, so its row denominator is complete. The 3,731 cancelled records with departure delays should be understood when interpreting the averages.
- **Airport/route SQL:** inner joins to `airports` drop 305,443 origin-mismatched October rows in origin-only summaries and all 486,165 October rows in two-endpoint route summaries. Airport rankings and route comparisons can therefore be biased by a complete missing month.
- **Airport heatmap:** its fixed IATA-code origin filter returns 180,722 October rows (179,953 with departure delay); numeric October origin codes are not represented in that filter. The October airport slice is consequently incomplete.
- **Root-cause chart:** the query sums cause components only where `departure_delay > 0`. There are 1,063,439 rows with at least one recorded cause component; 112,566 of those fail that filter. The filtered query sums 59,655,228 cause minutes versus 62,651,867 across all rows with recorded causes. This is a 4.78% difference in cause minutes and 10.59% of cause-bearing rows. The intended population and denominator should be made explicit before interpreting the chart as a complete cause distribution.
- **Hourly delay chart:** scheduled departure is present and valid for all rows; all 12 months and 365 dates are represented. Delay averages still depend on NULL handling described above.

## 10. Proposed Data Quality Score

This is a proposed, uncalibrated summary, not an established project KPI. It avoids penalizing status-dependent NULLs by scoring only required flight identity/schedule fields and deterministic checks.

| Dimension | Weight | Measured result | Weighted points | Definition |
|---|---:|---:|---:|---|
| Core-field completeness | 20% | 100.00% | 20.00 | Required date, airline, flight number, origin, destination, scheduled departure, distance and status fields are non-NULL. |
| Deterministic validity | 25% | 100.00% | 25.00 | Date/day, HHMM, flag, nonnegative distance/durations/cause components, and nonidentical endpoints checks above. Ambiguous cancellation/operation combinations are excluded pending semantics. |
| Exact-row uniqueness | 20% | 100.00% | 20.00 | No exact duplicate rows across all available flight columns. Candidate-key ambiguity is reported separately because it is not proven erroneous. |
| Reference integrity | 35% | 93.20% | 32.62 | Valid airport endpoint references: 10,846,550 of 11,638,158 origin/destination references. Airline mapping is separately 100%. |
| **Composite** | **100%** |  | **97.62 / 100** | Weighted sum of measured dimensions. |

The 97.62 score is global and dilutes a concentrated, severe October issue. It must be read alongside the finding table and not used alone to approve airport or route reporting. Weights are proposed: reference integrity receives the largest weight because current analyses join through airport keys; completeness and validity protect core metrics; uniqueness guards against row inflation.

## 11. Prioritized remediation roadmap

1. **Resolve October airport identifiers first.** Obtain the source’s code definitions/crosswalk, map both origin and destination consistently, and reconcile row-level counts without dropping unmapped records.
2. **Confirm cancellation/diversion semantics.** Review the 3,731 cancelled rows with departure timestamps (837 with wheels-off) against source documentation and decide how these records belong in delay/cancellation metrics.
3. **Document cause-field population and denominator.** Confirm what the cause components represent and align the root-cause report’s inclusion rule with the intended measure; quantify excluded cause minutes in any revised analysis.
4. **Resolve the one candidate-key collision** against the source and define a stable flight-row identity if available.
5. **Track low-impact gaps** such as 14,721 missing tail numbers and three airport coordinate records if those attributes become analysis inputs.

## 12. Audit execution, limitations, and next sprint

**Executed:** inspected project SQL/Python/schema definitions; connected through the shared SQLAlchemy module and `.env`; queried actual PostgreSQL table names, row counts, columns and constraints; ran read-only missingness, placeholder, duplicate, validity, date coverage, distribution, status and reference aggregates; compared airport joins and cause-query inclusion; verified elapsed-time arithmetic consistency.

**Not executed / not verifiable:** no source CSV files were available in the workspace; no external airport or cancellation-code reference was supplied; no business data dictionary was available to distinguish all legitimate edge cases; no SQL loading/analysis script was executed. Statistical extremes were not labeled errors absent a defensible domain threshold. No cleanup or remediation was performed.

**Recommended next sprint:** implement a reviewed, source-backed airport code reconciliation and automated validation checks for both airport endpoints, while preserving raw source codes and documenting any transformation. Keep the ambiguous cancellations and candidate duplicate under investigation until source semantics are confirmed.

## Final decision

**Sprint 2 audit completion: PASS.** The audit was completed with quantified evidence and documented limits. **Dataset quality: mixed; conditionally usable.** Airline and broad delay analyses have a sound base with NULL/status caveats, but airport and route analyses are not reliable as-is because all October destination codes fail the local reference join. No remediation was started.

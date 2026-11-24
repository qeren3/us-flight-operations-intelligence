# Sprint 3 — October Airport Code Reconciliation Investigation

**Audit date:** 2026-11-20  
**Scope:** Read-only PostgreSQL queries, local CSV/header and frequency inspection, and static review of project SQL/Python. No database object or record was changed; no SQL or Python file was modified.

## 1. Executive summary

October’s mismatch is present in the original local `C:\airline_data\flights.csv`, not introduced by PostgreSQL `COPY`: all 486,165 October source rows use five-digit numeric values in both airport columns, while the other 11 months use alphabetic airport codes. The source has 306 distinct origin IDs and 307 distinct destination IDs. The local `airports.csv`/`airports` reference has 322 IATA-code rows and no numeric identifier field.

The source and database row counts both equal 5,819,079. The database’s October destination code frequencies match the raw CSV exactly. Its origin frequency distribution also matches the raw CSV exactly after applying the ten origin mappings written in `sql/process_of_analyst.sql`. This strongly indicates that those ten origin substitutions (or an identical transformation) were applied after import; it does not prove the SQL script itself was executed. The SQL contains no destination correction.

Five-digit numeric values are consistent with a DOT airport identifier, not an airport code. BTS documents `OriginAirportID` as a unique DOT-assigned airport identifier, distinct from the `Origin` airport-code field; it also documents time-specific sequence IDs. This supports the identifier-system hypothesis but does not independently validate all 307 exact ID-to-code relationships. [BTS TranStats field definitions](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ) and [BTS table profile and definitions](https://transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&V0s1_b0yB=D&gnoyr_VQ=FGJ).

**No complete code-to-airport mapping is confirmed from local data.** Ten numeric-to-IATA pairs are explicit in project SQL and fit the current database frequencies, so they are strong candidates, but the local airport reference lacks the numeric IDs needed to verify them. The remaining codes are unresolved. The authoritative evidence required is the 2015 BTS source extract or crosswalk with paired airport ID and airport-code fields (and sequence/effective-time fields where available).

## 2. October code patterns

October contains 486,165 flight rows.

| Source/DB view | Code type | Rows | % of October rows | Distinct values | Local airport reference matches |
|---|---|---:|---:|---:|---:|
| Raw CSV origin | Numeric, all 5 digits | 486,165 | 100.00% | 306 | 0 |
| Raw CSV destination | Numeric, all 5 digits | 486,165 | 100.00% | 307 | 0 |
| Current DB origin | Numeric | 305,443 | 62.83% | 296 | 0 |
| Current DB origin | Alphabetic, three letters | 180,722 | 37.17% | 10 | 10 |
| Current DB destination | Numeric | 486,165 | 100.00% | 307 | 0 |
| Either column | NULL, mixed, or other | 0 | 0.00% | 0 | n/a |

Every numeric source code has length five. Origin numeric IDs are a subset of destination numeric IDs; destinations have one additional distinct ID not present as an origin. Every source ID in either column is unmatched to `airports.iata_code`. The ten current alphabetic origin values are ATL, ORD, DFW, DEN, LAX, SFO, IAH, PHX, LAS, and MSP; all match the local airport reference.

The patterns differ by column in the current database because ten origins have been converted while no destinations have. In the raw CSV, origin and destination follow the same October-only numeric pattern.

### Source monthly comparison

The table compares raw CSV code forms and current database reference join results. All non-October source airport values are alphabetic, and the database has zero unmatched airport codes in those months.

| Month | Rows | Distinct origin codes | Distinct destination codes | Source origin numeric | Source origin alphabetic | Source destination numeric | Source destination alphabetic | DB unmatched origins | DB unmatched destinations | DB rows surviving both airport joins |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 01 | 469,968 | 312 | 312 | 0 | 469,968 | 0 | 469,968 | 0 | 0 | 469,968 |
| 02 | 429,191 | 315 | 315 | 0 | 429,191 | 0 | 429,191 | 0 | 0 | 429,191 |
| 03 | 504,312 | 312 | 311 | 0 | 504,312 | 0 | 504,312 | 0 | 0 | 504,312 |
| 04 | 485,151 | 312 | 313 | 0 | 485,151 | 0 | 485,151 | 0 | 0 | 485,151 |
| 05 | 496,993 | 306 | 306 | 0 | 496,993 | 0 | 496,993 | 0 | 0 | 496,993 |
| 06 | 503,897 | 314 | 314 | 0 | 503,897 | 0 | 503,897 | 0 | 0 | 503,897 |
| 07 | 520,718 | 312 | 312 | 0 | 520,718 | 0 | 520,718 | 0 | 0 | 520,718 |
| 08 | 510,536 | 313 | 313 | 0 | 510,536 | 0 | 510,536 | 0 | 0 | 510,536 |
| 09 | 464,946 | 308 | 309 | 0 | 464,946 | 0 | 464,946 | 0 | 0 | 464,946 |
| 10 | 486,165 | 306 | 307 | 486,165 | 0 | 486,165 | 0 | 305,443 | 486,165 | 0 |
| 11 | 467,972 | 305 | 305 | 0 | 467,972 | 0 | 467,972 | 0 | 0 | 467,972 |
| 12 | 479,230 | 307 | 307 | 0 | 479,230 | 0 | 479,230 | 0 | 0 | 479,230 |

## 3. Distinct values and frequencies

### Most frequent source codes

The most frequent source origin IDs were 10397 (32,588), 13930 (27,652), 11298 (21,044), 11292 (18,136), 12892 (17,728), 14771 (14,170), 12266 (13,211), 14107 (12,921), 12889 (12,688), and 13487 (10,584). The corresponding ten codes are also the SQL’s only proposed mappings.

### Top 20 source origin codes

| Code | Rows | % of October | Reference status |
|---|---:|---:|---|
| 10397 | 32,588 | 6.70% | unmatched |
| 13930 | 27,652 | 5.69% | unmatched |
| 11298 | 21,044 | 4.33% | unmatched |
| 11292 | 18,136 | 3.73% | unmatched |
| 12892 | 17,728 | 3.65% | unmatched |
| 14771 | 14,170 | 2.91% | unmatched |
| 12266 | 13,211 | 2.72% | unmatched |
| 14107 | 12,921 | 2.66% | unmatched |
| 12889 | 12,688 | 2.61% | unmatched |
| 13487 | 10,584 | 2.18% | unmatched |
| 14747 | 10,388 | 2.14% | unmatched |
| 10721 | 10,164 | 2.09% | unmatched |
| 11433 | 9,925 | 2.04% | unmatched |
| 11618 | 9,622 | 1.98% | unmatched |
| 11057 | 9,572 | 1.97% | unmatched |
| 13204 | 9,047 | 1.86% | unmatched |
| 14869 | 8,763 | 1.80% | unmatched |
| 12953 | 8,590 | 1.77% | unmatched |
| 12478 | 8,303 | 1.71% | unmatched |
| 10821 | 8,022 | 1.65% | unmatched |

### Top 20 source destination codes

| Code | Rows | % of October | Reference status |
|---|---:|---:|---|
| 10397 | 32,594 | 6.70% | unmatched |
| 13930 | 27,608 | 5.68% | unmatched |
| 11298 | 21,033 | 4.33% | unmatched |
| 11292 | 18,125 | 3.73% | unmatched |
| 12892 | 17,739 | 3.65% | unmatched |
| 14771 | 14,170 | 2.91% | unmatched |
| 12266 | 13,227 | 2.72% | unmatched |
| 14107 | 12,932 | 2.66% | unmatched |
| 12889 | 12,702 | 2.61% | unmatched |
| 13487 | 10,623 | 2.19% | unmatched |
| 14747 | 10,385 | 2.14% | unmatched |
| 10721 | 10,161 | 2.09% | unmatched |
| 11433 | 9,913 | 2.04% | unmatched |
| 11618 | 9,656 | 1.99% | unmatched |
| 11057 | 9,573 | 1.97% | unmatched |
| 13204 | 9,048 | 1.86% | unmatched |
| 14869 | 8,764 | 1.80% | unmatched |
| 12953 | 8,570 | 1.76% | unmatched |
| 12478 | 8,285 | 1.70% | unmatched |
| 10821 | 8,020 | 1.65% | unmatched |

Full frequencies for all 307 numeric source values appear in Appendix A. Raw source origin has 306 distinct codes; raw destination has 307. The current database contains those same 307 numeric destination codes and the ten origin targets noted above; the appendix includes counts in raw source and current database for each code.

## 4. Confirmed mappings, candidates, and unresolved codes

**Confirmed numeric-ID-to-IATA mappings: none from local reference data.** The `airports` table and `airports.csv` contain only `IATA_CODE`, `AIRPORT`, `CITY`, `STATE`, `COUNTRY`, `LATITUDE`, and `LONGITUDE`; neither has a DOT airport ID or sequence ID. The 322 airport-code values in the CSV match the database airport-key set exactly, but this does not crosswalk numeric IDs.

The following pairs are **unverified candidates asserted by the existing `UPDATE` statement**. The raw source counts equal the current database counts under each target IATA code, which confirms the frequency-preserving substitution pattern, not the airport identity itself.

| Numeric source code | Proposed IATA code in SQL | Raw CSV origin rows | Raw CSV destination rows | Current DB origin rows under IATA code | Current DB destination rows under numeric code |
|---:|:---:|---:|---:|---:|---:|
| 10397 | ATL | 32,588 | 32,594 | 32,588 | 32,594 |
| 13930 | ORD | 27,652 | 27,608 | 27,652 | 27,608 |
| 11298 | DFW | 21,044 | 21,033 | 21,044 | 21,033 |
| 11292 | DEN | 18,136 | 18,125 | 18,136 | 18,125 |
| 12892 | LAX | 17,728 | 17,739 | 17,728 | 17,739 |
| 14771 | SFO | 14,170 | 14,170 | 14,170 | 14,170 |
| 12266 | IAH | 13,211 | 13,227 | 13,211 | 13,227 |
| 14107 | PHX | 12,921 | 12,932 | 12,921 | 12,932 |
| 12889 | LAS | 12,688 | 12,702 | 12,688 | 12,702 |
| 13487 | MSP | 10,584 | 10,623 | 10,584 | 10,623 |

There are 296 distinct numeric origin codes still unresolved in the current database and 307 distinct numeric destination codes. All 307 numeric IDs are listed with exact frequencies in Appendix A. The ten IDs above are still unresolved as destination codes even though project SQL proposes origin mappings for them. No numeric values were converted or inferred during this investigation.

## 5. Source and loading process

- Local files exist at `C:\airline_data\flights.csv`, `airports.csv`, and `airlines.csv`; the flight CSV contains 5,819,079 data rows, matching the database row count.
- The `flights.csv` header includes `ORIGIN_AIRPORT` and `DESTINATION_AIRPORT`; the explicit `COPY flights (...)` column list in `create_tables.sql` / `FlightsData.sql` aligns to the CSV header order. The `COPY` statement performs no mapping or expression transformation.
- `airports.csv` has 322 code rows and the seven columns listed above. Its code set exactly matches the 322 database airport keys; all are alphabetic.
- `sql/process_of_analyst.sql` contains an October-only `UPDATE` mapping ten numeric origin values to the ten current alphabetic origin values. It updates `origin_airport` only; it contains no destination mapping. The current DB origin-frequency dictionary equals the source dictionary after applying precisely these ten substitutions; destination frequencies are unchanged from the CSV.
- The other SQL files include table creation/import setup. No SQL file was executed as part of this investigation.

### Root-cause assessment

| Assessment | Evidence | Confidence |
|---|---|---|
| October raw source contains a different airport identifier representation | The original CSV itself has numeric five-digit origin and destination values for every October row; other 11 months are alphabetic. | High |
| Numeric values likely represent a DOT/BTS Airport ID | Five-digit format; BTS field catalog distinguishes unique `OriginAirportID` from the airport-code field `Origin`. | High for identifier-system hypothesis; not a per-code mapping confirmation |
| Database origin has a partial correction | Current DB origin counts equal the CSV after the ten SQL substitutions, while all destination codes remain raw numeric. | High that the transformation occurred; medium on whether this exact SQL file was executed (no execution log) |
| COPY column-order error caused the pattern | Header/explicit COPY column order aligns; all months except October have matching alphabetic codes. | Low; no supporting evidence |
| Local airport reference is itself the source of the mismatch | The reference CSV and database keys agree exactly and contain only alphabetic IATA-like codes; no alternative ID field exists. | Low; current evidence favors source-ID/reference mismatch instead |
| Why the source changed identifier systems only in October | No source manifest, transformation history, or upstream processing logs are available. | Unknown |

The strongest supported explanation is: **the CSV was already inconsistent for October, then a partial origin-only normalization was applied before or after the current database load.** Why the CSV uses numeric IDs in October is not established. The exact ten mapping assertions are not independently confirmed.

## 6. Analytical impact

- **Origin-only airport joins:** 305,443 October rows (62.83%) fail the local airport join; 180,722 (37.17%) survive.
- **Joins requiring both endpoints:** all 486,165 October rows fail because every destination is unmatched; zero October rows survive.
- **Airport rankings and origin summaries:** numeric origins disappear from `INNER JOIN airports` analyses, which can understate airport volumes and distort delay rankings. Across the full year, 305,443 rows (5.25%) are affected at the origin endpoint.
- **Route analysis:** loses the whole October cohort (8.35% of the annual dataset) under two-endpoint inner joins. Annual route comparisons consequently omit one month.
- **Fixed top-ten origin heatmap:** it receives 180,722 October rows, including the ten alphabetic origins produced by the candidate mappings. Coverage for those selected airports is conditional on the ten mappings being correct; the remaining numeric origins are excluded by its IATA filter.

No existing KPI or query was changed.

## 7. Recommended reconciliation architecture

Use a small, explicit crosswalk layer; retain the source code unchanged.

1. Preserve raw `origin_airport` and `destination_airport` values in a raw/staging layer (or immutable raw columns) and record source file/version.
2. Obtain an authoritative, 2015-relevant BTS crosswalk/source extract pairing `OriginAirportID` with `Origin` and `DestAirportID` with `Dest`. Prefer sequence/effective-time keys for historical airport-code changes. BTS notes that codes may change or be reused and that Airport IDs/sequence IDs serve distinct identification purposes.
3. Store verified rows in a simple mapping table or checked-in mapping file with source identifier system, numeric ID, canonical airport code, effective period/sequence ID, source citation/version, and review status. Enforce one-to-one mapping for the key used; send ambiguous/unmapped values to review.
4. Reconcile via `LEFT JOIN`, never by filtering out unmatched flights. Report mapped, ambiguous, and unresolved counts separately; do not silently drop or overwrite raw codes.
5. Validate pre/post row counts (486,165 October rows preserved), both endpoint coverage, unique mapping keys, and no unexpected row multiplication. Add tests for the October cohort and general airport-reference integrity before enabling existing joins.

## 8. Next-sprint implementation plan

1. Acquire the official 2015 BTS row-level export or identifier crosswalk containing both airport ID and airport code for origin and destination; record its version and checksum.
2. Compare all 307 numeric values against that source, separately for origin and destination; confirm or reject the ten existing SQL candidates and review the destination-only code.
3. Document one-to-one, ambiguous, obsolete, and unresolved codes; do not map from frequency or city-name guesses.
4. Add a minimal mapping layer while preserving raw identifiers. Resolve every row or expose unresolved status; keep unmatched flight records in the output.
5. Add assertions for unique mapping keys, full row preservation, no join multiplication, and reference-coverage targets; compare airport/route summaries before and after only once mapping is reviewed.

## 9. Tests executed and limitations

**Executed:** read-only database inspection via the shared connection module; frequency aggregation of all October origin/destination codes; monthly code-form and reference-match comparison; source CSV header/row/frequency scan; exact frequency comparison between raw CSV and current database; static inspection of `COPY` and October `UPDATE` statements; airport reference CSV/database code-set comparison; BTS field-definition review.

**Not executed:** no DDL/DML, corrections, or chart/KPI changes. No authoritative 2015 ID-to-IATA crosswalk was present locally or downloaded; therefore the ten SQL pairs and other numeric IDs are not certified. No upstream ETL logs or original source publisher/version manifest were available, so the earlier reason for the October-only values cannot be proven.

## Final decision

**Sprint 3 investigation: PASS.** The cause can be localized to numeric IDs already present in the raw CSV, with a strongly evidenced partial origin-only correction. **The reconciliation itself is unresolved.** A source-backed 2015 BTS crosswalk pairing airport IDs with airport codes is required before implementing any mapping. No correction has been applied.

## Appendix A — October raw numeric code frequencies

## Appendix A — October raw numeric code frequencies

These rows cover the union of every numeric airport code in the October source CSV (307 codes). Source origin and destination columns are counted independently. The database columns show current values after the project’s ten origin mappings; a target is an unverified SQL candidate, not an independently validated airport crosswalk.

| Source numeric code | CSV origin rows | CSV destination rows | Current DB origin value | Current DB origin rows under source numeric code | Current DB destination rows | Existing SQL origin candidate | DB origin rows under candidate |
|---:|---:|---|---:|---:|---|---:|
| 10135 | 239 | 238 | 10135 | 239 | 238 |  | 0 |
| 10136 | 201 | 201 | 10136 | 201 | 201 |  | 0 |
| 10140 | 1,816 | 1,815 | 10140 | 1,816 | 1,815 |  | 0 |
| 10141 | 71 | 71 | 10141 | 71 | 71 |  | 0 |
| 10146 | 87 | 87 | 10146 | 87 | 87 |  | 0 |
| 10154 | 28 | 28 | 10154 | 28 | 28 |  | 0 |
| 10155 | 148 | 148 | 10155 | 148 | 148 |  | 0 |
| 10157 | 122 | 122 | 10157 | 122 | 122 |  | 0 |
| 10158 | 248 | 248 | 10158 | 248 | 248 |  | 0 |
| 10165 | 9 | 9 | 10165 | 9 | 9 |  | 0 |
| 10170 | 31 | 31 | 10170 | 31 | 31 |  | 0 |
| 10185 | 282 | 282 | 10185 | 282 | 282 |  | 0 |
| 10208 | 223 | 222 | 10208 | 223 | 222 |  | 0 |
| 10257 | 734 | 733 | 10257 | 734 | 733 |  | 0 |
| 10268 | 57 | 56 | 10268 | 57 | 56 |  | 0 |
| 10279 | 307 | 307 | 10279 | 307 | 307 |  | 0 |
| 10299 | 1,234 | 1,232 | 10299 | 1,234 | 1,232 |  | 0 |
| 10333 | 53 | 53 | 10333 | 53 | 53 |  | 0 |
| 10372 | 59 | 59 | 10372 | 59 | 59 |  | 0 |
| 10397 | 32,588 | 32,594 | ATL | 0 | 32,594 | ATL | 32,588 |
| 10408 | 260 | 260 | 10408 | 260 | 260 |  | 0 |
| 10423 | 4,021 | 4,014 | 10423 | 4,021 | 4,014 |  | 0 |
| 10431 | 284 | 283 | 10431 | 284 | 283 |  | 0 |
| 10434 | 113 | 113 | 10434 | 113 | 113 |  | 0 |
| 10469 | 121 | 121 | 10469 | 121 | 121 |  | 0 |
| 10529 | 1,714 | 1,715 | 10529 | 1,714 | 1,715 |  | 0 |
| 10551 | 84 | 84 | 10551 | 84 | 84 |  | 0 |
| 10561 | 183 | 183 | 10561 | 183 | 183 |  | 0 |
| 10577 | 62 | 61 | 10577 | 62 | 61 |  | 0 |
| 10581 | 27 | 26 | 10581 | 27 | 26 |  | 0 |
| 10599 | 1,146 | 1,146 | 10599 | 1,146 | 1,146 |  | 0 |
| 10620 | 264 | 263 | 10620 | 264 | 263 |  | 0 |
| 10627 | 339 | 340 | 10627 | 339 | 340 |  | 0 |
| 10631 | 62 | 62 | 10631 | 62 | 62 |  | 0 |
| 10666 | 0 | 1 | 10666 | 0 | 1 |  | 0 |
| 10685 | 238 | 238 | 10685 | 238 | 238 |  | 0 |
| 10693 | 4,477 | 4,479 | 10693 | 4,477 | 4,479 |  | 0 |
| 10713 | 1,160 | 1,163 | 10713 | 1,160 | 1,163 |  | 0 |
| 10721 | 10,164 | 10,161 | 10721 | 10,164 | 10,161 |  | 0 |
| 10728 | 87 | 87 | 10728 | 87 | 87 |  | 0 |
| 10731 | 85 | 85 | 10731 | 85 | 85 |  | 0 |
| 10732 | 96 | 98 | 10732 | 96 | 98 |  | 0 |
| 10739 | 53 | 53 | 10739 | 53 | 53 |  | 0 |
| 10747 | 204 | 203 | 10747 | 204 | 203 |  | 0 |
| 10754 | 81 | 81 | 10754 | 81 | 81 |  | 0 |
| 10779 | 62 | 62 | 10779 | 62 | 62 |  | 0 |
| 10781 | 659 | 659 | 10781 | 659 | 659 |  | 0 |
| 10785 | 348 | 349 | 10785 | 348 | 349 |  | 0 |
| 10792 | 1,593 | 1,587 | 10792 | 1,593 | 1,587 |  | 0 |
| 10800 | 1,768 | 1,767 | 10800 | 1,768 | 1,767 |  | 0 |
| 10821 | 8,022 | 8,020 | 10821 | 8,022 | 8,020 |  | 0 |
| 10849 | 335 | 335 | 10849 | 335 | 335 |  | 0 |
| 10868 | 434 | 434 | 10868 | 434 | 434 |  | 0 |
| 10874 | 491 | 490 | 10874 | 491 | 490 |  | 0 |
| 10918 | 53 | 53 | 10918 | 53 | 53 |  | 0 |
| 10926 | 62 | 62 | 10926 | 62 | 62 |  | 0 |
| 10980 | 417 | 416 | 10980 | 417 | 416 |  | 0 |
| 10990 | 237 | 237 | 10990 | 237 | 237 |  | 0 |
| 10994 | 1,207 | 1,207 | 10994 | 1,207 | 1,207 |  | 0 |
| 11003 | 532 | 533 | 11003 | 532 | 533 |  | 0 |
| 11013 | 57 | 57 | 11013 | 57 | 57 |  | 0 |
| 11042 | 3,224 | 3,221 | 11042 | 3,224 | 3,221 |  | 0 |
| 11049 | 223 | 222 | 11049 | 223 | 222 |  | 0 |
| 11057 | 9,572 | 9,573 | 11057 | 9,572 | 9,573 |  | 0 |
| 11066 | 2,188 | 2,188 | 11066 | 2,188 | 2,188 |  | 0 |
| 11067 | 206 | 206 | 11067 | 206 | 206 |  | 0 |
| 11076 | 62 | 62 | 11076 | 62 | 62 |  | 0 |
| 11097 | 31 | 31 | 11097 | 31 | 31 |  | 0 |
| 11109 | 610 | 607 | 11109 | 610 | 607 |  | 0 |
| 11111 | 123 | 123 | 11111 | 123 | 123 |  | 0 |
| 11122 | 138 | 139 | 11122 | 138 | 139 |  | 0 |
| 11140 | 366 | 366 | 11140 | 366 | 366 |  | 0 |
| 11146 | 224 | 224 | 11146 | 224 | 224 |  | 0 |
| 11150 | 112 | 112 | 11150 | 112 | 112 |  | 0 |
| 11193 | 1,919 | 1,917 | 11193 | 1,919 | 1,917 |  | 0 |
| 11203 | 145 | 144 | 11203 | 145 | 144 |  | 0 |
| 11252 | 119 | 119 | 11252 | 119 | 119 |  | 0 |
| 11259 | 5,930 | 5,930 | 11259 | 5,930 | 5,930 |  | 0 |
| 11267 | 753 | 753 | 11267 | 753 | 753 |  | 0 |
| 11274 | 87 | 87 | 11274 | 87 | 87 |  | 0 |
| 11278 | 6,819 | 6,818 | 11278 | 6,819 | 6,818 |  | 0 |
| 11292 | 18,136 | 18,125 | DEN | 0 | 18,125 | DEN | 18,136 |
| 11298 | 21,044 | 21,033 | DFW | 0 | 21,033 | DFW | 21,044 |
| 11308 | 118 | 118 | 11308 | 118 | 118 |  | 0 |
| 11315 | 61 | 61 | 11315 | 61 | 61 |  | 0 |
| 11337 | 223 | 223 | 11337 | 223 | 223 |  | 0 |
| 11413 | 178 | 178 | 11413 | 178 | 178 |  | 0 |
| 11423 | 710 | 710 | 11423 | 710 | 710 |  | 0 |
| 11433 | 9,925 | 9,913 | 11433 | 9,925 | 9,913 |  | 0 |
| 11447 | 49 | 48 | 11447 | 49 | 48 |  | 0 |
| 11471 | 62 | 62 | 11471 | 62 | 62 |  | 0 |
| 11481 | 376 | 375 | 11481 | 376 | 375 |  | 0 |
| 11503 | 4 | 3 | 11503 | 4 | 3 |  | 0 |
| 11525 | 53 | 53 | 11525 | 53 | 53 |  | 0 |
| 11537 | 195 | 195 | 11537 | 195 | 195 |  | 0 |
| 11540 | 1,046 | 1,045 | 11540 | 1,046 | 1,045 |  | 0 |
| 11577 | 57 | 57 | 11577 | 57 | 57 |  | 0 |
| 11587 | 53 | 53 | 11587 | 53 | 53 |  | 0 |
| 11603 | 328 | 328 | 11603 | 328 | 328 |  | 0 |
| 11612 | 399 | 399 | 11612 | 399 | 399 |  | 0 |
| 11617 | 55 | 55 | 11617 | 55 | 55 |  | 0 |
| 11618 | 9,622 | 9,656 | 11618 | 9,622 | 9,656 |  | 0 |
| 11624 | 151 | 151 | 11624 | 151 | 151 |  | 0 |
| 11630 | 177 | 177 | 11630 | 177 | 177 |  | 0 |
| 11637 | 527 | 526 | 11637 | 527 | 526 |  | 0 |
| 11638 | 656 | 657 | 11638 | 656 | 657 |  | 0 |
| 11641 | 150 | 150 | 11641 | 150 | 150 |  | 0 |
| 11648 | 123 | 123 | 11648 | 123 | 123 |  | 0 |
| 11695 | 158 | 158 | 11695 | 158 | 158 |  | 0 |
| 11697 | 5,812 | 5,820 | 11697 | 5,812 | 5,820 |  | 0 |
| 11721 | 413 | 412 | 11721 | 413 | 412 |  | 0 |
| 11775 | 445 | 444 | 11775 | 445 | 444 |  | 0 |
| 11778 | 180 | 180 | 11778 | 180 | 180 |  | 0 |
| 11823 | 511 | 511 | 11823 | 511 | 511 |  | 0 |
| 11865 | 88 | 88 | 11865 | 88 | 88 |  | 0 |
| 11867 | 62 | 62 | 11867 | 62 | 62 |  | 0 |
| 11884 | 828 | 829 | 11884 | 828 | 829 |  | 0 |
| 11898 | 90 | 89 | 11898 | 90 | 89 |  | 0 |
| 11905 | 59 | 60 | 11905 | 59 | 60 |  | 0 |
| 11921 | 271 | 271 | 11921 | 271 | 271 |  | 0 |
| 11953 | 234 | 234 | 11953 | 234 | 234 |  | 0 |
| 11973 | 304 | 303 | 11973 | 304 | 303 |  | 0 |
| 11977 | 489 | 488 | 11977 | 489 | 488 |  | 0 |
| 11980 | 57 | 57 | 11980 | 57 | 57 |  | 0 |
| 11982 | 371 | 370 | 11982 | 371 | 370 |  | 0 |
| 11986 | 928 | 927 | 11986 | 928 | 927 |  | 0 |
| 11995 | 598 | 595 | 11995 | 598 | 595 |  | 0 |
| 11996 | 631 | 630 | 11996 | 631 | 630 |  | 0 |
| 12003 | 190 | 190 | 12003 | 190 | 190 |  | 0 |
| 12007 | 88 | 88 | 12007 | 88 | 88 |  | 0 |
| 12016 | 31 | 31 | 12016 | 31 | 31 |  | 0 |
| 12094 | 20 | 20 | 12094 | 20 | 20 |  | 0 |
| 12129 | 84 | 84 | 12129 | 84 | 84 |  | 0 |
| 12156 | 141 | 141 | 12156 | 141 | 141 |  | 0 |
| 12173 | 3,780 | 3,780 | 12173 | 3,780 | 3,780 |  | 0 |
| 12177 | 53 | 53 | 12177 | 53 | 53 |  | 0 |
| 12191 | 4,718 | 4,717 | 12191 | 4,718 | 4,717 |  | 0 |
| 12197 | 721 | 720 | 12197 | 721 | 720 |  | 0 |
| 12206 | 287 | 286 | 12206 | 287 | 286 |  | 0 |
| 12217 | 390 | 390 | 12217 | 390 | 390 |  | 0 |
| 12255 | 53 | 53 | 12255 | 53 | 53 |  | 0 |
| 12264 | 2,996 | 3,000 | 12264 | 2,996 | 3,000 |  | 0 |
| 12265 | 22 | 22 | 12265 | 22 | 22 |  | 0 |
| 12266 | 13,211 | 13,227 | IAH | 0 | 13,227 | IAH | 13,211 |
| 12278 | 698 | 698 | 12278 | 698 | 698 |  | 0 |
| 12280 | 201 | 201 | 12280 | 201 | 201 |  | 0 |
| 12323 | 215 | 215 | 12323 | 215 | 215 |  | 0 |
| 12335 | 58 | 57 | 12335 | 58 | 57 |  | 0 |
| 12339 | 2,373 | 2,378 | 12339 | 2,373 | 2,378 |  | 0 |
| 12343 | 53 | 53 | 12343 | 53 | 53 |  | 0 |
| 12389 | 221 | 220 | 12389 | 221 | 220 |  | 0 |
| 12391 | 366 | 366 | 12391 | 366 | 366 |  | 0 |
| 12402 | 503 | 504 | 12402 | 503 | 504 |  | 0 |
| 12441 | 158 | 157 | 12441 | 158 | 157 |  | 0 |
| 12448 | 654 | 654 | 12448 | 654 | 654 |  | 0 |
| 12451 | 1,712 | 1,710 | 12451 | 1,712 | 1,710 |  | 0 |
| 12478 | 8,303 | 8,285 | 12478 | 8,303 | 8,285 |  | 0 |
| 12511 | 58 | 58 | 12511 | 58 | 58 |  | 0 |
| 12519 | 75 | 75 | 12519 | 75 | 75 |  | 0 |
| 12523 | 336 | 336 | 12523 | 336 | 336 |  | 0 |
| 12758 | 967 | 967 | 12758 | 967 | 967 |  | 0 |
| 12819 | 186 | 186 | 12819 | 186 | 186 |  | 0 |
| 12884 | 222 | 224 | 12884 | 222 | 224 |  | 0 |
| 12888 | 53 | 53 | 12888 | 53 | 53 |  | 0 |
| 12889 | 12,688 | 12,702 | LAS | 0 | 12,702 | LAS | 12,688 |
| 12891 | 124 | 124 | 12891 | 124 | 124 |  | 0 |
| 12892 | 17,728 | 17,739 | LAX | 0 | 17,739 | LAX | 17,728 |
| 12896 | 436 | 435 | 12896 | 436 | 435 |  | 0 |
| 12898 | 117 | 117 | 12898 | 117 | 117 |  | 0 |
| 12915 | 198 | 198 | 12915 | 198 | 198 |  | 0 |
| 12945 | 587 | 586 | 12945 | 587 | 586 |  | 0 |
| 12951 | 431 | 432 | 12951 | 431 | 432 |  | 0 |
| 12953 | 8,590 | 8,570 | 12953 | 8,590 | 8,570 |  | 0 |
| 12954 | 774 | 775 | 12954 | 774 | 775 |  | 0 |
| 12982 | 881 | 882 | 12982 | 881 | 882 |  | 0 |
| 12992 | 1,048 | 1,050 | 12992 | 1,048 | 1,050 |  | 0 |
| 13029 | 288 | 288 | 13029 | 288 | 288 |  | 0 |
| 13061 | 203 | 203 | 13061 | 203 | 203 |  | 0 |
| 13076 | 166 | 166 | 13076 | 166 | 166 |  | 0 |
| 13127 | 53 | 53 | 13127 | 53 | 53 |  | 0 |
| 13158 | 600 | 601 | 13158 | 600 | 601 |  | 0 |
| 13184 | 142 | 142 | 13184 | 142 | 142 |  | 0 |
| 13198 | 3,555 | 3,557 | 13198 | 3,555 | 3,557 |  | 0 |
| 13204 | 9,047 | 9,048 | 13204 | 9,047 | 9,048 |  | 0 |
| 13230 | 285 | 285 | 13230 | 285 | 285 |  | 0 |
| 13232 | 7,617 | 7,613 | 13232 | 7,617 | 7,613 |  | 0 |
| 13241 | 84 | 84 | 13241 | 84 | 84 |  | 0 |
| 13244 | 1,520 | 1,518 | 13244 | 1,520 | 1,518 |  | 0 |
| 13256 | 238 | 239 | 13256 | 238 | 239 |  | 0 |
| 13264 | 243 | 243 | 13264 | 243 | 243 |  | 0 |
| 13277 | 309 | 309 | 13277 | 309 | 309 |  | 0 |
| 13290 | 151 | 151 | 13290 | 151 | 151 |  | 0 |
| 13296 | 577 | 579 | 13296 | 577 | 579 |  | 0 |
| 13303 | 5,958 | 5,956 | 13303 | 5,958 | 5,956 |  | 0 |
| 13342 | 2,642 | 2,644 | 13342 | 2,642 | 2,644 |  | 0 |
| 13344 | 62 | 62 | 13344 | 62 | 62 |  | 0 |
| 13360 | 116 | 116 | 13360 | 116 | 116 |  | 0 |
| 13367 | 308 | 308 | 13367 | 308 | 308 |  | 0 |
| 13377 | 279 | 278 | 13377 | 279 | 278 |  | 0 |
| 13422 | 437 | 438 | 13422 | 437 | 438 |  | 0 |
| 13433 | 218 | 218 | 13433 | 218 | 218 |  | 0 |
| 13459 | 26 | 26 | 13459 | 26 | 26 |  | 0 |
| 13476 | 241 | 241 | 13476 | 241 | 241 |  | 0 |
| 13485 | 838 | 837 | 13485 | 838 | 837 |  | 0 |
| 13486 | 171 | 170 | 13486 | 171 | 170 |  | 0 |
| 13487 | 10,584 | 10,623 | MSP | 0 | 10,623 | MSP | 10,584 |
| 13495 | 3,663 | 3,670 | 13495 | 3,663 | 3,670 |  | 0 |
| 13502 | 6 | 7 | 13502 | 6 | 7 |  | 0 |
| 13541 | 11 | 11 | 13541 | 11 | 11 |  | 0 |
| 13577 | 507 | 507 | 13577 | 507 | 507 |  | 0 |
| 13795 | 112 | 112 | 13795 | 112 | 112 |  | 0 |
| 13796 | 4,016 | 4,012 | 13796 | 4,016 | 4,012 |  | 0 |
| 13830 | 1,823 | 1,823 | 13830 | 1,823 | 1,823 |  | 0 |
| 13851 | 1,641 | 1,639 | 13851 | 1,641 | 1,639 |  | 0 |
| 13871 | 1,501 | 1,501 | 13871 | 1,501 | 1,501 |  | 0 |
| 13873 | 62 | 62 | 13873 | 62 | 62 |  | 0 |
| 13891 | 1,742 | 1,742 | 13891 | 1,742 | 1,742 |  | 0 |
| 13930 | 27,652 | 27,608 | ORD | 0 | 27,608 | ORD | 27,652 |
| 13931 | 914 | 911 | 13931 | 914 | 911 |  | 0 |
| 13933 | 62 | 62 | 13933 | 62 | 62 |  | 0 |
| 13964 | 36 | 36 | 13964 | 36 | 36 |  | 0 |
| 13970 | 62 | 62 | 13970 | 62 | 62 |  | 0 |
| 14006 | 62 | 62 | 14006 | 62 | 62 |  | 0 |
| 14025 | 13 | 13 | 14025 | 13 | 13 |  | 0 |
| 14027 | 1,742 | 1,746 | 14027 | 1,742 | 1,746 |  | 0 |
| 14057 | 4,550 | 4,553 | 14057 | 4,550 | 4,553 |  | 0 |
| 14098 | 114 | 114 | 14098 | 114 | 114 |  | 0 |
| 14100 | 6,094 | 6,089 | 14100 | 6,094 | 6,089 |  | 0 |
| 14107 | 12,921 | 12,932 | PHX | 0 | 12,932 | PHX | 12,921 |
| 14108 | 476 | 475 | 14108 | 476 | 475 |  | 0 |
| 14109 | 53 | 53 | 14109 | 53 | 53 |  | 0 |
| 14113 | 57 | 57 | 14113 | 57 | 57 |  | 0 |
| 14122 | 2,131 | 2,130 | 14122 | 2,131 | 2,130 |  | 0 |
| 14150 | 62 | 62 | 14150 | 62 | 62 |  | 0 |
| 14193 | 478 | 478 | 14193 | 478 | 478 |  | 0 |
| 14222 | 9 | 9 | 14222 | 9 | 9 |  | 0 |
| 14252 | 210 | 210 | 14252 | 210 | 210 |  | 0 |
| 14254 | 62 | 62 | 14254 | 62 | 62 |  | 0 |
| 14256 | 62 | 62 | 14256 | 62 | 62 |  | 0 |
| 14262 | 673 | 673 | 14262 | 673 | 673 |  | 0 |
| 14307 | 1,098 | 1,098 | 14307 | 1,098 | 1,098 |  | 0 |
| 14321 | 477 | 479 | 14321 | 477 | 479 |  | 0 |
| 14457 | 236 | 236 | 14457 | 236 | 236 |  | 0 |
| 14487 | 62 | 62 | 14487 | 62 | 62 |  | 0 |
| 14489 | 200 | 200 | 14489 | 200 | 200 |  | 0 |
| 14492 | 3,002 | 2,999 | 14492 | 3,002 | 2,999 |  | 0 |
| 14520 | 88 | 89 | 14520 | 88 | 89 |  | 0 |
| 14524 | 1,647 | 1,647 | 14524 | 1,647 | 1,647 |  | 0 |
| 14543 | 57 | 57 | 14543 | 57 | 57 |  | 0 |
| 14570 | 1,144 | 1,144 | 14570 | 1,144 | 1,144 |  | 0 |
| 14574 | 223 | 223 | 14574 | 223 | 223 |  | 0 |
| 14576 | 737 | 738 | 14576 | 737 | 738 |  | 0 |
| 14588 | 92 | 92 | 14588 | 92 | 92 |  | 0 |
| 14633 | 185 | 185 | 14633 | 185 | 185 |  | 0 |
| 14635 | 1,766 | 1,778 | 14635 | 1,766 | 1,778 |  | 0 |
| 14674 | 93 | 93 | 14674 | 93 | 93 |  | 0 |
| 14679 | 6,209 | 6,207 | 14679 | 6,209 | 6,207 |  | 0 |
| 14683 | 2,624 | 2,626 | 14683 | 2,624 | 2,626 |  | 0 |
| 14685 | 661 | 661 | 14685 | 661 | 661 |  | 0 |
| 14689 | 565 | 564 | 14689 | 565 | 564 |  | 0 |
| 14696 | 415 | 416 | 14696 | 415 | 416 |  | 0 |
| 14698 | 250 | 249 | 14698 | 250 | 249 |  | 0 |
| 14709 | 81 | 81 | 14709 | 81 | 81 |  | 0 |
| 14711 | 62 | 62 | 14711 | 62 | 62 |  | 0 |
| 14730 | 843 | 844 | 14730 | 843 | 844 |  | 0 |
| 14747 | 10,388 | 10,385 | 14747 | 10,388 | 10,385 |  | 0 |
| 14771 | 14,170 | 14,170 | SFO | 0 | 14,170 | SFO | 14,170 |
| 14783 | 531 | 529 | 14783 | 531 | 529 |  | 0 |
| 14794 | 203 | 203 | 14794 | 203 | 203 |  | 0 |
| 14814 | 556 | 555 | 14814 | 556 | 555 |  | 0 |
| 14828 | 93 | 93 | 14828 | 93 | 93 |  | 0 |
| 14831 | 3,481 | 3,482 | 14831 | 3,481 | 3,482 |  | 0 |
| 14842 | 149 | 148 | 14842 | 149 | 148 |  | 0 |
| 14843 | 1,868 | 1,876 | 14843 | 1,868 | 1,876 |  | 0 |
| 14869 | 8,763 | 8,764 | 14869 | 8,763 | 8,764 |  | 0 |
| 14893 | 3,618 | 3,618 | 14893 | 3,618 | 3,618 |  | 0 |
| 14905 | 62 | 62 | 14905 | 62 | 62 |  | 0 |
| 14908 | 3,542 | 3,538 | 14908 | 3,542 | 3,538 |  | 0 |
| 14952 | 150 | 150 | 14952 | 150 | 150 |  | 0 |
| 14960 | 122 | 122 | 14960 | 122 | 122 |  | 0 |
| 14986 | 305 | 306 | 14986 | 305 | 306 |  | 0 |
| 15016 | 4,314 | 4,310 | 15016 | 4,314 | 4,310 |  | 0 |
| 15024 | 237 | 237 | 15024 | 237 | 237 |  | 0 |
| 15027 | 68 | 69 | 15027 | 68 | 69 |  | 0 |
| 15041 | 62 | 62 | 15041 | 62 | 62 |  | 0 |
| 15048 | 57 | 57 | 15048 | 57 | 57 |  | 0 |
| 15070 | 62 | 62 | 15070 | 62 | 62 |  | 0 |
| 15096 | 640 | 639 | 15096 | 640 | 639 |  | 0 |
| 15249 | 279 | 279 | 15249 | 279 | 279 |  | 0 |
| 15295 | 88 | 88 | 15295 | 88 | 88 |  | 0 |
| 15304 | 5,143 | 5,148 | 15304 | 5,143 | 5,148 |  | 0 |
| 15323 | 159 | 159 | 15323 | 159 | 159 |  | 0 |
| 15356 | 277 | 277 | 15356 | 277 | 277 |  | 0 |
| 15370 | 1,319 | 1,318 | 15370 | 1,319 | 1,318 |  | 0 |
| 15376 | 1,311 | 1,313 | 15376 | 1,311 | 1,313 |  | 0 |
| 15380 | 208 | 208 | 15380 | 208 | 208 |  | 0 |
| 15389 | 87 | 87 | 15389 | 87 | 87 |  | 0 |
| 15401 | 88 | 88 | 15401 | 88 | 88 |  | 0 |
| 15411 | 227 | 227 | 15411 | 227 | 227 |  | 0 |
| 15412 | 629 | 629 | 15412 | 629 | 629 |  | 0 |
| 15497 | 14 | 14 | 15497 | 14 | 14 |  | 0 |
| 15607 | 88 | 88 | 15607 | 88 | 88 |  | 0 |
| 15624 | 415 | 416 | 15624 | 415 | 416 |  | 0 |
| 15841 | 62 | 62 | 15841 | 62 | 62 |  | 0 |
| 15919 | 941 | 940 | 15919 | 941 | 940 |  | 0 |
| 15991 | 62 | 62 | 15991 | 62 | 62 |  | 0 |
| 16218 | 177 | 177 | 16218 | 177 | 177 |  | 0 |

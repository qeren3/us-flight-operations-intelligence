# Sprint 7 — Python Visualization Migration

## Executive summary

**Verdict: PASS for the applicable visualization migration.** The chart inventory is complete. The one airport-dependent chart was migrated into a parallel normalized script and its PNG was generated and visually inspected. The three other primary charts do not join airport or route data, so they were left unchanged. The normalized heatmap results exactly match the current original-query results for its fixed ten-airport selection in all months. This is expected: Sprint 5 had already converted the October origin values represented in this chart's selection. Other October airport and route analyses benefit from normalized coverage, as documented in Sprint 6; this particular heatmap's selected groups do not change further.

## Existing chart inventory

| Script | Purpose / chart | Source and KPI / filters | Output | Airport/route dependency | Action |
|---|---|---|---|---|---|
| `python/airport_heatmap.py` | Monthly departure-delay heatmap for the fixed ten airport codes ATL, ORD, DFW, DEN, LAX, SFO, PHX, IAH, LAS, MSP | `flights`; average departure delay by origin and month; excludes NULL departure delay; SQL rounds to one decimal | `assets/airport_monthly_heatmap.png` | Origin airport only; October codes were affected by reconciliation | Migrated to normalized source |
| `python/airline_delays_chart.py` | Horizontal bar chart of average departure delay by airline | `flights` INNER JOIN `airlines`; average delay grouped by airline; no additional filter | `assets/airline_delays.png` | No airport/route dependency | Left unchanged |
| `python/hourly_delay_chart.py` | Line chart of average delay by scheduled departure hour | Flight table; scheduled departure non-NULL; average delay grouped by integer hour; chart filters plotted hours to 0–23 | `assets/hourly_delay_trend.png` | No airport/route dependency | Left unchanged |
| `python/root_cause_chart.py` | Donut chart of delay causes in hours | Flight table; sums five cause-delay columns divided by 60; rows with departure delay > 0; pie percentages are proportions of those sums | `assets/root_cause_distribution.png` | No airport/route dependency | Left unchanged |
| `python/tempCodeRunnerFile.py` | Temporary duplicate of the hourly delay line chart | Same SQL, KPI and plotting logic as `hourly_delay_chart.py` | Same relative output name as the hourly chart | No airport/route dependency | Treated as an editor-generated duplicate, not a primary chart; left untouched and not run |

The database connection helper `python/db_connect.py` is shared by the original scripts. The migrated script also uses its `get_engine()` function and does not contain connection settings.

## Migration and SQL dependency

Created `python/normalized/airport_heatmap.py`. It queries `public.flights_normalized.origin_airport_iata`, groups and averages in SQL, and retains the original fixed airport selection, month grouping, and non-NULL departure-delay filter. The airport list is bound as a parameter. The query uses the same `AVG` NULL behavior and one-decimal SQL rounding as the original chart.

The Sprint 6 monthly airport query is a general all-airport origin/destination report. The heatmap needs only its origin aggregation and has a chart-specific filter and one-decimal output, so the normalized script uses the same aggregation directly against the Sprint 6 normalized view rather than fetching destination rows or calculating the average in Python.

Visual design was preserved: 13×7-inch figure, YlOrRd palette, annotations, airport labels, Turkish month labels, title, axis labels and color-bar caption. The script writes only to `assets/normalized/airport_monthly_heatmap.png`, uses a noninteractive renderer, closes the figure and disposes the SQLAlchemy engine after querying. Database failures print only the exception type and a generic troubleshooting message.

## Before/after comparison

The original query was compared with the equivalent normalized query using the same airport list, non-NULL filter, grouping, and rounding. The data comparison grouped by airport and month and checked flight counts and rounded averages.

| Measure | Original query | Normalized query | Difference |
|---|---:|---:|---:|
| Airport/month groups, each month | 10 | 10 | 0 |
| Selected-airport delay observations, October 2015 | 179,953 | 179,953 | 0 |
| Selected airport/month groups with changed counts or average | — | — | 0 of 120 |
| All selected-airport monthly groups with matching counts and averages | — | — | 120 of 120 |

All twelve monthly totals matched exactly. In October, each of the ten selected airports had matching source and normalized delay-observation counts: ATL 32,561; ORD 27,609; DFW 20,647; DEN 18,106; LAX 17,656; SFO 14,116; PHX 12,905; IAH 13,121; LAS 12,663; MSP 10,569. The normalized heatmap therefore has no additional October change for this fixed selection. This does not mean that all airport or route queries are unchanged: Sprint 6 verified that normalization recovers the remainder of the October cohort for broader endpoint and route analyses.

The airline, hourly and root-cause charts have no airport mapping dependency and were intentionally not copied or changed. Their chart-specific aggregates were also compared directly between the base table and normalized view: the airline chart matched for all 14 airline groups; the hourly chart matched for all 24 hours (and had no groups outside the plotted 0–23 range); and all five rounded root-cause totals matched exactly (late aircraft 416,032 hours, airline 335,622, NAS 189,819, weather 51,431, security 1,350). Sprint 6 separately compared overall delay observation counts and averages, cancellations and diversions and found exact equality with equivalent denominators. No new versions of those unaffected charts were required.

## Generation and validation

- Ran `python python/normalized/airport_heatmap.py` from the project root; it completed and wrote the normalized output.
- Inspected the generated chart. It contains the expected ten labeled airport rows and twelve month columns, with no missing labels or empty values.
- Verified the output is a valid PNG, 3900 × 2100 pixels, with nonzero size (453,744 bytes).
- The script checks required result columns, non-empty results, null airport codes, duplicate airport/month keys, airport membership and month range before plotting.
- No airport/month aggregate keys were duplicated and both queries returned all 120 expected groups.
- Original scripts and images were not overwritten. No database records, schema, SQL files, dashboards or Power BI files were modified.

## Running the normalized chart

From the project root, run:

```powershell
python python\normalized\airport_heatmap.py
```

The command uses the project's existing `.env` configuration through `python/db_connect.py` and writes `assets/normalized/airport_monthly_heatmap.png`.

## Limitations

Only the airport heatmap needed a normalized variant based on the inventory. The fixed ten-airport chart already reflected the October origin values for those airports after the Sprint 5 corrections, so it does not show a new change relative to its current original query. This script does not migrate or regenerate the three unaffected charts. No dashboard or Power BI consumer was changed.

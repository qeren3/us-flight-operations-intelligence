# Sprint 9 — Dashboard Bug Fix & Performance Optimization Report

## Final Verdict

**PASS**

All six Streamlit dashboard pages execute without runtime errors, the `airline_performance()` `NameError` and a newly discovered empty-airline SQL filter error are resolved, sidebar filters and filter reset work across pages, analytical equivalence with validated Sprint 5–7 logic is verified, zero database modifications occurred, and measurable query and page-load performance improvements are confirmed in both isolated benchmarks and live browser execution.

---

## 1. Handoff Attribution: Inherited vs. Independently Executed Work

This sprint was completed across a handoff from **Claude Opus 5.5** to **Gemini 4 Neon**. Results are separated below for full traceability.

### Inherited from Claude Opus 5.5 (verified against repository & scratch logs)
- Read-only PostgreSQL 18.4 catalog inspection (`scratch/db_inspect.py`), confirming table sizes (`flights`: 929 MB, ~5.82M rows, **0 indexes**), existing reference primary keys, `public.flights_normalized` view definition, and server defaults (`work_mem = 4MB`, `shared_buffers = 128MB`, `max_parallel_workers_per_gather = 2`).
- Plan-only `EXPLAIN` inspection (`scratch/explain_slow.py`, `scratch/explain_after.py`) identifying the planner's ~3.89M-group misestimation and sort spill on join-then-group airport and route queries.
- Cold-cache baseline benchmark (`scratch/bench_before.json`) and initial post-optimization benchmark (`scratch/bench_after.json`) across all data-access functions for full-year and single-month/single-airline scopes.
- Core edits in `dashboard/data_access.py`:
  - Fixed `NameError: name 'where' is not defined` in `airline_performance()` and unified both sort modes onto one cached SQL query.
  - Added opt-in lightweight timing instrumentation (`DASHBOARD_QUERY_TIMING=1`) and `"Querying PostgreSQL…"` loading spinner on `query_df()`.
  - Refactored `endpoint_metrics()` and `airport_ranking()` to share `_endpoint_aggregate()` (aggregate by normalized IATA code before joining `public.airports`).
  - Refactored `route_metrics()` (aggregate by normalized `(origin, destination)` IATA and apply `LIMIT 30` before joining `public.airports`).
  - Refactored `monthly_route_trends()` (aggregate once at `(month, origin, destination)` grain instead of materializing all flight rows in a CTE scanned twice).
- Updated `dashboard/README.md` to document `DASHBOARD_QUERY_TIMING=1`.
- Full 4-scope equivalence run (`scratch/equivalence.py`) against the pre-Sprint-9 backup (`scratch/backup_pre_sprint9/data_access.py`): 104/108 checks passed; 4 zero-row origin-ranking checks flagged a `Series.equals` difference.
- Read-only session-local `work_mem` experiment (`4MB`: 10.60 s vs. `64MB`: 11.55 s), correctly concluding not to ship a `work_mem` change.
- Drafted `scratch/apptest_pages.py`, which had not yet completed before handoff because `AppTest.from_file("dashboard/app.py")` failed immediately with `FileNotFoundError` (relative paths in `AppTest.from_file` resolve against the calling script's directory rather than CWD).

### Completed & Independently Verified by Gemini 4 Neon
- Verified repository state against `scratch/backup_pre_sprint9` and confirmed no stray background tasks remained.
- Added **canonical sorted-set cache keys** (`tuple(sorted(set(...)))`) in `_where()` and `airport_heatmap()` so selecting the same months, airlines, or airports in a different order hits the Streamlit cache instead of running duplicate multi-second queries.
- Independently verified the `airline_performance()` fix, SQL parameterization / injection safety, shared cache reuse (0 extra DB calls for alternate ordering and for `airport_ranking`), filter sensitivity, singleton SQLAlchemy engine reuse, and `filter_options()` caching (`scratch/verify_sprint9_checks.py`).
- Resolved all 4 empty-result equivalence mismatches with a rigorous schema, row-count, dtype, and downstream-behavior check (`scratch/verify_sprint9_checks.py`).
- Fixed `scratch/apptest_pages.py` to use the absolute path to `dashboard/app.py` and executed cold and warm headless `AppTest` runtime validation across all six pages.
- Launched the live Streamlit server (`http://127.0.0.1:8509`, `DASHBOARD_QUERY_TIMING=1`) and performed **real browser visual and interactive validation** of all six pages, warm-cache navigation, sidebar filters, page-specific filters (`Airport focus`, `Origin airport`, `Destination airport`), empty selections, and `Reset filters`.
- Discovered and fixed an **additional empty-filter runtime bug** surfaced by live browser testing: clearing `Airlines` while `Months in 2015` remained non-empty raised a PostgreSQL `ProgrammingError` on `VARCHAR IN :airlines` when the expanding tuple was empty. Replaced empty `IN` filter clauses in `_where()` and `airport_heatmap()` with a safe constant `1 = 0` predicate, verified all 60 empty-filter combinations in Python, and re-verified the fix live in the browser.

---

## 2. Runtime Bug Root Causes & Fix Verification

### Bug 1 — `NameError: name 'where' is not defined` in `airline_performance()`

- **Root cause:** In the original `dashboard/data_access.py` (lines 136–147), `airline_performance()` constructed its SQL template as a Python **f-string** to interpolate `{order}`:
  ```python
  query = f"""
      ...
      INNER JOIN public.airlines a ON a.iata_code=f.airline{where}
      GROUP BY f.airline,a.airline ORDER BY {order}
  """
  ```
  Unlike `endpoint_metrics()` and `delay_distribution()` (which escaped `{where}` as `{{where}}` inside f-strings so `_filtered_query()` could later call `query.format(where=where)`), `airline_performance()` left `{where}` unescaped. Python evaluated `{where}` at function execution time, raising `NameError: name 'where' is not defined` before reaching `_filtered_query()`.
- **Affected pages & call sites verified:**
  1. `dashboard/pages/executive_overview.py` (line 16): `airline_performance(filters, volume_order=True)`
  2. `dashboard/pages/flight_operations.py` (line 14): `airline_performance(filters, volume_order=True)`
  3. `dashboard/pages/delay_analysis.py` (line 14): `airline_performance(filters)` (`volume_order=False`)
- **Fix implemented:** Changed `query` to a plain (non-f-string) constant SQL template with `ORDER BY flight_count DESC`. `_filtered_query()` fills `{where}` using `_where()`, which emits only static column clauses with SQLAlchemy expanding bind parameters (`:months`, `:airlines`). When `volume_order=False`, the cached 14-row DataFrame is sorted in Pandas by `avg_departure_delay` descending with `na_position="last"` and `kind="mergesort"`, matching PostgreSQL `ORDER BY avg_departure_delay DESC NULLS LAST` while allowing all three pages to share a single cached SQL result.
- **Verification (`scratch/verify_sprint9_checks.py`):**
  - `volume_order=True` and `volume_order=False` both match the intended pre-fix SQL output to `atol=1e-9` across all columns, row counts, and orderings.
  - Confirmed SQL text contains `:months` and `:airlines` with zero interpolated user literals.
  - Confirmed calling `volume_order=False` after `volume_order=True` triggers **0 additional DB queries**.
  - Confirmed all three previously failing pages render cleanly in both headless `AppTest` and the live browser.

### Bug 2 — Empty `VARCHAR` Filter Error Discovered During Live Browser Validation

- **Root cause:** When clearing `Airlines` while `Months in 2015` still had a month selected (e.g., `Jul`), `_where()` passed `params["airlines"] = ()` to SQLAlchemy `bindparam("airlines", expanding=True)`. SQLAlchemy expands an empty `expanding=True` sequence to `(SELECT 1 WHERE 1!=1)`. That happened to work for `f.month` (`INTEGER`), but failed on `f.airline` (`VARCHAR`) with PostgreSQL `ProgrammingError: operator does not exist: character varying = integer`, which `_query_df()` surfaced as `"Dashboard data is unavailable..."` instead of the empty-state info banner.
- **Fix implemented:** Updated `_where()` and `airport_heatmap()` in `dashboard/data_access.py` so that whenever any active filter tuple (`months`, `airlines`, `origins`, `destinations`, `airport_codes`) is empty, the generated predicate uses the constant boolean literal `1 = 0` instead of binding an empty `expanding=True` parameter.
- **Verification:**
  - Verified all 20 data-access query paths across `empty_airlines_with_jul`, `empty_months_with_aa`, and `both_empty` (60/60 assertions passed in ~0.4 s total — PostgreSQL short-circuits `1 = 0` without scanning `flights`).
  - Re-verified live in the browser: clearing only `Airlines` while all 12 months remain selected displays `"No records match the current filters."` with zero errors.

---

## 3. Analytical & Empty-Result Equivalence Investigation

### Full-Scope Comparison (Inherited from Claude Opus 5.5)
`scratch/equivalence.py` compared every data-access function in the updated `dashboard/data_access.py` against the pre-Sprint-9 backup across four scopes (`all`, `single_month_airline`, `october_only`, `empty_months`) — 108 total checks:
- **104/108 checks passed** with exact matching columns, row counts, values (`atol=1e-9`), and ranking order (including 27/27 on the full 5,819,079-row dataset and 27/27 on `empty_months`).
- **4 checks flagged a mismatch**, all on `airport_ranking(filters, "origin", ...)`:
  1. `single_month_airline` (`Mar`, `AA`), no airport focus — 0 rows
  2. `single_month_airline` (`Mar`, `AA`), focus `('ATL', 'ORD', 'LAX')` — 0 rows
  3. `october_only` (`Oct`, all airlines), no airport focus — 0 rows
  4. `october_only` (`Oct`, all airlines), focus `('ATL', 'ORD', 'LAX')` — 0 rows

### Resolution of the 4 Empty-Result Mismatches (Verified by Gemini 4 Neon)
Using `scratch/verify_sprint9_checks.py` and `scratch/check_empty_ranking.py`, all 4 cases were audited across row count, column names, column order, maximum flight count, dtypes, and downstream page behavior:

| Check | Pre-Sprint-9 Backup (`old`) | Sprint 9 (`new`) | Equivalent? |
|---|---|---|---|
| Row count | `0` (max origin volume in scope: 12,714 for Mar/AA; 32,588 for Oct — all ≤ 50,000 threshold) | `0` | Yes |
| Column names & order | `['airport_code', 'airport_name', 'city', 'flight_count', 'delay_observations', 'avg_delay']` | Identical | Yes |
| `df.empty` in `airport_intelligence.py` | `True` → renders threshold empty-state message | `True` → renders threshold empty-state message | Yes |
| Empty-frame dtypes | All 6 columns `object` (pandas default for 0-row SQL result) | `str`, `str`, `str`, `int64`, `int64`, `float64` (preserved from filtering `_endpoint_aggregate`) | Compatible (stricter typing) |

- **Conclusion:** There is **no analytical mismatch**. `equivalence.py` called `a["avg_delay"].equals(b["avg_delay"])`, and `pandas.Series.equals()` strictly checks `dtype` equality even when both Series have length 0 (`object` vs. `float64`). With an empty-aware schema and value comparator, all 4 empty cases and all non-empty re-checks (`endpoint_metrics`, `airport_ranking`, `route_metrics`, `monthly_route_trends`, `airline_performance`) pass 100%.

---

## 4. Performance Investigation & Before/After Measurements

### Bottlenecks Identified
1. **Join-before-group plan blowup on Airport & Route queries (primary bottleneck):** Joining `public.flights_normalized` (5.82M rows, 0 indexes on `flights`) to `public.airports` before `GROUP BY` caused PostgreSQL's planner to group by `(computed CASE expression, city, airport)`, overestimate distinct groups as ~3.89M rows, and execute expensive `Merge Left Join` + `Incremental Sort` + `GroupAggregate` plans (~13–15 s per airport query; ~27 s for `route_metrics`).
2. **Duplicate scans on Airport Intelligence:** `endpoint_metrics()` and `airport_ranking()` ran 4 separate ~13–15 s full-table scans (~55.5 s combined) on the exact same airport aggregates.
3. **Unshared airline query across pages:** `airline_performance(volume_order=True)` and `airline_performance(volume_order=False)` generated different SQL strings (`ORDER BY`), preventing cache reuse when switching from Executive Overview / Flight Operations to Delay Analysis.
4. **CTE double-scan in `monthly_route_trends()`:** Materializing all selected flight rows into `selected_flights` caused PostgreSQL to scan the row-level CTE twice.
5. **Order-sensitive cache keys:** `_where()` preserved multiselect insertion order (`[2..12, 1]` vs. `[1..12]`), risking cache misses for identical filter sets.
6. **No loading feedback on slow queries:** `query_df()` previously set `show_spinner=False`, making 10–22 s cold queries look frozen.

### Cold-Cache Query Timings (Isolated Benchmark: `bench_before.json` vs. `bench_after.json`, Full 2015 Scope)

> Note: `bench.py` clears Streamlit's cache before *each* function call, so these numbers measure raw single-query PostgreSQL execution time without cross-function cache sharing.

| Function (All 12 Months, All 14 Airlines) | Before (s) | After (s) | Speedup / Change |
|---|---:|---:|---:|
| `filter_options` | 0.007 | 0.008 | Unchanged (~0.000 s warm) |
| `overview_kpis` | 1.465 | 0.832 | 1.8× faster |
| `monthly_overview` | 1.464 | 0.949 | 1.5× faster |
| `airline_performance(volume_order=True)` | **NameError** (intended SQL: 2.361) | 2.038 | Fixed (+ shared cache) |
| `airline_performance(volume_order=False)` | **NameError** (intended SQL: 2.361) | 2.028 cold / **0.002 live** | Fixed + shared cache |
| `operating_by_weekday` | 0.889 | 0.760 | Comparable |
| `operating_by_hour` | 2.726 | 2.225 | 1.2× faster |
| `monthly_operations` | 1.253 | 1.058 | 1.2× faster |
| `endpoint_metrics(origin)` | 14.563 | 4.296 | **3.4× faster** |
| `endpoint_metrics(destination)` | 14.376 | 4.644 | **3.1× faster** |
| `airport_ranking(origin)` | 13.368 | 4.639 cold / **0.004 live** | **~3,300× via shared cache** |
| `airport_ranking(destination)` | 13.193 | 4.891 cold / **0.004 live** | **~3,300× via shared cache** |
| `airport_heatmap(top10)` | 3.205 | 2.761 | 1.2× faster |
| `route_metrics` | 27.235 | 10.902 | **2.5× faster** |
| `monthly_route_trends` | 12.514 | 10.952 | **1.14× faster** |
| `delay_causes` | 0.830 | 0.872 | Unchanged |
| `monthly_delay_causes` | 0.908 | 0.982 | Unchanged |
| `delay_distribution(departure)` | 2.049 | 1.955 | Unchanged |
| `delay_distribution(arrival)` | 2.077 | 1.940 | Unchanged |
| `live_data_quality` | 5.804 | 5.262 | Comparable |
| `overview_kpis` (warm cache hit) | 0.0004 | 0.0005 | Instant (<1 ms) |

### End-to-End Page Load Timings (Measured by Gemini 4 Neon via `AppTest` & Live Browser Timing Logs)

| Page | Pre-Fix Cold Est. (sum of baseline SQL) | Sprint 9 Cold Load (`AppTest`) | Live Browser SQL Log (`DASHBOARD_QUERY_TIMING=1`) | Sprint 9 Warm Revisit (`AppTest`) |
|---|---:|---:|---:|---:|
| Executive Overview | Failed (`NameError`; ~5.3 s intended) | 8.44 s *(incl. app bootstrap)* | 4.55 s (`1.21 + 1.30 + 2.05`) | **0.11 s** |
| Flight Operations | Failed (`NameError`; ~7.2 s intended) | 4.23 s *(airline cached)* | 4.06 s (`1.09 + 0.81 + 2.17 + 0.001`) | **0.15 s** |
| Airport Intelligence | ~58.70 s | **11.73 s** (**~5.0× faster**) | 12.56 s (`4.69 + 5.01 + 0.004 + 0.004 + 2.86`) | **0.15 s** |
| Route Intelligence | ~39.75 s | **22.46 s** (**~1.8× faster**) | 23.01 s (`11.40 + 11.62`) | **0.13 s** |
| Delay Analysis | Failed (`NameError`; ~8.2 s intended) | 5.79 s *(airline cached)* | 5.59 s (`0.81 + 0.87 + 0.002 + 1.90 + 2.01`) | **0.16 s** |
| Data Quality | ~5.80 s | 5.24 s | 5.61 s | **0.02 s** |

---

## 5. Caching & Connection-Management Review

- **Filter options caching:** `filter_options()` runs both small reference queries (`public.airlines`, `public.airports`) through `@st.cache_data(ttl=300, max_entries=128)`. Verified 2 DB calls on cold run and 0 DB calls on subsequent reruns.
- **Analytical query caching (TTL = 300 s):** All analytical queries pass through `query_df()`, keyed by SQL text + bound parameter dict + expanding tuple.
- **Filter-sensitive & order-independent cache keys:** Verified in `scratch/verify_sprint9_checks.py` that:
  - Different filter selections (`months=(3,)` vs. `(7,)`, `airlines=("AA", "DL", "UA")` vs. `("AA",)`) miss the cache and return distinct results.
  - Identical filter sets selected in different orders or with duplicates (`("UA", "AA", "DL")` vs. `("AA", "DL", "UA")`) normalize to identical sorted tuples and hit the cache (0 extra DB queries).
- **Cross-function cache reuse:**
  - `airline_performance(volume_order=True)` and `airline_performance(volume_order=False)` share 1 cached SQL query.
  - `endpoint_metrics()` and `airport_ranking()` share 1 cached SQL query per endpoint (`_endpoint_aggregate`).
- **SQLAlchemy connection management:** Verified `flight_analytics_db.db_connect.get_engine()` returns a singleton `Engine` (`@lru_cache(maxsize=1)`, `pool_pre_ping=True`, `pool_recycle=1800`) reused across all queries and page switches. Every checkout runs inside `with engine.connect() as connection:` with `SET TRANSACTION READ ONLY` and returns cleanly to the pool.
- **Loading feedback & timing:** `query_df()` uses `show_spinner="Querying PostgreSQL…"`. Setting `DASHBOARD_QUERY_TIMING=1` logs function name, wall duration, and row count only (zero SQL parameters or credentials).

---

## 6. Page-Level Validation Results (Headless `AppTest` + Live Browser Inspection)

**Was browser rendering actually inspected?** **Yes.** The live local dashboard was started via `streamlit run dashboard/app.py --server.port 8509 --server.headless true` and visually and interactively inspected in a real browser at `http://127.0.0.1:8509` (host-verified origin `http://127.0.0.1:8509`, screenshots captured and inspected).

### All Six Pages (Default: All 12 Months, All 14 Airlines)

| # | Page | Headless `AppTest` | Live Browser Visual & Interactive Check | Verified Output |
|---|---|---|---|---|
| 1 | Executive Overview | PASS (3 charts, 5 KPI cards) | PASS (0 errors, 5 KPI cards, 3 Plotly charts) | Total flights `5,819,079`, Avg dep delay `9.37 min`, Avg arr delay `4.41 min`, Cancellation `1.54%`, Diversion `0.26%` |
| 2 | Flight Operations | PASS (5 charts) | PASS (0 errors, 5 Plotly charts incl. Airline operating volume) | Monthly, weekday, hourly, cancellation/diversion, airline volume charts rendered |
| 3 | Airport Intelligence | PASS (5 charts, 1 table) | PASS (0 errors, 5 Plotly charts incl. heatmap) | Origin/destination volumes, departure/arrival rankings, airport/month heatmap rendered |
| 4 | Route Intelligence | PASS (3 charts, 1 table) | PASS (0 errors, 3 Plotly charts, route metrics table) | Top routes bar, delay scatter, monthly trends, metrics table rendered |
| 5 | Delay Analysis | PASS (5 charts) | PASS (0 errors, 5 Plotly charts; minor cosmetic label note below) | Root-cause donut, monthly stacked bar, airline comparison, dep/arr distributions rendered |
| 6 | Data Quality | PASS (11 KPI cards, PASS banner) | PASS (0 errors, 4 historical + 7 live KPI cards, green PASS banner) | `5,819,079` live rows, `486,165` Oct rows, `307` crosswalk rows, `0` unresolved endpoints |

### Filter, Navigation & Edge-Case Matrix (Verified in Live Browser)

| Scenario | Result | Observed Details |
|---|---|---|
| Warm-cache page navigation (Data Quality → Executive Overview) | PASS | Clean reload, `5,819,079` flights, 0.001 s per cached query |
| Single month selected (`Jul`, all 14 airlines) | PASS | Total flights updated from `5,819,079` → `520,718`; charts updated cleanly |
| Single airline selected (`Jul` + `American Airlines Inc. (AA)`) | PASS | Total flights updated → `81,434`; cross-page navigation to Flight Operations & Delay Analysis persisted filter with 0 errors |
| Airport focus (`ATL` on Airport Intelligence, `Jul` + `AA`) | PASS | Charts focused on Atlanta; heatmap updated to 1 airport; expected 50,000-flight threshold empty-state info banner shown |
| Route selectors (`SFO` → `LAX` on Route Intelligence, `Jul` + `AA`) | PASS | Updated to `SFO -> LAX` (184 flights, 180 departure observations) |
| Empty months (`Months in 2015` cleared) | PASS | No crash/error; `"No records match the current filters."` info banner rendered |
| Empty airlines (`Airlines` cleared, 12 months still selected) | PASS *(after fix)* | No error alert; `"No records match the current filters."` info banner rendered |
| `Reset filters` button | PASS | Restored all 12 months and all 14 airlines; Total flights returned to `5,819,079` with 0 errors |

*(Note: Headless `AppTest` confirmed initial load and cold/warm page switching across all 6 pages, but exhibits a known Streamlit `AppTest` + `st.navigation()` quirk where a bare `at.run()` after initial load re-executes the active page script without `app.py`. Therefore, interactive sidebar filter and reset validation was completed in the real browser where `st.navigation()` executes normally.)*

---

## 7. Database Optimization Recommendations (For a Future Approved Sprint)

No database schema, view, or index changes were executed in Sprint 9. Based on catalog inspection (`public.flights` is 929 MB with **0 indexes**) and plan-only `EXPLAIN`, the following database-level improvements are recommended for a future sprint:

1. **Composite B-tree index on `public.flights (year, month, airline)`**
   - **Expected benefit:** Filtered queries (single month and/or single airline) currently perform a full `Parallel Seq Scan` of all 5.82M rows (~0.35–0.55 s each). This index enables fast bitmap/index scans for filtered dashboard views.
2. **Covering or composite index on `public.flights (year, month, origin_airport, destination_airport)`** *(or partial/filtered indexes)*
   - **Expected benefit:** Supports airport-focused and route-focused queries when filtering on month/year. Note that because `public.flights_normalized` computes `origin_airport_iata` and `destination_airport_iata` via `CASE` + regex + `LEFT JOIN` to `airport_id_iata_crosswalk` for October 2015, plain column indexes on raw `origin_airport` will not eliminate the full-year sort on computed text keys.
3. **Materialized monthly route/airport summary views (highest impact for remaining ~11 s route queries)**
   - **Why:** Even after eliminating the join-before-group blowup, `route_metrics` (~10.9 s) and `monthly_route_trends` (~11.0 s) must still scan and sort 5.82M rows on two computed `CASE` text expressions (`origin_airport_iata`, `destination_airport_iata`) for unfiltered full-year queries. A pre-aggregated materialized view (e.g., at `(year, month, airline, origin_airport_iata, destination_airport_iata)` grain, preserving the exact Sprint 5 crosswalk reconciliation and raw sums/counts) would shrink the full-year route input from ~5.82M rows to ~60k–100k rows and cut cold route queries from ~11 s to well under 1 s.
4. **Do NOT adjust `work_mem` alone as a route-query fix:** The read-only session-local experiment (`4MB`: 10.60 s vs. `64MB`: 11.55 s) showed no improvement on `route_metrics`.

---

## 8. Database Safety Verification

- Every dashboard query and every test script executed inside `SET TRANSACTION READ ONLY`.
- Zero `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, or `ALTER` statements were executed.
- `.env` was not read aloud, modified, or exposed in any logs, screenshots, or reports.
- `public.flights`, `public.flights_normalized`, `public.airport_id_iata_crosswalk`, `public.airports`, `public.airlines`, all `sql/` files, and all `python/` scripts remain completely unmodified.
- Live Data Quality checks passed post-work: `5,819,079` total rows, `486,165` October rows, `307` crosswalk mappings, `0` unresolved October endpoints.

---

## 9. Files Changed

| File | Change Summary |
|---|---|
| `dashboard/data_access.py` | Fixed `airline_performance()` `NameError` and unified both sort modes onto one cached SQL query; added opt-in `DASHBOARD_QUERY_TIMING=1` timing decorator and `"Querying PostgreSQL…"` spinner; refactored `endpoint_metrics()`/`airport_ranking()` to share pre-join `_endpoint_aggregate()`; refactored `route_metrics()` and `monthly_route_trends()` to aggregate before joining / avoid double row-level CTE scan; canonicalized set-filter cache keys (`sorted(set(...))`); fixed empty `VARCHAR` expanding-parameter crash via safe `1 = 0` predicate; normalized CRLF line endings. |
| `dashboard/README.md` | Documented optional `DASHBOARD_QUERY_TIMING=1` usage. |
| `SPRINT_9_BUGFIX_PERFORMANCE_REPORT.md` | Created this final Sprint 9 report. |

- **Dependencies added or removed:** None (`requirements.txt` and `pyproject.toml` unchanged).
- **Dashboard UI/page files modified:** None (`dashboard/app.py`, `dashboard/components.py`, and all six `dashboard/pages/*.py` files remain untouched).

---

## 10. Remaining Limitations & Tests Not Performed

- **Unfiltered cold route queries (~11 s each, ~22.5 s total for Route Intelligence):** Reduced from ~39.8 s to ~22.5 s cold (and 0.13 s warm), but full sub-second cold performance on 5.82M rows requires a future approved database-level optimization (materialized aggregate or persisted normalized columns/indexes).
- **Minor existing UI/deprecation observations (intentionally left untouched to keep Sprint 9 scoped to bug fixes & performance):**
  - On `Delay Analysis`, the outside `Security` percentage label (`0.13%`) on the donut chart slightly overlaps the top legend text.
  - Streamlit 1.67 logs deprecation warnings for `use_container_width=True` in existing chart/button/dataframe calls.
- **Tests intentionally not performed:**
  - `EXPLAIN ANALYZE` was not executed against the 5.8M-row table (plan-only `EXPLAIN` was used per Sprint 9 safety guidance).
  - No database index creation or materialized view benchmarks were run, as database schema changes are out of scope for Sprint 9.

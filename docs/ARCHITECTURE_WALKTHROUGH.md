# Technical Architecture Walkthrough — US Flight Operations Intelligence

This document explains the system architecture, key data engineering decisions, query-plan optimizations, security boundaries, and frontend state patterns behind **US Flight Operations Intelligence**.

---

## 1. System Overview & Layer Boundaries

The platform separates concerns cleanly across four layers so analytical SQL correctness is decoupled from UI presentation:

1. **PostgreSQL Storage & Normalization Layer (`sql/`)**
   - Base tables: `public.flights` (5,819,079 rows, 929 MB), `public.airports` (322 rows), `public.airlines` (14 rows), and `public.airport_id_iata_crosswalk` (307 rows).
   - Normalization layer: `public.flights_normalized`, a non-destructive SQL view exposing `origin_airport_iata`, `destination_airport_iata`, `origin_airport_mapping_status`, and `destination_airport_mapping_status`.
2. **Database Connectivity Layer (`python/db_connect.py`, installed as `flight_analytics_db`)**
   - Loads `.env` once via `python-dotenv` (with process environment variables taking precedence).
   - Exposes a process-wide singleton SQLAlchemy `Engine` via `@lru_cache(maxsize=1)` configured with `pool_pre_ping=True` and `pool_recycle=1800`.
3. **Read-Only Data Access & Caching Layer (`dashboard/data_access.py`)**
   - Every query runs inside `SET TRANSACTION READ ONLY` via SQLAlchemy `text()` + `bindparam(..., expanding=True)`.
   - Heavy aggregations run exclusively inside PostgreSQL; Pandas receives small pre-aggregated DataFrames (1–322 rows per query) rather than raw flight rows.
   - Results are cached for 300 seconds via `@st.cache_data(ttl=300, max_entries=128)`.
4. **Presentation, Localization & Navigation Layer (`dashboard/app.py`, `components.py`, `i18n.py`, `pages/*.py`)**
   - Multipage navigation via `st.navigation()` with stable language-independent `url_path` slugs.
   - Centralized English/Turkish dictionary (`219` keys × 2 languages) and unified Plotly dark-navy theme + `build_hover()` tooltip builder.

---

## 2. Key Data Engineering Decision: Non-Destructive Airport Reconciliation

### The Problem
During Sprint 2–3 auditing, raw queries joining `public.flights` to `public.airports` dropped **486,165 flights** — 100% of October 2015 — because the upstream BTS feed temporarily emitted **numeric DOT Airport IDs** (e.g., `10397`, `13930`) instead of 3-letter IATA codes (`ATL`, `ORD`) for that single month.

### Why a View Instead of Mutating `public.flights`?
Two options existed: run an `UPDATE` on `public.flights` in place, or introduce a reference crosswalk + view. We chose the **non-destructive view** (`public.flights_normalized`) because:

- **Auditability & Reproducibility:** Raw source columns (`origin_airport`, `destination_airport`) stay untouched alongside the resolved IATA columns (`origin_airport_iata`, `destination_airport_iata`) and explicit lineage statuses (`mapped_from_dot_id`, `existing_iata`, `passed_through`, `unresolved`).
- **Scoped Precision:** The crosswalk join is constrained strictly to `f.year = 2015 AND f.month = 10` and `source_dataset_month = DATE '2015-10-01'`, preventing unintended cross-month collisions.
- **Continuous Live Verification:** The **Data Quality** dashboard page runs live SQL checks directly against `public.flights_normalized` and `public.airport_id_iata_crosswalk`, confirming `5,819,079` total rows, `486,165` October rows, `307` distinct IDs & sequences, and `0` unresolved endpoints.

---

## 3. Security & Read-Only Safety Architecture

- **Zero Hardcoded Credentials:** Database settings are read strictly from environment variables / local `.env` via `flight_analytics_db.db_connect._database_url()`.
- **Sanitized Error Boundary:** `_query_df()` catches driver exceptions, logs only `type(exc).__name__` (never raw driver error strings that can embed host/user details), and raises `DashboardDataError` with a generic localized UI message.
- **Read-Only Transaction Guard:** Every checkout executes `connection.exec_driver_sql("SET TRANSACTION READ ONLY")` before executing SQL, enforcing read-only behavior at the database session level.
- **SQL Injection Prevention:** Dynamic `WHERE` clauses in `_where()` only emit hardcoded column templates (`f.month IN :months`, `f.airline IN :airlines`, etc.) paired with bound parameters. When any filter set is empty, `_where()` emits the constant SQL boolean `1 = 0` — which both prevents SQLAlchemy's empty `expanding=True` PostgreSQL `VARCHAR = INTEGER` type error and lets PostgreSQL short-circuit without scanning the table.
- **Localhost-Only Binding:** `.streamlit/config.toml` binds `address = "127.0.0.1"` and disables usage telemetry (`gatherUsageStats = false`).

---

## 4. Performance Engineering Decisions (Sprint 9)

### Root Cause of Slow Airport & Route Pages
Plan-only `EXPLAIN` against PostgreSQL 18.4 revealed that the initial airport and route queries joined `public.flights_normalized` to `public.airports` *before* `GROUP BY (computed_case_expr, city, airport)`. Because PostgreSQL cannot easily estimate distinct counts across `CASE` + regex expressions combined with extra columns from a joined table, the planner estimated ~3.89 million distinct groups and chose expensive `Merge Left Join` + `Incremental Sort` + `GroupAggregate` plans (~14 s per airport query, ~27 s for `route_metrics`).

### Evidence-Based Optimizations Implemented
1. **Aggregate Before Joining (`_endpoint_aggregate`, `route_metrics`):** Because `public.airports.iata_code` is a `PRIMARY KEY` (unique), aggregating by normalized IATA code first and joining the 322-row `public.airports` table afterward produces **mathematically identical groups, counts, averages, and labels** while reducing `endpoint_metrics` from `14.56 s → 4.30 s` and `route_metrics` from `27.24 s → 10.90 s`.
2. **Eliminate Redundant Full-Table Scans:**
   - `endpoint_metrics()` and `airport_ranking()` share `_endpoint_aggregate()`. On **Airport Intelligence**, ranking queries drop from `13.3 s` each to `0.004 s` cache hits, cutting cold page load from **~58.7 s → 11.7 s** (~5× faster).
   - `airline_performance(volume_order=True)` and `airline_performance(volume_order=False)` share one cached SQL query and sort the 14-row result in Pandas (`mergesort`, `na_position="last"`), saving a full ~2 s scan when navigating between Executive Overview, Flight Operations, and Delay Analysis.
3. **Eliminate Row-Level CTE Double Scan (`monthly_route_trends`):** Replaced a row-level `selected_flights` CTE scanned twice with a single `(month, origin_iata, destination_iata)` aggregation CTE, computing top-10 route totals via `SUM(flight_count)`.
4. **Canonical Set-Filter Cache Keys:** `_where()` and `airport_heatmap()` normalize set filters via `tuple(sorted(set(...)))` so selecting the same months, carriers, or airports in a different order always hits the existing cache entry.
5. **What Was Tested & Rejected:** A read-only session-local `work_mem` test (`4MB`: `10.60 s` vs. `64MB`: `11.55 s`) showed no speedup on `route_metrics` because the dominant cost is scanning and sorting computed view text keys over 5.82M rows. No `work_mem` override was shipped.

---

## 5. Frontend Architecture: TR/EN Localization & Widget State Persistence (Sprint 10)

### Centralized Localization (`dashboard/i18n.py`)
- Single source of truth with **219 English keys and 219 Turkish keys**, verified programmatically for 100% key and format-placeholder parity.
- Turkish-aware uppercase helper (`upper_localized()`) preserves dotted `İ` (`Havalimanı` → `HAVALİMANI`) inside Plotly tooltip headers and donut annotations.

### Solving Streamlit's `format_func` Language-Switch Edge Case
In Streamlit, when a `st.multiselect` or `st.selectbox` uses a `format_func` whose output labels change across languages (`Jan..Dec` vs. `Oca..Ara`, or `All Origins` vs. `Tüm Kalkışlar`), keeping the same widget key across a language switch can cause Streamlit's frontend state reconciliation to drop options whose formatted strings no longer match.

`dashboard/app.py` solves this cleanly with two patterns:
1. **Canonical Language-Independent Stores:** Raw filter values (`list[int]` for months, IATA codes for airlines/airports, canonical sentinels `"Any origin"` / `"Any destination"`) live in dedicated session-state stores (`dashboard_months_store`, `dashboard_origin_store`, `dashboard_destination_store`).
2. **Generation-Keyed Language Widgets:** `set_lang()` increments `dashboard_lang_gen`, mounting a fresh widget key (`dashboard_months_{lang}_{lang_gen}`) seeded directly from the canonical store. Combined with stable `url_path` slugs on `st.Page()`, switching **`TR | EN`** preserves the active page and every filter reliably across reruns and filter resets.

### Consistent Plotly Visualization System (`dashboard/components.py`)
- `build_hover()` enforces uniform dark elevated tooltips across all 21 charts, preventing cramped default Plotly Express labels and ensuring `<extra></extra>` suppresses redundant secondary trace tags.
- `kpi_grid()` renders responsive CSS Grid cards (`repeat(auto-fit, minmax(205px, 1fr))`) with `tabular-nums` and `white-space: nowrap` values, eliminating narrow-column mid-word wrapping across desktop (`1440×900`) and laptop (`1024×768`) viewports.

---

## 6. Future Database Scaling Blueprint (Not Yet Applied)

All Sprint 1–11 work kept the PostgreSQL schema read-only after Sprint 5 reconciliation. For a future approved database optimization sprint, the highest-leverage improvements based on `EXPLAIN` evidence are:

1. **Composite Index on Filtered Dimensions:**
   ```sql
   CREATE INDEX idx_flights_year_month_airline
       ON public.flights (year, month, airline);
   ```
   Accelerates single-month and single-carrier slices from full 5.82M-row sequential scans (~0.4 s) to indexed scans.
2. **Materialized Monthly Corridor Aggregate View:**
   Pre-aggregate `(year, month, airline, origin_airport_iata, destination_airport_iata)` with exact `COUNT(*)`, `COUNT(delay)`, and `SUM(delay)` columns derived from `public.flights_normalized`. This shrinks full-year route input from ~5.82M rows to ~60k–100k rows and reduces cold **Route Intelligence** queries from ~11 s to well under 1 second while preserving 100% KPI parity.

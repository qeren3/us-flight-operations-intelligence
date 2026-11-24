# US Flight Operations Intelligence

A local, read-only Streamlit dashboard for the project's 2015 flight dataset. It uses the normalized airport view, aggregates in PostgreSQL, and renders interactive Plotly charts. It does not download all flight rows into the browser and is configured to bind only to `127.0.0.1`.

## Run locally

From the project root in PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
streamlit run dashboard/app.py
```

Open the local address printed by Streamlit. The editable install registers the `dashboard` and `flight_analytics_db` packages so Streamlit can import them consistently while rerunning page scripts. The project root `.env` is loaded through the shared `flight_analytics_db.db_connect` helper. Do not copy credentials into dashboard files. Use the Data Quality page to compare live database checks with the historical Sprint 5 audit.

## Pages

- **Executive Overview** — flight totals, delay averages, cancellation/diversion rates, monthly volume and trends, and airline performance.
- **Flight Operations** — monthly and source day-of-week volumes, scheduled-hour performance, cancellation/diversion trends, and airline volumes.
- **Airport Intelligence** — origin and destination volumes, airport delay rankings, and an interactive airport/month heatmap based on normalized IATA codes.
- **Route Intelligence** — route volume and delay comparisons, normalized origin/destination selectors, and monthly route trends.
- **Delay Analysis** — root-cause breakdown and trends, airline delay comparisons, and departure/arrival delay distributions.
- **Data Quality** — historical reconciliation audit values beside live row counts, endpoint coverage, unresolved endpoints, and crosswalk integrity checks.

## Filters and calculation notes

Month and airline filters appear on analytical pages and affect that page's SQL results. Airport focus appears on Airport Intelligence and filters its origin/destination metrics, rankings, and heatmap. Origin and destination selectors appear on Route Intelligence and filter route tables and charts; monthly trends show the ten highest-volume matching routes across the selected period. Data Quality has no analytical filters because its checks are fixed to the validated 2015 cohort.

The dataset covers 2015 only. Flight counts include every matching flight row. Cancellation and diversion rates use all matching flights as the denominator. Delay averages use SQL `AVG`, which ignores NULL delay observations without filtering on cancellation or diversion status. The root-cause page preserves the original definition: sum each cause field in hours (`SUM(cause_delay)/60`) only for rows where `departure_delay > 0`; SQL `SUM` ignores NULL cause values. Root-cause donut percentages are shares of the five displayed cause totals. Delay distributions include all non-NULL delay observations, including any non-NULL delays attached to cancelled or diverted rows.

Query results use a five-minute Streamlit cache. Reset Filters restores all months and all airline choices. The dashboard uses read-only SQL transactions and displays sanitized database error messages.

## Query timing (optional)

To log how long each data-access call takes (function name, seconds, row count only — no SQL parameters or connection details), start the app with:

```powershell
$env:DASHBOARD_QUERY_TIMING = "1"; streamlit run dashboard/app.py
```

Cache hits appear as near-zero durations.

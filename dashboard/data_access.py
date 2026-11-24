import functools
import logging
import os
import time
from typing import Any, Callable, Mapping, Sequence, TypeVar

import pandas as pd
import streamlit as st
from sqlalchemy import bindparam, text

from flight_analytics_db.db_connect import get_engine

logger = logging.getLogger(__name__)

# Opt-in query timing: set DASHBOARD_QUERY_TIMING=1 before `streamlit run` to log one line
# per data-access call (function name, elapsed seconds, row count). Only names, durations
# and row counts are logged -- never SQL parameters or connection details.
_TIMING_ENABLED = os.getenv("DASHBOARD_QUERY_TIMING", "").strip().lower() in {"1", "true", "yes"}
if _TIMING_ENABLED and not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s dashboard-timing %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

_F = TypeVar("_F", bound=Callable[..., pd.DataFrame])


def _timed(func: _F) -> _F:
    """Log wall time of a data-access call when timing is enabled (cache hits show ~0s)."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
        if not _TIMING_ENABLED:
            return func(*args, **kwargs)
        started = time.perf_counter()
        result = func(*args, **kwargs)
        rows = len(result) if hasattr(result, "__len__") else "-"
        logger.info("%s %.3fs rows=%s", func.__name__, time.perf_counter() - started, rows)
        return result
    return wrapper  # type: ignore[return-value]


class DashboardDataError(RuntimeError):
    """Safe, user-facing database error with no connection details."""


def _query_df(query: str, params: Mapping[str, Any] | None = None,
              expanding: Sequence[str] = ()) -> pd.DataFrame:
    values = dict(params or {})
    statement = text(query)
    if expanding:
        statement = statement.bindparams(*(bindparam(name, expanding=True) for name in expanding))
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            return pd.read_sql_query(statement, connection, params=values)
    except Exception as exc:
        # Log only the exception class; driver messages can contain connection details.
        logger.warning("Dashboard data query failed (%s)", type(exc).__name__)
        raise DashboardDataError(
            "Dashboard data is unavailable. Check that local PostgreSQL is running and the project configuration is valid."
        ) from None


@st.cache_data(ttl=300, max_entries=128, show_spinner=False)
def query_df(query: str, params: Mapping[str, Any] | None = None,
             expanding: tuple[str, ...] = ()) -> pd.DataFrame:
    """Execute and cache a read-only, parameterized SQL aggregate for five minutes.

    The cache key is the full SQL text plus every bound parameter value, so each distinct
    filter selection (months, airlines, airports) gets its own cache entry.
    """
    return _query_df(query, params, expanding)


def _where(filters: Mapping[str, Any], alias: str = "f", *, include_months: bool = True,
           include_airlines: bool = True, origin_codes: tuple[str, ...] | None = None,
           destination_codes: tuple[str, ...] | None = None,
           airport_codes: tuple[str, ...] | None = None) -> tuple[str, dict[str, Any], tuple[str, ...]]:
    clauses = [f"{alias}.year = 2015"]
    params: dict[str, Any] = {}
    expanding: list[str] = []
    if include_months:
        months = tuple(sorted(set(filters.get("months", ()))))
        if months:
            clauses.append(f"{alias}.month IN :months")
            params["months"] = months
            expanding.append("months")
        else:
            clauses.append("1 = 0")
    if include_airlines:
        airlines = tuple(sorted(set(filters.get("airlines", ()))))
        if airlines:
            clauses.append(f"{alias}.airline IN :airlines")
            params["airlines"] = airlines
            expanding.append("airlines")
        else:
            clauses.append("1 = 0")
    if origin_codes is not None:
        origins = tuple(sorted(set(origin_codes)))
        if origins:
            clauses.append(f"{alias}.origin_airport_iata IN :origins")
            params["origins"] = origins
            expanding.append("origins")
        else:
            clauses.append("1 = 0")
    if destination_codes is not None:
        destinations = tuple(sorted(set(destination_codes)))
        if destinations:
            clauses.append(f"{alias}.destination_airport_iata IN :destinations")
            params["destinations"] = destinations
            expanding.append("destinations")
        else:
            clauses.append("1 = 0")
    if airport_codes is not None:
        codes = tuple(sorted(set(airport_codes[1:])))
        if codes:
            clauses.append(f"{airport_codes[0]} IN :airport_codes")
            params["airport_codes"] = codes
            expanding.append("airport_codes")
        else:
            clauses.append("1 = 0")
    return " WHERE " + " AND ".join(clauses), params, tuple(expanding)


def _filtered_query(query: str, filters: Mapping[str, Any], *, include_months: bool = True,
                    include_airlines: bool = True,
                    origin_codes: tuple[str, ...] | None = None,
                    destination_codes: tuple[str, ...] | None = None,
                    airport_codes: tuple[str, ...] | None = None) -> pd.DataFrame:
    where, params, expanding = _where(
        filters, include_months=include_months, include_airlines=include_airlines,
        origin_codes=origin_codes, destination_codes=destination_codes,
        airport_codes=airport_codes,
    )
    return query_df(query.format(where=where), params, expanding)


def filter_options() -> dict[str, Any]:
    airline_rows = query_df(
        "SELECT a.iata_code, a.airline FROM public.airlines a ORDER BY a.airline"
    )
    airport_rows = query_df(
        "SELECT iata_code, airport, city FROM public.airports ORDER BY city, airport"
    )
    return {
        "months": tuple(range(1, 13)),
        "airlines": tuple(airline_rows["iata_code"].tolist()),
        "airline_labels": dict(zip(airline_rows["iata_code"], airline_rows["airline"])),
        "airports": tuple(airport_rows["iata_code"].tolist()),
        "airport_labels": {
            row.iata_code: f"{row.iata_code} · {row.city or row.airport}"
            for row in airport_rows.itertuples(index=False)
        },
    }


@_timed
def overview_kpis(filters: Mapping[str, Any]) -> pd.DataFrame:
    query = """
        SELECT COUNT(*) AS total_flights,
               COUNT(*) FILTER (WHERE f.cancelled = 1) AS cancelled_flights,
               COUNT(*) FILTER (WHERE f.diverted = 1) AS diverted_flights,
               ROUND(100.0 * COUNT(*) FILTER (WHERE f.cancelled = 1) / NULLIF(COUNT(*),0), 2) AS cancellation_rate,
               ROUND(100.0 * COUNT(*) FILTER (WHERE f.diverted = 1) / NULLIF(COUNT(*),0), 2) AS diversion_rate,
               COUNT(f.departure_delay) AS departure_delay_observations,
               ROUND(AVG(f.departure_delay), 2) AS avg_departure_delay,
               COUNT(f.arrival_delay) AS arrival_delay_observations,
               ROUND(AVG(f.arrival_delay), 2) AS avg_arrival_delay
        FROM public.flights_normalized f{where}
    """
    return _filtered_query(query, filters)


@_timed
def monthly_overview(filters: Mapping[str, Any]) -> pd.DataFrame:
    query = """
        SELECT f.month, COUNT(*) AS flight_count,
               COUNT(f.departure_delay) AS departure_delay_observations,
               ROUND(AVG(f.departure_delay),2) AS avg_departure_delay,
               COUNT(f.arrival_delay) AS arrival_delay_observations,
               ROUND(AVG(f.arrival_delay),2) AS avg_arrival_delay
        FROM public.flights_normalized f{where}
        GROUP BY f.month ORDER BY f.month
    """
    return _filtered_query(query, filters)


@_timed
def airline_performance(filters: Mapping[str, Any], *, volume_order: bool = False) -> pd.DataFrame:
    # Sprint 9 fix: this template was previously an f-string, so Python tried to evaluate
    # "{where}" immediately (NameError). The SQL text is now a constant template whose
    # "{where}" placeholder is filled by _filtered_query with bound parameters only.
    # Both orderings share one cached SQL result; the requested order is applied in pandas
    # (avg_departure_delay DESC NULLS LAST, matching the previous ORDER BY).
    query = """
        SELECT f.airline AS airline_code, a.airline AS airline_name,
               COUNT(*) AS flight_count,
               COUNT(f.departure_delay) AS departure_delay_observations,
               ROUND(AVG(f.departure_delay),2) AS avg_departure_delay,
               COUNT(f.arrival_delay) AS arrival_delay_observations,
               ROUND(AVG(f.arrival_delay),2) AS avg_arrival_delay,
               ROUND(100.0 * COUNT(*) FILTER (WHERE f.cancelled=1) / NULLIF(COUNT(*),0),2) AS cancellation_rate
        FROM public.flights_normalized f
        INNER JOIN public.airlines a ON a.iata_code=f.airline{where}
        GROUP BY f.airline,a.airline ORDER BY flight_count DESC
    """
    result = _filtered_query(query, filters)
    if volume_order:
        return result
    return result.sort_values(
        "avg_departure_delay", ascending=False, na_position="last", kind="mergesort",
    ).reset_index(drop=True)


@_timed
def operating_by_weekday(filters: Mapping[str, Any]) -> pd.DataFrame:
    query = """
        SELECT f.day_of_week, COUNT(*) AS flight_count
        FROM public.flights_normalized f{where}
        GROUP BY f.day_of_week ORDER BY f.day_of_week
    """
    return _filtered_query(query, filters)


@_timed
def operating_by_hour(filters: Mapping[str, Any]) -> pd.DataFrame:
    query = """
        SELECT f.scheduled_departure / 100 AS departure_hour,
               COUNT(*) AS flight_count,
               COUNT(f.departure_delay) AS delay_observations,
               ROUND(AVG(f.departure_delay),2) AS avg_departure_delay
        FROM public.flights_normalized f{where} AND f.scheduled_departure IS NOT NULL
        GROUP BY departure_hour
        HAVING f.scheduled_departure / 100 BETWEEN 0 AND 23
        ORDER BY departure_hour
    """
    return _filtered_query(query, filters)


@_timed
def monthly_operations(filters: Mapping[str, Any]) -> pd.DataFrame:
    query = """
        SELECT f.month, COUNT(*) AS flight_count,
               COUNT(*) FILTER (WHERE f.cancelled=1) AS cancelled_flights,
               ROUND(100.0 * COUNT(*) FILTER (WHERE f.cancelled=1) / NULLIF(COUNT(*),0),2) AS cancellation_rate,
               COUNT(*) FILTER (WHERE f.diverted=1) AS diverted_flights,
               ROUND(100.0 * COUNT(*) FILTER (WHERE f.diverted=1) / NULLIF(COUNT(*),0),2) AS diversion_rate
        FROM public.flights_normalized f{where}
        GROUP BY f.month ORDER BY f.month
    """
    return _filtered_query(query, filters)


def _endpoint_aggregate(filters: Mapping[str, Any], endpoint: str,
                        airport_selection: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Per-airport aggregates for one endpoint, shared by endpoint_metrics and airport_ranking.

    Sprint 9 performance change: flights are aggregated by normalized IATA code *before*
    joining public.airports (unique on iata_code). The previous form joined every flight row
    to airports and grouped by (code, city, airport); the planner mis-estimated ~3.9M groups
    and sorted millions of rows (~14 s per query). Because iata_code is unique, each code maps
    to at most one airport row, so groups, counts, AVG values and labels are identical.
    """
    if endpoint == "origin":
        code, delay = "origin_airport_iata", "departure_delay"
    elif endpoint == "destination":
        code, delay = "destination_airport_iata", "arrival_delay"
    else:
        raise ValueError("endpoint must be origin or destination")
    query = f"""
        SELECT agg.airport_code,
               COALESCE(a.city, a.airport, agg.airport_code) AS airport_label,
               COALESCE(a.airport, agg.airport_code) AS airport_name,
               a.city AS city,
               agg.flight_count, agg.delay_observations, agg.avg_delay
        FROM (
            SELECT f.{code} AS airport_code,
                   COUNT(*) AS flight_count,
                   COUNT(f.{delay}) AS delay_observations,
                   ROUND(AVG(f.{delay}),2) AS avg_delay
            FROM public.flights_normalized f{{where}}
            GROUP BY f.{code}
        ) agg
        LEFT JOIN public.airports a ON a.iata_code=agg.airport_code
        ORDER BY agg.flight_count DESC
    """
    selected = (f"f.{code}",) + airport_selection if airport_selection is not None else None
    return _filtered_query(query, filters, airport_codes=selected)


@_timed
def endpoint_metrics(filters: Mapping[str, Any], endpoint: str,
                     airport_selection: tuple[str, ...] | None = None) -> pd.DataFrame:
    data = _endpoint_aggregate(filters, endpoint, airport_selection)
    return data[["airport_code", "airport_label", "flight_count", "delay_observations", "avg_delay"]].reset_index(drop=True)


@_timed
def airport_ranking(filters: Mapping[str, Any], endpoint: str,
                    airport_selection: tuple[str, ...] | None = None) -> pd.DataFrame:
    # Same aggregate as endpoint_metrics (one cached query per endpoint/filter set).
    # Original definitions preserved: origin keeps HAVING COUNT(*) > 50000; ordering is
    # avg_delay DESC NULLS LAST.
    data = _endpoint_aggregate(filters, endpoint, airport_selection)
    if endpoint == "origin":
        data = data[data["flight_count"] > 50000]
    data = data.sort_values("avg_delay", ascending=False, na_position="last", kind="mergesort")
    return data[["airport_code", "airport_name", "city", "flight_count", "delay_observations", "avg_delay"]].reset_index(drop=True)


@_timed
def airport_heatmap(filters: Mapping[str, Any], airports: tuple[str, ...]) -> pd.DataFrame:
    where, params, expanding = _where(filters)
    codes = tuple(sorted(set(airports)))
    if codes:
        airport_clause = "AND f.origin_airport_iata IN :airport_codes"
        params["airport_codes"] = codes
        expanding = expanding + ("airport_codes",)
    else:
        airport_clause = "AND 1 = 0"
    query = f"""
        SELECT f.origin_airport_iata AS airport_code, f.month,
               ROUND(AVG(f.departure_delay),1) AS avg_departure_delay,
               COUNT(f.departure_delay) AS delay_observations
        FROM public.flights_normalized f{{where}}
          {airport_clause}
          AND f.departure_delay IS NOT NULL
        GROUP BY f.origin_airport_iata,f.month
        ORDER BY f.origin_airport_iata,f.month
    """
    return query_df(query.format(where=where), params, expanding)


@_timed
def route_metrics(filters: Mapping[str, Any], origins: tuple[str, ...] | None = None,
                  destinations: tuple[str, ...] | None = None) -> pd.DataFrame:
    # Sprint 9 performance change: aggregate by (origin, destination) IATA first, keep the top
    # 30 by volume, then attach airport labels. Identical groups/metrics to the previous
    # join-then-group form because public.airports is unique on iata_code.
    query = """
        SELECT r.origin_iata, r.destination_iata,
               COALESCE(o.city,o.airport,r.origin_iata) AS origin_label,
               COALESCE(d.city,d.airport,r.destination_iata) AS destination_label,
               r.flight_count, r.departure_delay_observations, r.avg_departure_delay,
               r.arrival_delay_observations, r.avg_arrival_delay
        FROM (
            SELECT f.origin_airport_iata AS origin_iata,
                   f.destination_airport_iata AS destination_iata,
                   COUNT(*) AS flight_count,
                   COUNT(f.departure_delay) AS departure_delay_observations,
                   ROUND(AVG(f.departure_delay),2) AS avg_departure_delay,
                   COUNT(f.arrival_delay) AS arrival_delay_observations,
                   ROUND(AVG(f.arrival_delay),2) AS avg_arrival_delay
            FROM public.flights_normalized f{where}
            GROUP BY f.origin_airport_iata,f.destination_airport_iata
            ORDER BY flight_count DESC
            LIMIT 30
        ) r
        LEFT JOIN public.airports o ON o.iata_code=r.origin_iata
        LEFT JOIN public.airports d ON d.iata_code=r.destination_iata
        ORDER BY r.flight_count DESC
    """
    return _filtered_query(query, filters, origin_codes=origins, destination_codes=destinations)


@_timed
def monthly_route_trends(filters: Mapping[str, Any], origins: tuple[str, ...] | None = None,
                         destinations: tuple[str, ...] | None = None) -> pd.DataFrame:
    # Sprint 9 performance change: aggregate once at the (month, origin, destination) grain
    # instead of materializing every selected flight row in a CTE that is scanned twice.
    # Route totals are SUM(monthly COUNT(*)) = COUNT(*) over the route, so the top-10 routes
    # and all monthly metrics are unchanged.
    query = """
        WITH monthly AS (
            SELECT f.month,f.origin_airport_iata AS origin_iata,
                   f.destination_airport_iata AS destination_iata,
                   COUNT(*) AS flight_count,
                   ROUND(AVG(f.departure_delay),2) AS avg_departure_delay,
                   ROUND(AVG(f.arrival_delay),2) AS avg_arrival_delay
            FROM public.flights_normalized f{where}
            GROUP BY f.month,f.origin_airport_iata,f.destination_airport_iata
        ), top_routes AS (
            SELECT origin_iata,destination_iata FROM monthly
            GROUP BY origin_iata,destination_iata
            ORDER BY SUM(flight_count) DESC LIMIT 10
        )
        SELECT m.month,m.origin_iata,m.destination_iata,
               m.flight_count,m.avg_departure_delay,m.avg_arrival_delay
        FROM monthly m
        INNER JOIN top_routes r USING (origin_iata,destination_iata)
        ORDER BY m.month,m.flight_count DESC
    """
    where, params, expanding = _where(
        filters, origin_codes=origins, destination_codes=destinations,
    )
    return query_df(query.format(where=where), params, expanding)


@_timed
def delay_causes(filters: Mapping[str, Any]) -> pd.DataFrame:
    # Preserve original root-cause definition: cause SUMs / 60, only departure_delay > 0.
    query = """
        SELECT ROUND(SUM(f.late_aircraft_delay)/60.0,0) AS late_aircraft_hours,
               ROUND(SUM(f.airline_delay)/60.0,0) AS airline_hours,
               ROUND(SUM(f.air_system_delay)/60.0,0) AS nas_hours,
               ROUND(SUM(f.weather_delay)/60.0,0) AS weather_hours,
               ROUND(SUM(f.security_delay)/60.0,0) AS security_hours
        FROM public.flights_normalized f{where} AND f.departure_delay > 0
    """
    return _filtered_query(query, filters)


@_timed
def monthly_delay_causes(filters: Mapping[str, Any]) -> pd.DataFrame:
    query = """
        SELECT f.month,
               ROUND(SUM(f.late_aircraft_delay)/60.0,0) AS late_aircraft_hours,
               ROUND(SUM(f.airline_delay)/60.0,0) AS airline_hours,
               ROUND(SUM(f.air_system_delay)/60.0,0) AS nas_hours,
               ROUND(SUM(f.weather_delay)/60.0,0) AS weather_hours,
               ROUND(SUM(f.security_delay)/60.0,0) AS security_hours
        FROM public.flights_normalized f{where} AND f.departure_delay > 0
        GROUP BY f.month ORDER BY f.month
    """
    return _filtered_query(query, filters)


@_timed
def delay_distribution(filters: Mapping[str, Any], delay_column: str) -> pd.DataFrame:
    columns = {"departure": "departure_delay", "arrival": "arrival_delay"}
    if delay_column not in columns:
        raise ValueError("delay_column must be departure or arrival")
    field = columns[delay_column]
    query = f"""
        WITH binned AS (
            SELECT f.{field} AS delay_value,
                   CASE WHEN f.{field} < -60 THEN -1
                        WHEN f.{field} >= 240 THEN 10
                        ELSE FLOOR((f.{field}+60)/30)::INTEGER END AS bin_id
            FROM public.flights_normalized f{{where}}
              AND f.{field} IS NOT NULL
        )
        SELECT bin_id,
               CASE WHEN bin_id=-1 THEN '< -60'
                    WHEN bin_id=10 THEN '240+'
                    ELSE (bin_id*30-60)::TEXT || ' to ' || (bin_id*30-30)::TEXT END AS delay_range,
               COUNT(*) AS flight_count
        FROM binned GROUP BY bin_id ORDER BY bin_id
    """
    return _filtered_query(query, filters)


@_timed
def live_data_quality() -> pd.DataFrame:
    # One aggregate scan of the normalized flight view plus one small crosswalk scan.
    return query_df("""
        WITH flight_audit AS (
          SELECT COUNT(*) AS live_total_rows,
                 COUNT(*) FILTER (WHERE f.year=2015 AND f.month=10) AS live_october_rows,
                 COUNT(*) FILTER (WHERE f.year=2015 AND f.month=10 AND o.iata_code IS NOT NULL) AS october_origin_coverage,
                 COUNT(*) FILTER (WHERE f.year=2015 AND f.month=10 AND d.iata_code IS NOT NULL) AS october_destination_coverage,
                 COUNT(*) FILTER (WHERE f.year=2015 AND f.month=10 AND f.origin_airport_mapping_status='unresolved') AS unresolved_october_origins,
                 COUNT(*) FILTER (WHERE f.year=2015 AND f.month=10 AND f.destination_airport_mapping_status='unresolved') AS unresolved_october_destinations
          FROM public.flights_normalized f
          LEFT JOIN public.airports o ON o.iata_code=f.origin_airport_iata
          LEFT JOIN public.airports d ON d.iata_code=f.destination_airport_iata
        ), crosswalk_audit AS (
          SELECT COUNT(*) AS live_crosswalk_rows,
                 COUNT(DISTINCT c.airport_id) AS distinct_crosswalk_ids,
                 COUNT(DISTINCT c.airport_sequence_id) AS distinct_crosswalk_sequences,
                 COUNT(*) FILTER (WHERE a.iata_code IS NULL) AS crosswalk_codes_missing_reference
          FROM public.airport_id_iata_crosswalk c
          LEFT JOIN public.airports a ON a.iata_code=c.iata_code
          WHERE c.source_dataset_month=DATE '2015-10-01'
        )
        SELECT * FROM flight_audit CROSS JOIN crosswalk_audit
    """)

"""Normalized monthly origin-delay heatmap for the 2015 flight dataset."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import bindparam, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "python"))
from db_connect import get_engine  # noqa: E402

TOP_AIRPORTS = ("ATL", "ORD", "DFW", "DEN", "LAX", "SFO", "PHX", "IAH", "LAS", "MSP")
AIRPORT_LABELS = {
    "ATL": "ATL (Atlanta)",
    "ORD": "ORD (Chicago)",
    "DFW": "DFW (Dallas)",
    "DEN": "DEN (Denver)",
    "LAX": "LAX (Los Angeles)",
    "SFO": "SFO (San Francisco)",
    "PHX": "PHX (Phoenix)",
    "IAH": "IAH (Houston)",
    "LAS": "LAS (Las Vegas)",
    "MSP": "MSP (Minneapolis)",
}
MONTH_LABELS = {
    1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 5: "May", 6: "Haz",
    7: "Tem", 8: "Ağu", 9: "Eyl", 10: "Eki", 11: "Kas", 12: "Ara",
}
OUTPUT = PROJECT_ROOT / "assets" / "normalized" / "airport_monthly_heatmap.png"

# Same KPI as the original chart: average non-NULL departure delay by origin/month.
# The normalized Sprint 6 source resolves October's numeric airport identifiers.
QUERY = text("""
    SELECT
        f.origin_airport_iata AS origin_airport,
        f.month,
        ROUND(AVG(f.departure_delay), 1) AS avg_delay
    FROM public.flights_normalized AS f
    WHERE f.origin_airport_iata IN :airports
      AND f.departure_delay IS NOT NULL
    GROUP BY f.origin_airport_iata, f.month
    ORDER BY f.origin_airport_iata, f.month
""").bindparams(bindparam("airports", expanding=True))


def fetch_monthly_delays() -> pd.DataFrame:
    """Load the normalized SQL aggregation, closing the connection reliably."""
    engine = get_engine()
    try:
        with engine.connect() as connection:
            frame = pd.read_sql_query(QUERY, connection, params={"airports": TOP_AIRPORTS})
    finally:
        engine.dispose()
    return frame


def validate_data(frame: pd.DataFrame) -> None:
    required = {"origin_airport", "month", "avg_delay"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Query result is missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("The normalized monthly airport query returned no rows.")
    if frame["origin_airport"].isna().any():
        raise ValueError("The query returned a null airport code.")
    if frame.duplicated(["origin_airport", "month"]).any():
        raise ValueError("The query returned duplicate airport/month groups.")
    if not frame["origin_airport"].isin(TOP_AIRPORTS).all():
        raise ValueError("The query returned an airport outside the original top-ten list.")
    if not frame["month"].between(1, 12).all():
        raise ValueError("The query returned a month outside 1–12.")


def render_chart(frame: pd.DataFrame) -> Path:
    validate_data(frame)
    frame = frame.copy()
    frame["airport_label"] = frame["origin_airport"].map(AIRPORT_LABELS)
    heatmap = frame.pivot(index="airport_label", columns="month", values="avg_delay")
    heatmap = heatmap.reindex(index=[AIRPORT_LABELS[a] for a in TOP_AIRPORTS])
    heatmap = heatmap.reindex(columns=range(1, 13))
    heatmap.columns = [MONTH_LABELS[m] for m in heatmap.columns]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(13, 7))
    sns.set_theme(style="white")
    sns.heatmap(
        heatmap,
        cmap="YlOrRd",
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        cbar_kws={"label": "Ortalama Kalkış Gecikmesi (Dakika)"},
    )
    plt.title("En Yoğun 10 ABD Havalimanında Aylık Gecikme Isı Haritası", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Aylar", fontsize=12)
    plt.ylabel("Havalimanı", fontsize=12)
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=300)
    plt.close()
    return OUTPUT


def main() -> None:
    try:
        result = render_chart(fetch_monthly_delays())
    except Exception as exc:
        raise SystemExit(f"Normalized airport heatmap failed ({type(exc).__name__}); check the local database configuration and query results.") from None
    print(f"Normalized airport heatmap saved: {result}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from dashboard.components import (
    PALETTE,
    build_hover,
    chart_caption,
    empty_state,
    format_number,
    kpi_grid,
    month_label,
    page_heading,
    scope_strip,
    section_heading,
    show_chart,
    status_banner,
)
from dashboard.data_access import airline_performance, monthly_overview, overview_kpis
from dashboard.i18n import t

filters = st.session_state.get("dashboard_filters", {})
page_heading(t("page.executive.title"), t("page.executive.desc"), section=t("page.executive.kicker"))
scope_strip(filters)

with st.spinner(t("status.loading")):
    kpis = overview_kpis(filters)
    monthly = monthly_overview(filters)
    airlines = airline_performance(filters, volume_order=True)

if kpis.empty or not int(kpis.iloc[0]["total_flights"]):
    empty_state()
else:
    row = kpis.iloc[0]
    u_min = t("unit.min")
    u_flights = t("unit.flights")

    kpi_grid(
        [
            {
                "label": t("exec.kpi.total_flights"),
                "value": format_number(row.total_flights),
                "note": t("exec.kpi.total_flights_note"),
                "icon": "flight",
                "tone": "gold",
            },
            {
                "label": t("exec.kpi.avg_dep_delay"),
                "value": format_number(row.avg_departure_delay, 2),
                "unit": u_min,
                "note": t("exec.kpi.obs_note", count=format_number(row.departure_delay_observations)),
                "icon": "clock",
                "tone": "gold",
            },
            {
                "label": t("exec.kpi.avg_arr_delay"),
                "value": format_number(row.avg_arrival_delay, 2),
                "unit": u_min,
                "note": t("exec.kpi.obs_note", count=format_number(row.arrival_delay_observations)),
                "icon": "arrival",
                "tone": "cyan",
            },
            {
                "label": t("exec.kpi.cancel_rate"),
                "value": f"{format_number(row.cancellation_rate, 2)}%",
                "note": t("exec.kpi.cancel_note", count=format_number(row.cancelled_flights)),
                "icon": "cancel",
                "tone": "warning",
            },
            {
                "label": t("exec.kpi.divert_rate"),
                "value": f"{format_number(row.diversion_rate, 2)}%",
                "note": t("exec.kpi.divert_note", count=format_number(row.diverted_flights)),
                "icon": "divert",
                "tone": "cyan",
            },
        ],
        columns_hint=5,
    )

    if not monthly.empty:
        peak = monthly.loc[monthly["flight_count"].idxmax()]
        status_banner(
            t(
                "exec.insight.peak",
                month=month_label(peak.month, short=False),
                count=format_number(peak.flight_count),
                dep=format_number(peak.avg_departure_delay, 2),
            ),
            tone="gold",
            icon="flight",
        )

        ordered_months = sorted(monthly["month"].unique())
        m_df = monthly.sort_values("month").copy()
        m_df["short_label"] = m_df["month"].map(lambda m: month_label(m, short=True))
        m_df["full_label"] = m_df["month"].map(lambda m: month_label(m, short=False))
        short_order = [month_label(m, short=True) for m in ordered_months]

        left, right = st.columns(2, gap="medium")
        with left:
            section_heading(t("exec.sec.monthly_vol"), t("exec.sec.monthly_vol_sub"))
            fig_vol = go.Figure(
                go.Bar(
                    x=m_df["short_label"],
                    y=m_df["flight_count"],
                    marker={"color": PALETTE["gold"], "line": {"width": 0}},
                    customdata=np.column_stack(
                        [
                            m_df["full_label"],
                            m_df["avg_departure_delay"].fillna(0.0),
                            m_df["avg_arrival_delay"].fillna(0.0),
                        ]
                    ),
                    hovertemplate=build_hover(
                        t("label.month"),
                        "%{customdata[0]} 2015",
                        [
                            (t("label.flights"), f"%{{y:,.0f}} {u_flights}"),
                            (t("label.avg_dep_delay"), f"%{{customdata[1]:.2f}} {u_min}"),
                            (t("label.avg_arr_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                        ],
                    ),
                )
            )
            fig_vol.update_xaxes(
                title=t("label.month"),
                categoryorder="array",
                categoryarray=short_order,
            )
            fig_vol.update_yaxes(title=t("label.flights"), tickformat=",")
            show_chart(fig_vol, height=360, show_legend=False)

        with right:
            section_heading(t("exec.sec.monthly_delay"), t("exec.sec.monthly_delay_sub"))
            fig_delay = go.Figure()
            fig_delay.add_trace(
                go.Scatter(
                    x=m_df["short_label"],
                    y=m_df["avg_departure_delay"],
                    name=t("label.departure"),
                    mode="lines+markers",
                    line={"color": PALETTE["gold"], "width": 2.6},
                    marker={"size": 7, "color": PALETTE["gold"], "line": {"color": "#0B1220", "width": 1.2}},
                    customdata=np.column_stack([m_df["full_label"], m_df["departure_delay_observations"]]),
                    hovertemplate=build_hover(
                        t("label.month"),
                        "%{customdata[0]} 2015",
                        [
                            (t("label.delay_type"), t("label.departure")),
                            (t("label.avg_dep_delay"), f"%{{y:.2f}} {u_min}"),
                            (t("label.observed_delays"), "%{customdata[1]:,.0f}"),
                        ],
                    ),
                )
            )
            fig_delay.add_trace(
                go.Scatter(
                    x=m_df["short_label"],
                    y=m_df["avg_arrival_delay"],
                    name=t("label.arrival"),
                    mode="lines+markers",
                    line={"color": PALETTE["cyan"], "width": 2.6},
                    marker={"size": 7, "color": PALETTE["cyan"], "line": {"color": "#0B1220", "width": 1.2}},
                    customdata=np.column_stack([m_df["full_label"], m_df["arrival_delay_observations"]]),
                    hovertemplate=build_hover(
                        t("label.month"),
                        "%{customdata[0]} 2015",
                        [
                            (t("label.delay_type"), t("label.arrival")),
                            (t("label.avg_arr_delay"), f"%{{y:.2f}} {u_min}"),
                            (t("label.observed_delays"), "%{customdata[1]:,.0f}"),
                        ],
                    ),
                )
            )
            fig_delay.update_xaxes(
                title=t("label.month"),
                categoryorder="array",
                categoryarray=short_order,
            )
            fig_delay.update_yaxes(title=f"{t('label.avg_delay')} ({u_min})", zeroline=True)
            show_chart(fig_delay, height=360, show_legend=True)

    if not airlines.empty:
        section_heading(t("exec.sec.airline_perf"), t("exec.sec.airline_perf_sub"))
        max_flights = max(float(airlines["flight_count"].max()), 1.0)
        sizes = np.clip(np.sqrt(airlines["flight_count"].astype(float) / max_flights) * 44.0, 12.0, 44.0)
        fig_air = go.Figure(
            go.Scatter(
                x=airlines["flight_count"],
                y=airlines["avg_departure_delay"],
                mode="markers+text",
                text=airlines["airline_code"],
                textposition="top center",
                textfont={"size": 10.5, "color": "#CBD5E1"},
                marker={
                    "size": sizes,
                    "color": airlines["cancellation_rate"],
                    "colorscale": [[0.0, "#1E5F74"], [0.5, "#38BDF8"], [1.0, "#F5C451"]],
                    "showscale": True,
                    "colorbar": {
                        "title": {"text": f"{t('label.cancellation_rate')}<br>(%)", "font": {"size": 11, "color": "#CBD5E1"}},
                        "tickfont": {"size": 11, "color": "#94A3B8"},
                        "thickness": 14,
                        "outlinewidth": 0,
                    },
                    "line": {"color": "#0B1220", "width": 1.3},
                    "opacity": 0.90,
                },
                customdata=np.column_stack(
                    [
                        airlines["airline_name"],
                        airlines["airline_code"],
                        airlines["avg_arrival_delay"].fillna(0.0),
                        airlines["cancellation_rate"].fillna(0.0),
                        airlines["departure_delay_observations"],
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.airline"),
                    "%{customdata[0]} (%{customdata[1]})",
                    [
                        (t("label.flights"), f"%{{x:,.0f}} {u_flights}"),
                        (t("label.avg_dep_delay"), f"%{{y:.2f}} {u_min}"),
                        (t("label.avg_arr_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                        (t("label.cancellation_rate"), "%{customdata[3]:.2f}%"),
                        (t("label.observed_delays"), "%{customdata[4]:,.0f}"),
                    ],
                ),
            )
        )
        fig_air.update_xaxes(title=t("label.flights"), tickformat=",", showgrid=True)
        fig_air.update_yaxes(title=f"{t('label.avg_dep_delay')} ({u_min})")
        show_chart(fig_air, height=450, show_legend=False, margin={"t": 34, "r": 30})
        chart_caption(t("exec.sec.airline_caption"))

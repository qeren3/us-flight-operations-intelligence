from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from dashboard.components import (
    PALETTE,
    build_hover,
    chart_caption,
    empty_state,
    month_label,
    page_heading,
    scope_strip,
    section_heading,
    show_chart,
)
from dashboard.data_access import (
    airline_performance,
    monthly_operations,
    operating_by_hour,
    operating_by_weekday,
)
from dashboard.i18n import t

filters = st.session_state.get("dashboard_filters", {})
page_heading(t("page.operations.title"), t("page.operations.desc"), section=t("page.operations.kicker"))
scope_strip(filters)

with st.spinner(t("status.loading")):
    monthly = monthly_operations(filters)
    weekday = operating_by_weekday(filters)
    hourly = operating_by_hour(filters)
    airline_volume = airline_performance(filters, volume_order=True)

if monthly.empty:
    empty_state()
else:
    u_flights = t("unit.flights")
    u_min = t("unit.min")

    m_df = monthly.sort_values("month").copy()
    m_df["short_label"] = m_df["month"].map(lambda m: month_label(m, short=True))
    m_df["full_label"] = m_df["month"].map(lambda m: month_label(m, short=False))
    short_order = m_df["short_label"].tolist()

    section_heading(t("ops.sec.monthly_vol"), t("ops.sec.monthly_vol_sub"))
    fig_m = go.Figure(
        go.Bar(
            x=m_df["short_label"],
            y=m_df["flight_count"],
            marker={"color": PALETTE["gold"]},
            customdata=np.column_stack(
                [
                    m_df["full_label"],
                    m_df["cancellation_rate"].fillna(0.0),
                    m_df["diversion_rate"].fillna(0.0),
                    m_df["cancelled_flights"],
                ]
            ),
            hovertemplate=build_hover(
                t("label.month"),
                "%{customdata[0]} 2015",
                [
                    (t("label.flights"), f"%{{y:,.0f}} {u_flights}"),
                    (t("label.cancellation_rate"), "%{customdata[1]:.2f}% (%{customdata[3]:,.0f})"),
                    (t("label.diversion_rate"), "%{customdata[2]:.2f}%"),
                ],
            ),
        )
    )
    fig_m.update_xaxes(title=t("label.month"), categoryorder="array", categoryarray=short_order)
    fig_m.update_yaxes(title=t("label.flights"), tickformat=",")
    show_chart(fig_m, height=340, show_legend=False)

    left, right = st.columns(2, gap="medium")
    with left:
        section_heading(t("ops.sec.weekday"), t("ops.sec.weekday_sub"))
        if weekday.empty:
            empty_state()
        else:
            fig_wd = go.Figure(
                go.Bar(
                    x=weekday["day_of_week"],
                    y=weekday["flight_count"],
                    marker={"color": PALETTE["cyan"]},
                    hovertemplate=build_hover(
                        t("label.day_of_week_code"),
                        "%{x}",
                        [(t("label.flights"), f"%{{y:,.0f}} {u_flights}")],
                    ),
                )
            )
            fig_wd.update_xaxes(title=t("label.day_of_week_code"), dtick=1)
            fig_wd.update_yaxes(title=t("label.flights"), tickformat=",")
            show_chart(fig_wd, height=350, show_legend=False)
            chart_caption(t("ops.sec.weekday_cap"))

    with right:
        section_heading(t("ops.sec.hourly"), t("ops.sec.hourly_sub"))
        if hourly.empty:
            empty_state()
        else:
            hour_windows = [t("ops.hover.hour_fmt", hour=int(h)) for h in hourly["departure_hour"]]
            fig_hr = go.Figure(
                go.Scatter(
                    x=hourly["departure_hour"],
                    y=hourly["avg_departure_delay"],
                    mode="lines+markers",
                    line={"color": PALETTE["gold"], "width": 2.6},
                    marker={"size": 6.5, "color": PALETTE["gold"], "line": {"color": "#0B1220", "width": 1.1}},
                    fill="tozeroy",
                    fillcolor="rgba(245, 196, 81, 0.08)",
                    customdata=np.column_stack(
                        [hour_windows, hourly["flight_count"], hourly["delay_observations"]]
                    ),
                    hovertemplate=build_hover(
                        t("label.scheduled_hour"),
                        "%{customdata[0]}",
                        [
                            (t("label.avg_dep_delay"), f"%{{y:.2f}} {u_min}"),
                            (t("label.flights"), f"%{{customdata[1]:,.0f}} {u_flights}"),
                            (t("label.observed_delays"), "%{customdata[2]:,.0f}"),
                        ],
                    ),
                )
            )
            fig_hr.update_xaxes(title=f"{t('label.scheduled_hour')} (0–23)", dtick=2, range=[-0.5, 23.5])
            fig_hr.update_yaxes(title=f"{t('label.avg_dep_delay')} ({u_min})", zeroline=True)
            show_chart(fig_hr, height=350, show_legend=False)
            chart_caption(t("ops.sec.hourly_cap"))

    section_heading(t("ops.sec.disruptions"), t("ops.sec.disruptions_sub"))
    fig_dis = go.Figure()
    fig_dis.add_trace(
        go.Scatter(
            x=m_df["short_label"],
            y=m_df["cancellation_rate"],
            name=t("ops.legend.cancellation"),
            mode="lines+markers",
            line={"color": PALETTE["gold"], "width": 2.6},
            marker={"size": 7, "color": PALETTE["gold"], "line": {"color": "#0B1220", "width": 1.2}},
            customdata=np.column_stack([m_df["full_label"], m_df["cancelled_flights"], m_df["flight_count"]]),
            hovertemplate=build_hover(
                t("label.month"),
                "%{customdata[0]} 2015",
                [
                    (t("label.cancellation_rate"), "%{y:.2f}%"),
                    (t("label.cancelled_flights"), f"%{{customdata[1]:,.0f}} {u_flights}"),
                    (t("label.flights"), f"%{{customdata[2]:,.0f}} {u_flights}"),
                ],
            ),
        )
    )
    fig_dis.add_trace(
        go.Scatter(
            x=m_df["short_label"],
            y=m_df["diversion_rate"],
            name=t("ops.legend.diversion"),
            mode="lines+markers",
            line={"color": PALETTE["cyan"], "width": 2.6},
            marker={"size": 7, "color": PALETTE["cyan"], "line": {"color": "#0B1220", "width": 1.2}},
            customdata=np.column_stack([m_df["full_label"], m_df["diverted_flights"], m_df["flight_count"]]),
            hovertemplate=build_hover(
                t("label.month"),
                "%{customdata[0]} 2015",
                [
                    (t("label.diversion_rate"), "%{y:.2f}%"),
                    (t("label.diverted_flights"), f"%{{customdata[1]:,.0f}} {u_flights}"),
                    (t("label.flights"), f"%{{customdata[2]:,.0f}} {u_flights}"),
                ],
            ),
        )
    )
    fig_dis.update_xaxes(title=t("label.month"), categoryorder="array", categoryarray=short_order)
    fig_dis.update_yaxes(title=t("label.rate_pct"), ticksuffix="%")
    show_chart(fig_dis, height=360, show_legend=True)
    chart_caption(t("ops.sec.disruptions_cap"))

    if not airline_volume.empty:
        section_heading(t("ops.sec.airline_vol"), t("ops.sec.airline_vol_sub"))
        top = airline_volume.head(15).sort_values("flight_count")
        fig_av = go.Figure(
            go.Bar(
                x=top["flight_count"],
                y=top["airline_name"],
                orientation="h",
                marker={"color": PALETTE["cyan"]},
                customdata=np.column_stack(
                    [
                        top["airline_name"],
                        top["airline_code"],
                        top["avg_departure_delay"].fillna(0.0),
                        top["cancellation_rate"].fillna(0.0),
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.airline"),
                    "%{customdata[0]} (%{customdata[1]})",
                    [
                        (t("label.flights"), f"%{{x:,.0f}} {u_flights}"),
                        (t("label.avg_dep_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                        (t("label.cancellation_rate"), "%{customdata[3]:.2f}%"),
                    ],
                ),
            )
        )
        fig_av.update_xaxes(title=t("label.flights"), tickformat=",", showgrid=True)
        fig_av.update_yaxes(title="", showgrid=False)
        show_chart(fig_av, height=440, show_legend=False)

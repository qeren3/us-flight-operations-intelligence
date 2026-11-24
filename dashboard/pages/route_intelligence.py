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
from dashboard.data_access import monthly_route_trends, route_metrics
from dashboard.i18n import t

filters = st.session_state.get("dashboard_filters", {})
origin = filters.get("route_origin", "Any origin")
destination = filters.get("route_destination", "Any destination")
origins = None if origin == "Any origin" else (origin,)
destinations = None if destination == "Any destination" else (destination,)

extra_chips: tuple[str, ...] = ()
if origins or destinations:
    o_lbl = origin if origins else t("filter.any_origin")
    d_lbl = destination if destinations else t("filter.any_destination")
    extra_chips = (t("scope.route_scope", scope=f"{o_lbl} → {d_lbl}"),)

page_heading(t("page.routes.title"), t("page.routes.desc"), section=t("page.routes.kicker"))
scope_strip(filters, extra_chips=extra_chips)

with st.spinner(t("status.loading")):
    routes = route_metrics(filters, origins=origins, destinations=destinations)
    monthly = monthly_route_trends(filters, origins=origins, destinations=destinations)

u_flights = t("unit.flights")
u_min = t("unit.min")

if routes.empty:
    empty_state()
else:
    routes = routes.copy()
    routes["route"] = routes["origin_iata"].fillna("?") + " → " + routes["destination_iata"].fillna("?")

    left, right = st.columns(2, gap="medium")
    with left:
        section_heading(t("route.sec.top_routes"), t("route.sec.top_routes_sub"))
        top = routes.head(15).sort_values("flight_count")
        fig_r = go.Figure(
            go.Bar(
                x=top["flight_count"],
                y=top["route"],
                orientation="h",
                marker={"color": PALETTE["gold"]},
                customdata=np.column_stack(
                    [
                        top["origin_label"].fillna("—"),
                        top["destination_label"].fillna("—"),
                        top["avg_departure_delay"].fillna(0.0),
                        top["avg_arrival_delay"].fillna(0.0),
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.route"),
                    "%{y}",
                    [
                        (t("label.flights"), f"%{{x:,.0f}} {u_flights}"),
                        (t("label.avg_dep_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                        (t("label.avg_arr_delay"), f"%{{customdata[3]:.2f}} {u_min}"),
                    ],
                    subtitle_expr="%{customdata[0]} → %{customdata[1]}",
                ),
            )
        )
        fig_r.update_xaxes(title=t("label.flights"), tickformat=",", showgrid=True)
        fig_r.update_yaxes(title="", showgrid=False)
        show_chart(fig_r, height=460, show_legend=False)

    with right:
        section_heading(t("route.sec.delay_scatter"), t("route.sec.delay_scatter_sub"))
        max_f = max(float(routes["flight_count"].max()), 1.0)
        sizes = np.clip(np.sqrt(routes["flight_count"].astype(float) / max_f) * 34.0, 9.0, 34.0)
        fig_sc = go.Figure(
            go.Scatter(
                x=routes["avg_departure_delay"],
                y=routes["avg_arrival_delay"],
                mode="markers",
                marker={
                    "size": sizes,
                    "color": routes["flight_count"],
                    "colorscale": [[0.0, "#1E5F74"], [0.5, "#38BDF8"], [1.0, "#F5C451"]],
                    "showscale": True,
                    "colorbar": {
                        "title": {"text": t("label.flights"), "font": {"size": 11, "color": "#CBD5E1"}},
                        "tickfont": {"size": 11, "color": "#94A3B8"},
                        "tickformat": ",",
                        "thickness": 14,
                        "outlinewidth": 0,
                    },
                    "line": {"color": "#0B1220", "width": 1.1},
                    "opacity": 0.90,
                },
                customdata=np.column_stack(
                    [
                        routes["route"],
                        routes["origin_label"].fillna("—"),
                        routes["destination_label"].fillna("—"),
                        routes["flight_count"],
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.route"),
                    "%{customdata[0]}",
                    [
                        (t("label.flights"), f"%{{customdata[3]:,.0f}} {u_flights}"),
                        (t("label.avg_dep_delay"), f"%{{x:.2f}} {u_min}"),
                        (t("label.avg_arr_delay"), f"%{{y:.2f}} {u_min}"),
                    ],
                    subtitle_expr="%{customdata[1]} → %{customdata[2]}",
                ),
            )
        )
        fig_sc.update_xaxes(title=f"{t('label.avg_dep_delay')} ({u_min})", showgrid=True, zeroline=True)
        fig_sc.update_yaxes(title=f"{t('label.avg_arr_delay')} ({u_min})", zeroline=True)
        show_chart(fig_sc, height=460, show_legend=False)

    section_heading(t("route.sec.monthly_trends"), t("route.sec.monthly_trends_sub"))
    if monthly.empty:
        empty_state()
    else:
        monthly = monthly.copy()
        monthly["route"] = monthly["origin_iata"].fillna("?") + " → " + monthly["destination_iata"].fillna("?")
        monthly["short_label"] = monthly["month"].map(lambda m: month_label(m, short=True))
        monthly["full_label"] = monthly["month"].map(lambda m: month_label(m, short=False))
        ordered_months = sorted(monthly["month"].unique())
        short_order = [month_label(m, short=True) for m in ordered_months]

        route_order = (
            monthly.groupby("route", as_index=False)["flight_count"]
            .sum()
            .sort_values("flight_count", ascending=False)["route"]
            .tolist()
        )
        fig_mt = go.Figure()
        for idx, route_name in enumerate(route_order):
            sub = monthly[monthly["route"] == route_name].sort_values("month")
            color = PALETTE["routes"][idx % len(PALETTE["routes"])]
            fig_mt.add_trace(
                go.Scatter(
                    x=sub["short_label"],
                    y=sub["flight_count"],
                    name=route_name,
                    mode="lines+markers",
                    line={"color": color, "width": 2.2},
                    marker={"size": 6, "color": color, "line": {"color": "#0B1220", "width": 1}},
                    customdata=np.column_stack(
                        [
                            sub["route"],
                            sub["full_label"],
                            sub["avg_departure_delay"].fillna(0.0),
                            sub["avg_arrival_delay"].fillna(0.0),
                        ]
                    ),
                    hovertemplate=build_hover(
                        t("label.route"),
                        "%{customdata[0]} · %{customdata[1]} 2015",
                        [
                            (t("label.flights"), f"%{{y:,.0f}} {u_flights}"),
                            (t("label.avg_dep_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                            (t("label.avg_arr_delay"), f"%{{customdata[3]:.2f}} {u_min}"),
                        ],
                    ),
                )
            )
        fig_mt.update_xaxes(
            title=t("label.month"),
            categoryorder="array",
            categoryarray=short_order,
        )
        fig_mt.update_yaxes(title=t("label.flights"), tickformat=",")
        show_chart(fig_mt, height=440, show_legend=True, margin={"t": 58})
        chart_caption(t("route.sec.monthly_trends_cap"))

    section_heading(t("route.sec.table"), t("route.sec.table_sub"))
    st.dataframe(
        routes[
            [
                "route",
                "origin_label",
                "destination_label",
                "flight_count",
                "departure_delay_observations",
                "avg_departure_delay",
                "arrival_delay_observations",
                "avg_arrival_delay",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "route": t("label.route"),
            "origin_label": t("label.origin"),
            "destination_label": t("label.destination"),
            "flight_count": st.column_config.NumberColumn(t("label.flights"), format="%,d"),
            "departure_delay_observations": st.column_config.NumberColumn(t("label.dep_obs"), format="%,d"),
            "avg_departure_delay": st.column_config.NumberColumn(f"{t('label.avg_dep_delay')} ({u_min})", format="%.2f"),
            "arrival_delay_observations": st.column_config.NumberColumn(t("label.arr_obs"), format="%,d"),
            "avg_arrival_delay": st.column_config.NumberColumn(f"{t('label.avg_arr_delay')} ({u_min})", format="%.2f"),
        },
    )
    chart_caption(t("route.sec.table_cap"))

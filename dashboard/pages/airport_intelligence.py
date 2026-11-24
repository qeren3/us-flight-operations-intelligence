from __future__ import annotations

import numpy as np
import pandas as pd
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
from dashboard.data_access import airport_heatmap, airport_ranking, endpoint_metrics
from dashboard.i18n import t

filters = st.session_state.get("dashboard_filters", {})
selected = tuple(filters.get("airport_focus", ()))
airport_selection = selected or None

page_heading(t("page.airports.title"), t("page.airports.desc"), section=t("page.airports.kicker"))
extra_chips = (t("scope.airports_focus", count=len(selected)),) if selected else ()
scope_strip(filters, extra_chips=extra_chips)

with st.spinner(t("status.loading")):
    origin = endpoint_metrics(filters, "origin", airport_selection)
    destination = endpoint_metrics(filters, "destination", airport_selection)
    departures = airport_ranking(filters, "origin", airport_selection)
    arrivals = airport_ranking(filters, "destination", airport_selection)

u_flights = t("unit.flights")
u_min = t("unit.min")

left, right = st.columns(2, gap="medium")
with left:
    section_heading(t("air.sec.top_origin"), t("air.sec.top_origin_sub"))
    if origin.empty:
        empty_state()
    else:
        top = origin.head(15).sort_values("flight_count").copy()
        top["axis_label"] = top["airport_label"] + " (" + top["airport_code"] + ")"
        fig_o = go.Figure(
            go.Bar(
                x=top["flight_count"],
                y=top["axis_label"],
                orientation="h",
                marker={"color": PALETTE["gold"]},
                customdata=np.column_stack(
                    [
                        top["airport_label"],
                        top["airport_code"],
                        top["avg_delay"].fillna(0.0),
                        top["delay_observations"],
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.airport"),
                    "%{customdata[0]} (%{customdata[1]})",
                    [
                        (t("label.departures"), f"%{{x:,.0f}} {u_flights}"),
                        (t("label.avg_dep_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                        (t("label.observed_delays"), "%{customdata[3]:,.0f}"),
                    ],
                ),
            )
        )
        fig_o.update_xaxes(title=t("label.departures"), tickformat=",", showgrid=True)
        fig_o.update_yaxes(title="", showgrid=False)
        show_chart(fig_o, height=440, show_legend=False)

with right:
    section_heading(t("air.sec.top_dest"), t("air.sec.top_dest_sub"))
    if destination.empty:
        empty_state()
    else:
        top = destination.head(15).sort_values("flight_count").copy()
        top["axis_label"] = top["airport_label"] + " (" + top["airport_code"] + ")"
        fig_d = go.Figure(
            go.Bar(
                x=top["flight_count"],
                y=top["axis_label"],
                orientation="h",
                marker={"color": PALETTE["cyan"]},
                customdata=np.column_stack(
                    [
                        top["airport_label"],
                        top["airport_code"],
                        top["avg_delay"].fillna(0.0),
                        top["delay_observations"],
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.airport"),
                    "%{customdata[0]} (%{customdata[1]})",
                    [
                        (t("label.arrivals"), f"%{{x:,.0f}} {u_flights}"),
                        (t("label.avg_arr_delay"), f"%{{customdata[2]:.2f}} {u_min}"),
                        (t("label.observed_delays"), "%{customdata[3]:,.0f}"),
                    ],
                ),
            )
        )
        fig_d.update_xaxes(title=t("label.arrivals"), tickformat=",", showgrid=True)
        fig_d.update_yaxes(title="", showgrid=False)
        show_chart(fig_d, height=440, show_legend=False)

section_heading(t("air.sec.rankings"), t("air.sec.rankings_sub"))
rank_left, rank_right = st.columns(2, gap="medium")
with rank_left:
    st.markdown(f"**{t('air.sec.rank_dep')}**")
    if departures.empty:
        empty_state(t("status.empty_threshold"))
    else:
        view = departures.head(15).sort_values("avg_delay").copy()
        view["axis_label"] = view["airport_code"] + " · " + view["city"].fillna(view["airport_name"])
        fig_rd = go.Figure(
            go.Bar(
                x=view["avg_delay"],
                y=view["axis_label"],
                orientation="h",
                marker={"color": PALETTE["gold"]},
                customdata=np.column_stack(
                    [
                        view["airport_name"],
                        view["airport_code"],
                        view["city"].fillna("—"),
                        view["flight_count"],
                        view["delay_observations"],
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.airport"),
                    "%{customdata[0]} (%{customdata[1]})",
                    [
                        (t("label.city"), "%{customdata[2]}"),
                        (t("label.avg_dep_delay"), f"%{{x:.2f}} {u_min}"),
                        (t("label.departures"), f"%{{customdata[3]:,.0f}} {u_flights}"),
                        (t("label.observed_delays"), "%{customdata[4]:,.0f}"),
                    ],
                ),
            )
        )
        fig_rd.update_xaxes(title=f"{t('label.avg_delay')} ({u_min})", showgrid=True, nticks=5, tickangle=0)
        fig_rd.update_yaxes(title="", showgrid=False)
        show_chart(fig_rd, height=440, show_legend=False)

with rank_right:
    st.markdown(f"**{t('air.sec.rank_arr')}**")
    if arrivals.empty:
        empty_state()
    else:
        view = arrivals.head(15).sort_values("avg_delay").copy()
        view["axis_label"] = view["airport_code"] + " · " + view["city"].fillna(view["airport_name"])
        fig_ra = go.Figure(
            go.Bar(
                x=view["avg_delay"],
                y=view["axis_label"],
                orientation="h",
                marker={"color": PALETTE["cyan"]},
                customdata=np.column_stack(
                    [
                        view["airport_name"],
                        view["airport_code"],
                        view["city"].fillna("—"),
                        view["flight_count"],
                        view["delay_observations"],
                    ]
                ),
                hovertemplate=build_hover(
                    t("label.airport"),
                    "%{customdata[0]} (%{customdata[1]})",
                    [
                        (t("label.city"), "%{customdata[2]}"),
                        (t("label.avg_arr_delay"), f"%{{x:.2f}} {u_min}"),
                        (t("label.arrivals"), f"%{{customdata[3]:,.0f}} {u_flights}"),
                        (t("label.observed_delays"), "%{customdata[4]:,.0f}"),
                    ],
                ),
            )
        )
        fig_ra.update_xaxes(title=f"{t('label.avg_delay')} ({u_min})", showgrid=True, nticks=5, tickangle=0)
        fig_ra.update_yaxes(title="", showgrid=False)
        show_chart(fig_ra, height=440, show_legend=False)
        chart_caption(t("air.sec.rank_arr_cap"))

if selected:
    heatmap_airports = selected
    heatmap_sub = t("air.sec.heatmap_sub_focus", count=len(selected))
else:
    heatmap_airports = tuple(origin.head(10)["airport_code"].dropna().tolist())
    heatmap_sub = t("air.sec.heatmap_sub_default")

section_heading(t("air.sec.heatmap"), heatmap_sub)
if not heatmap_airports:
    empty_state()
else:
    with st.spinner(t("status.loading")):
        heat = airport_heatmap(filters, heatmap_airports)
    if heat.empty:
        empty_state()
    else:
        month_cols = sorted(heat["month"].unique())
        matrix = heat.pivot(index="airport_code", columns="month", values="avg_departure_delay")
        matrix = matrix.reindex(index=list(heatmap_airports), columns=month_cols)
        obs_matrix = heat.pivot(index="airport_code", columns="month", values="delay_observations")
        obs_matrix = obs_matrix.reindex(index=list(heatmap_airports), columns=month_cols).fillna(0)

        short_labels = [month_label(m, short=True) for m in month_cols]
        full_labels = [month_label(m, short=False) for m in month_cols]
        # Build (rows, cols, 2) customdata with [full_month, delay_observations]
        full_grid = np.tile(np.array(full_labels, dtype=object), (len(matrix.index), 1))
        custom = np.dstack([full_grid, obs_matrix.values])

        fig_hm = go.Figure(
            go.Heatmap(
                z=matrix.values,
                x=short_labels,
                y=matrix.index.tolist(),
                customdata=custom,
                xgap=3,
                ygap=3,
                colorscale=[
                    [0.00, "#1D3557"],
                    [0.30, "#2A6F97"],
                    [0.58, "#F5C451"],
                    [0.82, "#E5954B"],
                    [1.00, "#DC5349"],
                ],
                colorbar={
                    "title": {"text": t("air.colorbar.title"), "font": {"size": 11, "color": "#CBD5E1"}},
                    "tickfont": {"size": 11, "color": "#94A3B8"},
                    "thickness": 14,
                    "outlinewidth": 0,
                },
                hovertemplate=build_hover(
                    t("label.airport"),
                    "%{y} · %{customdata[0]} 2015",
                    [
                        (t("label.avg_dep_delay"), f"%{{z:.1f}} {u_min}"),
                        (t("label.observed_delays"), "%{customdata[1]:,.0f}"),
                    ],
                ),
            )
        )
        fig_hm.update_xaxes(title=t("label.month"), showgrid=False, side="bottom")
        fig_hm.update_yaxes(title=t("label.airport"), showgrid=False, autorange="reversed")
        show_chart(
            fig_hm,
            height=max(350, min(640, 120 + len(heatmap_airports) * 42)),
            show_legend=False,
            margin={"t": 26, "b": 36},
        )
        chart_caption(t("air.sec.heatmap_cap"))

with st.expander(t("air.table.expander")):
    combined = pd.concat(
        [
            origin.assign(endpoint=t("label.origin"), average_delay_metric=t("air.table.metric_dep")),
            destination.assign(endpoint=t("label.destination"), average_delay_metric=t("air.table.metric_arr")),
        ],
        ignore_index=True,
    )
    st.dataframe(
        combined,
        width="stretch",
        hide_index=True,
        column_config={
            "airport_code": "IATA",
            "airport_label": t("label.airport"),
            "endpoint": t("label.endpoint"),
            "average_delay_metric": t("label.metric"),
            "flight_count": st.column_config.NumberColumn(t("label.flights"), format="%,d"),
            "delay_observations": st.column_config.NumberColumn(t("label.observed_delays"), format="%,d"),
            "avg_delay": st.column_config.NumberColumn(f"{t('label.avg_delay')} ({u_min})", format="%.2f"),
        },
    )

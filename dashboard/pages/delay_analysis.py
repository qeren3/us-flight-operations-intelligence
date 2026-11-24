from __future__ import annotations

from html import escape

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from dashboard.components import (
    PALETTE,
    build_hover,
    chart_caption,
    empty_state,
    format_number,
    month_label,
    page_heading,
    scope_strip,
    section_heading,
    show_chart,
)
from dashboard.data_access import (
    airline_performance,
    delay_causes,
    delay_distribution,
    monthly_delay_causes,
)
from dashboard.i18n import delay_bin_label, t, upper_localized

filters = st.session_state.get("dashboard_filters", {})
page_heading(t("page.delays.title"), t("page.delays.desc"), section=t("page.delays.kicker"))
scope_strip(filters)

with st.spinner(t("status.loading")):
    causes = delay_causes(filters)
    monthly_causes = monthly_delay_causes(filters)
    airlines = airline_performance(filters)
    departure_distribution = delay_distribution(filters, "departure")
    arrival_distribution = delay_distribution(filters, "arrival")

u_hours = t("unit.hours")
u_flights = t("unit.flights")
u_min = t("unit.min")

CAUSE_SPECS: list[tuple[str, str, str]] = [
    ("late_aircraft_hours", "delay.cause.late_aircraft", PALETTE["causes"][0]),
    ("airline_hours", "delay.cause.airline", PALETTE["causes"][1]),
    ("nas_hours", "delay.cause.nas", PALETTE["causes"][2]),
    ("weather_hours", "delay.cause.weather", PALETTE["causes"][3]),
    ("security_hours", "delay.cause.security", PALETTE["causes"][4]),
]

section_heading(t("delay.sec.breakdown"), t("delay.sec.breakdown_sub"))
if causes.empty or causes.iloc[0].isna().all() or causes.iloc[0].fillna(0).sum() == 0:
    empty_state(t("status.empty_causes"))
else:
    row = causes.iloc[0]
    labels = [t(i18n_key) for _, i18n_key, _ in CAUSE_SPECS]
    colors = [color for _, _, color in CAUSE_SPECS]
    values = [float(row[col] or 0) for col, _, _ in CAUSE_SPECS]
    total_hours = sum(values)
    shares = [(v / total_hours * 100.0) if total_hours else 0.0 for v in values]

    # Show crisp inside percentage labels only on slices >= 5% so tiny slices (e.g. Security 0.13%)
    # never collide with legends or neighbor labels; all 5 causes appear in the companion breakdown panel.
    slice_text = [f"{pct:.1f}%" if pct >= 5.0 else "" for pct in shares]

    donut_col, summary_col = st.columns([1.35, 1.0], gap="medium")
    with donut_col:
        fig_pie = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.64,
                sort=False,
                direction="clockwise",
                text=slice_text,
                textinfo="text",
                textposition="inside",
                insidetextorientation="horizontal",
                insidetextfont={"size": 12.5, "color": "#0B1220", "family": "Inter, Segoe UI, sans-serif"},
                marker={"colors": colors, "line": {"color": "#162338", "width": 2.5}},
                customdata=shares,
                hovertemplate=build_hover(
                    t("label.cause"),
                    "%{label}",
                    [
                        (t("label.delay_hours"), f"%{{value:,.0f}} {u_hours}"),
                        (t("label.share"), "%{customdata:.2f}%"),
                    ],
                ),
            )
        )
        fig_pie.add_annotation(
            text=(
                f"<span style='font-size:10px;color:#94A3B8'>{escape(upper_localized(t('delay.summary.donut_label')))}</span>"
                f"<br><b style='font-size:18px;color:#F8FAFC'>{format_number(total_hours, 0)}</b>"
                f"<br><span style='font-size:11.5px;color:#94A3B8'>{escape(u_hours)}</span>"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            align="center",
        )
        show_chart(fig_pie, height=390, show_legend=False, margin={"t": 22, "b": 22, "l": 16, "r": 16})

    with summary_col:
        rows_html: list[str] = []
        for lbl, val, pct, col in zip(labels, values, shares, colors):
            bar_w = max(pct, 1.2) if val > 0 else 0.0
            rows_html.append(
                '<div class="cause-row">'
                '<div class="cause-row-top">'
                f'<span class="cause-name"><span class="cause-dot" style="background:{col};"></span>{escape(lbl)}</span>'
                f'<span class="cause-vals">{format_number(val, 0)} {escape(u_hours)}'
                f'<span class="cause-pct">({pct:.2f}%)</span></span>'
                '</div>'
                '<div class="cause-bar-track">'
                f'<div class="cause-bar-fill" style="width:{bar_w:.1f}%;background:{col};"></div>'
                '</div>'
                '</div>'
            )
        st.markdown(
            '<div class="cause-panel">'
            f'<div class="cause-panel-title">{escape(t("delay.summary.heading"))}</div>'
            f'{"".join(rows_html)}'
            '<div class="cause-total">'
            f'<span class="cause-total-label">{escape(t("delay.summary.total"))}</span>'
            f'<span class="cause-total-val">{format_number(total_hours, 0)} {escape(u_hours)}</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    chart_caption(t("delay.sec.breakdown_cap"))

section_heading(t("delay.sec.monthly_causes"), t("delay.sec.monthly_causes_sub"))
if monthly_causes.empty:
    empty_state()
else:
    mc = monthly_causes.sort_values("month").copy()
    mc["short_label"] = mc["month"].map(lambda m: month_label(m, short=True))
    mc["full_label"] = mc["month"].map(lambda m: month_label(m, short=False))
    short_order = mc["short_label"].tolist()

    fig_mc = go.Figure()
    for col, i18n_key, color in CAUSE_SPECS:
        cause_name = t(i18n_key)
        fig_mc.add_trace(
            go.Bar(
                x=mc["short_label"],
                y=mc[col].fillna(0),
                name=cause_name,
                marker={"color": color},
                customdata=mc["full_label"],
                hovertemplate=build_hover(
                    t("label.month"),
                    "%{customdata} 2015",
                    [
                        (t("label.cause"), cause_name),
                        (t("label.delay_hours"), f"%{{y:,.0f}} {u_hours}"),
                    ],
                ),
            )
        )
    fig_mc.update_layout(barmode="stack")
    fig_mc.update_xaxes(title=t("label.month"), categoryorder="array", categoryarray=short_order)
    fig_mc.update_yaxes(title=t("label.delay_hours"), tickformat=",")
    show_chart(fig_mc, height=415, show_legend=True)
    chart_caption(t("delay.sec.monthly_causes_cap"))

section_heading(t("delay.sec.airline_comp"), t("delay.sec.airline_comp_sub"))
if airlines.empty:
    empty_state()
else:
    top_air = airlines.head(12).iloc[::-1].copy()
    fig_ac = go.Figure()
    fig_ac.add_trace(
        go.Bar(
            x=top_air["avg_departure_delay"],
            y=top_air["airline_name"],
            name=t("label.departure"),
            orientation="h",
            marker={"color": PALETTE["gold"]},
            customdata=np.column_stack(
                [top_air["airline_name"], top_air["airline_code"], top_air["flight_count"]]
            ),
            hovertemplate=build_hover(
                t("label.airline"),
                "%{customdata[0]} (%{customdata[1]})",
                [
                    (t("label.delay_type"), t("label.departure")),
                    (t("label.avg_dep_delay"), f"%{{x:.2f}} {u_min}"),
                    (t("label.flights"), f"%{{customdata[2]:,.0f}} {u_flights}"),
                ],
            ),
        )
    )
    fig_ac.add_trace(
        go.Bar(
            x=top_air["avg_arrival_delay"],
            y=top_air["airline_name"],
            name=t("label.arrival"),
            orientation="h",
            marker={"color": PALETTE["cyan"]},
            customdata=np.column_stack(
                [top_air["airline_name"], top_air["airline_code"], top_air["flight_count"]]
            ),
            hovertemplate=build_hover(
                t("label.airline"),
                "%{customdata[0]} (%{customdata[1]})",
                [
                    (t("label.delay_type"), t("label.arrival")),
                    (t("label.avg_arr_delay"), f"%{{x:.2f}} {u_min}"),
                    (t("label.flights"), f"%{{customdata[2]:,.0f}} {u_flights}"),
                ],
            ),
        )
    )
    fig_ac.update_layout(barmode="group")
    fig_ac.update_xaxes(title=f"{t('label.avg_delay')} ({u_min})", showgrid=True, zeroline=True)
    fig_ac.update_yaxes(title="", showgrid=False)
    show_chart(fig_ac, height=460, show_legend=True)
    chart_caption(t("delay.sec.airline_comp_cap"))

section_heading(t("delay.sec.distributions"), t("delay.sec.distributions_sub"))
left, right = st.columns(2, gap="medium")
for column, frame, sub_title, bar_color in [
    (left, departure_distribution, t("delay.sec.dist_dep"), PALETTE["gold"]),
    (right, arrival_distribution, t("delay.sec.dist_arr"), PALETTE["cyan"]),
]:
    with column:
        st.markdown(f"**{sub_title}**")
        if frame.empty:
            empty_state()
        else:
            df_dist = frame.sort_values("bin_id").copy()
            df_dist["tick_range"] = [
                delay_bin_label(bid, raw, compact=True) for bid, raw in zip(df_dist["bin_id"], df_dist["delay_range"])
            ]
            df_dist["full_range"] = [
                delay_bin_label(bid, raw, compact=False) for bid, raw in zip(df_dist["bin_id"], df_dist["delay_range"])
            ]
            total_obs = float(df_dist["flight_count"].sum()) or 1.0
            df_dist["share_pct"] = df_dist["flight_count"].astype(float) / total_obs * 100.0
            cat_order = df_dist["tick_range"].tolist()

            fig_d = go.Figure(
                go.Bar(
                    x=df_dist["tick_range"],
                    y=df_dist["flight_count"],
                    marker={"color": bar_color},
                    customdata=np.column_stack([df_dist["full_range"], df_dist["share_pct"]]),
                    hovertemplate=build_hover(
                        t("label.delay_range"),
                        "%{customdata[0]}",
                        [
                            (t("label.flights"), f"%{{y:,.0f}} {u_flights}"),
                            (t("label.share"), "%{customdata[1]:.1f}%"),
                        ],
                    ),
                )
            )
            fig_d.update_xaxes(
                title=f"{t('label.delay_range')} ({u_min})",
                categoryorder="array",
                categoryarray=cat_order,
                tickangle=-35,
            )
            fig_d.update_yaxes(title=t("label.flights"), tickformat=",")
            show_chart(fig_d, height=400, show_legend=False, margin={"b": 64})

chart_caption(t("delay.sec.dist_cap"))

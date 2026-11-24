from __future__ import annotations

from html import escape

import streamlit as st

from dashboard.components import (
    chart_caption,
    format_number,
    kpi_grid,
    page_heading,
    section_heading,
    status_banner,
)
from dashboard.data_access import live_data_quality
from dashboard.i18n import t

page_heading(t("page.quality.title"), t("page.quality.desc"), section=t("page.quality.kicker"))

with st.spinner(t("status.loading")):
    live = live_data_quality().iloc[0]

expected_october = 486_165
live_total = int(live.live_total_rows)
live_oct = int(live.live_october_rows)
live_cw = int(live.live_crosswalk_rows)
unresolved_orig = int(live.unresolved_october_origins)
unresolved_dest = int(live.unresolved_october_destinations)
unresolved_total = unresolved_orig + unresolved_dest
orig_cov = int(live.october_origin_coverage)
dest_cov = int(live.october_destination_coverage)
missing_ref = int(live.crosswalk_codes_missing_reference)

passed = (
    live_total == 5_819_079
    and live_oct == expected_october
    and live_cw == 307
    and int(live.distinct_crosswalk_ids) == 307
    and int(live.distinct_crosswalk_sequences) == 307
    and missing_ref == 0
    and orig_cov == expected_october
    and dest_cov == expected_october
    and unresolved_orig == 0
    and unresolved_dest == 0
)

if passed:
    status_banner(
        t("dq.status.pass_body"),
        title=t("dq.status.pass_title"),
        tone="success",
        icon="shield",
    )
else:
    status_banner(
        t("dq.status.fail_body"),
        title=t("dq.status.fail_title"),
        tone="error",
        icon="alert",
    )

section_heading(t("dq.sec.historical"), t("dq.sec.historical_sub"))
kpi_grid(
    [
        {
            "label": t("dq.kpi.hist_flights"),
            "value": "5,819,079",
            "note": t("dq.kpi.hist_flights_note"),
            "icon": "database",
            "tone": "slate",
        },
        {
            "label": t("dq.kpi.hist_oct"),
            "value": "486,165",
            "note": t("dq.kpi.hist_oct_note"),
            "icon": "database",
            "tone": "slate",
        },
        {
            "label": t("dq.kpi.hist_crosswalk"),
            "value": "307",
            "note": t("dq.kpi.hist_crosswalk_note"),
            "icon": "map",
            "tone": "slate",
        },
        {
            "label": t("dq.kpi.hist_validation"),
            "value": t("dq.kpi.hist_validation_val"),
            "note": t("dq.kpi.hist_validation_note"),
            "icon": "check",
            "tone": "success",
        },
    ],
    columns_hint=4,
)
chart_caption(t("dq.sec.historical_cap"))

section_heading(t("dq.sec.live"), t("dq.sec.live_sub"))
kpi_grid(
    [
        {
            "label": t("dq.kpi.live_flights"),
            "value": format_number(live_total),
            "note": "public.flights_normalized",
            "icon": "database",
            "tone": "gold" if live_total == 5_819_079 else "error",
        },
        {
            "label": t("dq.kpi.live_oct"),
            "value": format_number(live_oct),
            "note": t("dq.kpi.live_oct_note"),
            "icon": "database",
            "tone": "cyan" if live_oct == expected_october else "error",
        },
        {
            "label": t("dq.kpi.live_crosswalk"),
            "value": format_number(live_cw),
            "note": t("dq.kpi.live_crosswalk_note"),
            "icon": "map",
            "tone": "cyan" if live_cw == 307 else "error",
        },
        {
            "label": t("dq.kpi.live_unresolved"),
            "value": format_number(unresolved_total),
            "note": t(
                "dq.kpi.live_unresolved_note",
                orig=format_number(unresolved_orig),
                dest=format_number(unresolved_dest),
            ),
            "icon": "shield" if unresolved_total == 0 else "alert",
            "tone": "success" if unresolved_total == 0 else "error",
        },
    ],
    columns_hint=4,
)

orig_pct = (100.0 * orig_cov / live_oct) if live_oct else 0.0
dest_pct = (100.0 * dest_cov / live_oct) if live_oct else 0.0
matched_cw = live_cw - missing_ref

kpi_grid(
    [
        {
            "label": t("dq.kpi.origin_cov"),
            "value": f"{format_number(orig_cov)} / {format_number(live_oct)}",
            "note": t("dq.kpi.cov_note", pct=f"{orig_pct:.2f}"),
            "icon": "check",
            "tone": "success" if orig_cov == live_oct else "warning",
        },
        {
            "label": t("dq.kpi.dest_cov"),
            "value": f"{format_number(dest_cov)} / {format_number(live_oct)}",
            "note": t("dq.kpi.cov_note", pct=f"{dest_pct:.2f}"),
            "icon": "check",
            "tone": "success" if dest_cov == live_oct else "warning",
        },
        {
            "label": t("dq.kpi.ref_integrity"),
            "value": f"{format_number(matched_cw)} / {format_number(live_cw)}",
            "unit": t("unit.codes"),
            "note": t("dq.kpi.ref_integrity_note", missing=format_number(missing_ref)),
            "icon": "shield",
            "tone": "success" if missing_ref == 0 else "error",
        },
    ],
    columns_hint=3,
)

section_heading(t("dq.sec.reconciled"))
body_html = escape(t("dq.sec.reconciled_body")).replace(
    "`public.flights_normalized`",
    "<code>public.flights_normalized</code>",
)
st.markdown(f'<div class="methodology-card">{body_html}</div>', unsafe_allow_html=True)
chart_caption(t("dq.sec.reconciled_cap"))

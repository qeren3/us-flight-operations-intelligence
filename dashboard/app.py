from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path before package imports when Streamlit runs dashboard/app.py.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

st.set_page_config(
    page_title="Flight Operations Intelligence",
    page_icon=":material/flight_takeoff:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.components import inject_styles, render_top_header, status_banner  # noqa: E402
from dashboard.data_access import DashboardDataError, filter_options  # noqa: E402
from dashboard.i18n import get_lang, month_name, t  # noqa: E402

# Initialize persisted language before building navigation so titles & filters render in the active language.
get_lang()
inject_styles()

# Stable language-independent url_path ensures switching TR | EN never navigates away or resets filters.
pages = [
    st.Page(
        "pages/executive_overview.py",
        title=t("page.executive.title"),
        icon=":material/dashboard:",
        url_path="executive_overview",
        default=True,
    ),
    st.Page(
        "pages/flight_operations.py",
        title=t("page.operations.title"),
        icon=":material/flight_takeoff:",
        url_path="flight_operations",
    ),
    st.Page(
        "pages/airport_intelligence.py",
        title=t("page.airports.title"),
        icon=":material/location_on:",
        url_path="airport_intelligence",
    ),
    st.Page(
        "pages/route_intelligence.py",
        title=t("page.routes.title"),
        icon=":material/alt_route:",
        url_path="route_intelligence",
    ),
    st.Page(
        "pages/delay_analysis.py",
        title=t("page.delays.title"),
        icon=":material/schedule:",
        url_path="delay_analysis",
    ),
    st.Page(
        "pages/data_quality.py",
        title=t("page.quality.title"),
        icon=":material/verified_user:",
        url_path="data_quality",
    ),
]
current_page = st.navigation(pages, position="sidebar", expanded=True)
active_slug = current_page.url_path or "executive_overview"

render_top_header()

filters: dict[str, object] = {}
sidebar = st.sidebar

if active_slug == "data_quality":
    sidebar.markdown(f'<div class="sidebar-section-label">{t("filter.heading")}</div>', unsafe_allow_html=True)
    sidebar.caption(t("filter.quality_note"))
    sidebar.markdown(f'<div class="sidebar-footnote">{t("filter.footnote")}</div>', unsafe_allow_html=True)
else:
    try:
        with st.spinner(t("status.loading")):
            options = filter_options()
    except DashboardDataError:
        status_banner(
            t("error.db_config_hint"),
            title=t("error.data_unavailable"),
            tone="error",
            icon="alert",
        )
        st.stop()

    lang = get_lang()
    lang_gen = int(st.session_state.get("dashboard_lang_gen", 0))
    defaults = {"months": list(options["months"]), "airlines": list(options["airlines"])}
    st.session_state["dashboard_filter_defaults"] = defaults

    # Canonical language-independent filter stores + generation-keyed widgets ensure
    # switching TR | EN mounts a fresh widget seeded from the canonical store so Streamlit's
    # frontend never replays stale values or drops months whose formatted labels changed.
    if "dashboard_months_store" not in st.session_state:
        st.session_state["dashboard_months_store"] = list(defaults["months"])
    if "dashboard_airlines" not in st.session_state:
        st.session_state["dashboard_airlines"] = list(defaults["airlines"])
    if "dashboard_airport_focus" not in st.session_state:
        st.session_state["dashboard_airport_focus"] = []
    if "dashboard_origin_store" not in st.session_state:
        st.session_state["dashboard_origin_store"] = "Any origin"
    if "dashboard_destination_store" not in st.session_state:
        st.session_state["dashboard_destination_store"] = "Any destination"

    months_widget_key = f"dashboard_months_{lang}_{lang_gen}"
    origin_widget_key = f"dashboard_origin_{lang}_{lang_gen}"
    dest_widget_key = f"dashboard_destination_{lang}_{lang_gen}"

    if months_widget_key not in st.session_state:
        st.session_state[months_widget_key] = list(st.session_state["dashboard_months_store"])
    if origin_widget_key not in st.session_state:
        st.session_state[origin_widget_key] = st.session_state["dashboard_origin_store"]
    if dest_widget_key not in st.session_state:
        st.session_state[dest_widget_key] = st.session_state["dashboard_destination_store"]

    def _sync_months(widget_key: str) -> None:
        st.session_state["dashboard_months_store"] = list(st.session_state[widget_key])

    def _sync_origin(widget_key: str) -> None:
        st.session_state["dashboard_origin_store"] = st.session_state[widget_key]

    def _sync_destination(widget_key: str) -> None:
        st.session_state["dashboard_destination_store"] = st.session_state[widget_key]

    def reset_filters() -> None:
        all_months = list(st.session_state["dashboard_filter_defaults"]["months"])
        all_airlines = list(st.session_state["dashboard_filter_defaults"]["airlines"])
        st.session_state["dashboard_months_store"] = list(all_months)
        st.session_state["dashboard_airlines"] = list(all_airlines)
        st.session_state["dashboard_airport_focus"] = []
        st.session_state["dashboard_origin_store"] = "Any origin"
        st.session_state["dashboard_destination_store"] = "Any destination"
        cur_lang = get_lang()
        cur_gen = int(st.session_state.get("dashboard_lang_gen", 0))
        st.session_state[f"dashboard_months_{cur_lang}_{cur_gen}"] = list(all_months)
        st.session_state[f"dashboard_origin_{cur_lang}_{cur_gen}"] = "Any origin"
        st.session_state[f"dashboard_destination_{cur_lang}_{cur_gen}"] = "Any destination"

    sidebar.markdown(f'<div class="sidebar-section-label">{t("filter.heading")}</div>', unsafe_allow_html=True)
    sidebar.multiselect(
        t("filter.months"),
        options=options["months"],
        format_func=lambda month: month_name(int(month)),
        key=months_widget_key,
        on_change=_sync_months,
        args=(months_widget_key,),
        placeholder=t("filter.placeholder"),
        help=t("filter.months_help"),
    )
    sidebar.multiselect(
        t("filter.airlines"),
        options=options["airlines"],
        format_func=lambda code: f"{options['airline_labels'].get(code, code)} ({code})",
        key="dashboard_airlines",
        placeholder=t("filter.placeholder"),
        help=t("filter.airlines_help"),
    )

    if active_slug == "airport_intelligence":
        sidebar.markdown(f'<div class="sidebar-group-label">{t("filter.page_group")}</div>', unsafe_allow_html=True)
        sidebar.multiselect(
            t("filter.airport_focus"),
            options=options["airports"],
            format_func=lambda code: options["airport_labels"].get(code, code),
            key="dashboard_airport_focus",
            placeholder=t("filter.placeholder"),
            help=t("filter.airport_focus_help"),
        )
    if active_slug == "route_intelligence":
        sidebar.markdown(f'<div class="sidebar-group-label">{t("filter.page_group")}</div>', unsafe_allow_html=True)
        airport_options = ["Any origin", *options["airports"]]
        destination_options = ["Any destination", *options["airports"]]
        sidebar.selectbox(
            t("filter.origin"),
            airport_options,
            format_func=lambda code: t("filter.any_origin") if code == "Any origin" else options["airport_labels"].get(code, code),
            key=origin_widget_key,
            on_change=_sync_origin,
            args=(origin_widget_key,),
            help=t("filter.origin_help"),
        )
        sidebar.selectbox(
            t("filter.destination"),
            destination_options,
            format_func=lambda code: t("filter.any_destination") if code == "Any destination" else options["airport_labels"].get(code, code),
            key=dest_widget_key,
            on_change=_sync_destination,
            args=(dest_widget_key,),
            help=t("filter.destination_help"),
        )

    sidebar.button(
        t("filter.reset"),
        on_click=reset_filters,
        help=t("filter.reset_help"),
        width="stretch",
    )
    sidebar.markdown(f'<div class="sidebar-footnote">{t("filter.footnote")}</div>', unsafe_allow_html=True)

    filters = {
        "months": tuple(st.session_state.get("dashboard_months_store", defaults["months"])),
        "airlines": tuple(st.session_state.get("dashboard_airlines", defaults["airlines"])),
        "airport_focus": tuple(st.session_state.get("dashboard_airport_focus", ())),
        "route_origin": st.session_state.get("dashboard_origin_store", "Any origin"),
        "route_destination": st.session_state.get("dashboard_destination_store", "Any destination"),
    }
    st.session_state["dashboard_filters"] = filters

try:
    current_page.run()
except DashboardDataError:
    status_banner(
        t("error.cache_hint"),
        title=t("error.data_unavailable"),
        tone="error",
        icon="alert",
    )

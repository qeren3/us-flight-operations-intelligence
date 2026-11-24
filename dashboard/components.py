"""Shared design system, layout primitives, KPI grids, and Plotly styling."""

from __future__ import annotations

from html import escape
from typing import Any, Mapping, Sequence

import plotly.graph_objects as go
import streamlit as st

from dashboard.i18n import MONTHS_SHORT, get_lang, month_name, set_lang, t, upper_localized

# Backward-compatible export (English short month map)
MONTHS = MONTHS_SHORT["en"]

# Cohesive aviation dark-navy design tokens
PALETTE: dict[str, Any] = {
    "bg": "#0B1220",
    "bg_secondary": "#111C2E",
    "card": "#162338",
    "elevated": "#1B2B43",
    "border": "#233652",
    "border_strong": "#324A6D",
    "gold": "#F5C451",
    "cyan": "#38BDF8",
    "amber": "#E5954B",
    "blue": "#60A5FA",
    "slate": "#94A3B8",
    "muted": "#64748B",
    "text": "#F1F5F9",
    "text_bright": "#F8FAFC",
    "success": "#34D399",
    "warning": "#F59E0B",
    "error": "#F87171",
    "causes": ["#F5C451", "#E5954B", "#38BDF8", "#60A5FA", "#94A3B8"],
    "routes": [
        "#F5C451", "#38BDF8", "#34D399", "#E5954B", "#A78BFA",
        "#60A5FA", "#F472B6", "#FBBF24", "#2DD4BF", "#94A3B8",
    ],
}

# Minimal inline SVG icons (16x16, stroke-based, aviation/analytics vocabulary)
_ICONS: dict[str, str] = {
    "flight": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "arrival": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M4 20h16"/></svg>',
    "cancel": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
    "divert": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M4 20 21 3"/><path d="M21 16v5h-5"/><path d="m15 15 6 6"/></svg>',
    "database": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5"/><path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3"/></svg>',
    "check": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "map": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6-5.33-6-10a6 6 0 1 1 12 0c0 4.67-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
    "alert": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
}

_BRAND_MARK_SVG = (
    '<svg viewBox="0 0 32 32" width="28" height="28" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="1" y="1" width="30" height="30" rx="8" fill="#162338" stroke="#324A6D" stroke-width="1.2"/>'
    '<path d="M22.5 9.5 14.8 17.2m7.7-7.7-4.9 12.6-2.8-4.9-4.9-2.8 12.6-4.9Z" '
    'stroke="#F5C451" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

_TONE_COLORS: dict[str, tuple[str, str, str]] = {
    # (accent_color, soft_bg, border_color)
    "gold": ("#F5C451", "rgba(245, 196, 81, 0.08)", "rgba(245, 196, 81, 0.30)"),
    "cyan": ("#38BDF8", "rgba(56, 189, 248, 0.08)", "rgba(56, 189, 248, 0.28)"),
    "success": ("#34D399", "rgba(52, 211, 153, 0.09)", "rgba(52, 211, 153, 0.34)"),
    "warning": ("#F59E0B", "rgba(245, 158, 11, 0.09)", "rgba(245, 158, 11, 0.34)"),
    "error": ("#F87171", "rgba(248, 113, 113, 0.09)", "rgba(248, 113, 113, 0.36)"),
    "slate": ("#64748B", "rgba(100, 116, 139, 0.10)", "rgba(148, 163, 184, 0.24)"),
}


def inject_styles() -> None:
    """Inject the unified dark-navy aviation CSS system."""
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

          :root {
            --bg-canvas: #0B1220;
            --bg-sidebar: #111C2E;
            --bg-card: #162338;
            --bg-elevated: #1B2B43;
            --border-subtle: #233652;
            --border-strong: #324A6D;
            --accent-gold: #F5C451;
            --accent-cyan: #38BDF8;
            --text-primary: #F1F5F9;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --status-success: #34D399;
            --status-warning: #F59E0B;
            --status-error: #F87171;
          }

          html, body, [class*="css"], .stApp {
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            color: var(--text-primary);
          }

          .stApp {
            background-color: var(--bg-canvas);
            background-image: radial-gradient(900px 420px at 14% 0%, rgba(27, 43, 67, 0.45), transparent 72%);
          }

          /* Keep top chrome subtle and uncluttered */
          [data-testid="stHeader"] {
            background: rgba(11, 18, 32, 0.82);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid rgba(35, 54, 82, 0.5);
          }
          [data-testid="stToolbar"] {
            opacity: 0.72;
          }
          [data-testid="stToolbar"]:hover {
            opacity: 1;
          }

          .block-container {
            padding-top: 3.1rem;
            padding-bottom: 2.75rem;
            padding-left: 2.25rem;
            padding-right: 2.25rem;
            max-width: 1520px;
          }

          /* Sidebar surface & refined navigation */
          [data-testid="stSidebar"] {
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-subtle);
          }
          [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.1rem;
          }
          [data-testid="stSidebarNav"] {
            padding-bottom: 0.75rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-subtle);
          }
          [data-testid="stSidebarNav"] ul {
            gap: 4px;
            padding: 0 0.6rem;
          }
          [data-testid="stSidebarNavLink"] {
            border-radius: 9px;
            padding: 0.52rem 0.78rem !important;
            border: 1px solid transparent;
            color: var(--text-secondary) !important;
            transition: background-color 140ms ease, border-color 140ms ease, color 140ms ease;
          }
          [data-testid="stSidebarNavLink"]:hover {
            background-color: var(--bg-card) !important;
            border-color: var(--border-subtle);
            color: var(--text-primary) !important;
          }
          [data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: var(--bg-elevated) !important;
            border-color: var(--border-strong);
            border-left: 3px solid var(--accent-gold) !important;
            color: #F8FAFC !important;
            font-weight: 600 !important;
          }
          [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #F8FAFC !important;
            font-weight: 600 !important;
          }

          /* Sidebar filter labels & restrained multi-select chips */
          .sidebar-section-label {
            font-size: 0.70rem;
            font-weight: 700;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            color: var(--accent-gold);
            margin: 0.25rem 0 0.65rem 0;
          }
          .sidebar-group-label {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 0.85rem 0 0.35rem 0;
            padding-top: 0.65rem;
            border-top: 1px solid rgba(35, 54, 82, 0.7);
          }
          [data-testid="stSidebar"] label p {
            font-size: 0.83rem !important;
            font-weight: 500 !important;
            color: var(--text-primary) !important;
          }
          [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: var(--bg-card) !important;
            border-color: var(--border-subtle) !important;
            border-radius: 9px !important;
          }
          [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
            border-color: var(--accent-gold) !important;
            box-shadow: 0 0 0 1px rgba(245, 196, 81, 0.25) !important;
          }
          /* Refined slate tags instead of bright solid yellow pills */
          [data-testid="stSidebar"] span[data-baseweb="tag"],
          [data-testid="stSidebar"] [data-baseweb="tag"] {
            background-color: #1B2B43 !important;
            border: 1px solid #324A6D !important;
            color: #E2E8F0 !important;
            border-radius: 6px !important;
            font-size: 0.76rem !important;
            font-weight: 500 !important;
            padding: 1px 6px !important;
          }
          [data-testid="stSidebar"] span[data-baseweb="tag"] span,
          [data-testid="stSidebar"] [data-baseweb="tag"] span {
            color: #E2E8F0 !important;
          }
          [data-testid="stSidebar"] span[data-baseweb="tag"] svg,
          [data-testid="stSidebar"] [data-baseweb="tag"] svg {
            color: #94A3B8 !important;
            fill: #94A3B8 !important;
          }
          [data-testid="stSidebar"] span[data-baseweb="tag"] svg:hover,
          [data-testid="stSidebar"] [data-baseweb="tag"] svg:hover {
            color: #F5C451 !important;
            fill: #F5C451 !important;
          }
          [data-testid="stSidebar"] .stButton > button {
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 9px !important;
            font-weight: 600 !important;
            font-size: 0.84rem !important;
            padding: 0.48rem 0.9rem !important;
            margin-top: 0.4rem;
            transition: background-color 140ms ease, border-color 140ms ease;
          }
          [data-testid="stSidebar"] .stButton > button:hover {
            background-color: var(--bg-elevated) !important;
            border-color: var(--accent-gold) !important;
            color: #F8FAFC !important;
          }
          .sidebar-footnote {
            font-size: 0.74rem;
            line-height: 1.45;
            color: var(--text-muted);
            margin-top: 0.8rem;
            padding-top: 0.7rem;
            border-top: 1px solid rgba(35, 54, 82, 0.65);
          }

          /* Global Top Header */
          .app-brand-lockup {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            min-height: 38px;
          }
          .app-brand-text {
            display: flex;
            flex-direction: column;
            gap: 2px;
            min-width: 0;
          }
          .app-brand-title-row {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            flex-wrap: wrap;
          }
          .app-brand-title {
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: var(--accent-gold);
            line-height: 1.2;
          }
          .app-brand-badge {
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 999px;
            padding: 0.1rem 0.5rem;
          }
          .app-brand-subtitle {
            font-size: 0.78rem;
            color: var(--text-secondary);
            line-height: 1.25;
          }
          .app-header-divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(50, 74, 109, 0.85) 0%, rgba(35, 54, 82, 0.35) 100%);
            margin: 0.55rem 0 1.45rem 0;
          }

          /* Top-right TR | EN segmented language switcher */
          .lang-sep {
            text-align: center;
            color: var(--border-strong);
            font-weight: 600;
            font-size: 0.85rem;
            user-select: none;
            line-height: 1;
          }
          div.st-key-lang_switcher_shell {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 9px;
            padding: 4px 6px;
          }
          div.st-key-lang_btn_tr button,
          div.st-key-lang_btn_en button {
            min-height: 30px !important;
            height: 30px !important;
            min-width: 44px !important;
            padding: 0 0.4rem !important;
            border-radius: 6px !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.05em !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
            line-height: 1 !important;
          }
          div.st-key-lang_btn_tr button p,
          div.st-key-lang_btn_en button p {
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
          }
          div.st-key-lang_btn_tr button[kind="primary"],
          div.st-key-lang_btn_en button[kind="primary"] {
            background-color: var(--accent-gold) !important;
            color: #0B1220 !important;
            border: 1px solid var(--accent-gold) !important;
          }
          div.st-key-lang_btn_tr button[kind="secondary"],
          div.st-key-lang_btn_en button[kind="secondary"] {
            background-color: transparent !important;
            color: var(--text-secondary) !important;
            border: 1px solid transparent !important;
          }
          div.st-key-lang_btn_tr button[kind="secondary"]:hover,
          div.st-key-lang_btn_en button[kind="secondary"]:hover {
            background-color: var(--bg-elevated) !important;
            color: var(--text-primary) !important;
          }

          /* Page Heading & Active Scope Bar */
          .page-hero {
            margin-bottom: 1.25rem;
          }
          .page-kicker {
            color: var(--accent-gold);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
          }
          .page-title {
            color: #F8FAFC;
            font-size: clamp(1.55rem, 2.2vw, 2.05rem);
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.18;
            margin: 0 0 0.35rem 0;
          }
          .page-description {
            color: var(--text-secondary);
            font-size: 0.94rem;
            line-height: 1.5;
            max-width: 78ch;
            margin: 0;
          }
          .scope-strip {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.45rem;
            margin: 0.75rem 0 1.35rem 0;
          }
          .scope-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.75rem;
            font-weight: 500;
            color: #CBD5E1;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 999px;
            padding: 0.22rem 0.68rem;
            font-variant-numeric: tabular-nums;
          }
          .scope-chip-accent {
            border-color: rgba(245, 196, 81, 0.42);
            color: #FDE68A;
            background: rgba(245, 196, 81, 0.08);
          }

          /* Responsive KPI Grid — prevents cramped columns and mid-word wrapping */
          .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
            gap: 0.9rem;
            margin: 0.2rem 0 1.35rem 0;
          }
          .kpi-grid-4 {
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          }
          .kpi-grid-3 {
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          }
          .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-top: 2px solid var(--kpi-accent, var(--accent-gold));
            border-radius: 12px;
            padding: 1rem 1.15rem 0.95rem 1.15rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 112px;
            transition: border-color 150ms ease, background-color 150ms ease;
          }
          .kpi-card:hover {
            border-color: var(--border-strong);
            border-top-color: var(--kpi-accent, var(--accent-gold));
            background: #182740;
          }
          .kpi-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            margin-bottom: 0.55rem;
          }
          .kpi-label {
            color: var(--text-secondary);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            line-height: 1.3;
            word-break: normal;
            overflow-wrap: break-word;
          }
          .kpi-icon {
            color: var(--kpi-accent, var(--accent-gold));
            opacity: 0.85;
            flex-shrink: 0;
            display: inline-flex;
          }
          .kpi-value {
            color: #F8FAFC;
            font-size: clamp(1.32rem, 1.7vw, 1.68rem);
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: -0.015em;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
          }
          .kpi-unit {
            font-size: 0.86rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-left: 0.25rem;
          }
          .kpi-note {
            color: var(--text-secondary);
            font-size: 0.76rem;
            line-height: 1.35;
            margin-top: 0.45rem;
            font-variant-numeric: tabular-nums;
          }

          /* Section Headers */
          .sec-header {
            margin: 1.35rem 0 0.55rem 0;
          }
          .sec-title {
            color: #F1F5F9;
            font-size: 1.06rem;
            font-weight: 650;
            letter-spacing: -0.01em;
            line-height: 1.3;
            margin: 0;
          }
          .sec-sub {
            color: var(--text-secondary);
            font-size: 0.83rem;
            line-height: 1.4;
            margin: 0.18rem 0 0 0;
          }

          /* Semantic Callouts / Insights / Status Banners */
          .callout-banner {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 0.9rem 1.05rem;
            border-radius: 10px;
            border: 1px solid var(--callout-border);
            border-left: 3px solid var(--callout-accent);
            background: var(--callout-bg);
            margin: 0.35rem 0 1.2rem 0;
          }
          .callout-icon {
            color: var(--callout-accent);
            flex-shrink: 0;
            margin-top: 2px;
          }
          .callout-title {
            color: #F8FAFC;
            font-size: 0.90rem;
            font-weight: 650;
            margin-bottom: 0.18rem;
          }
          .callout-body {
            color: #CBD5E1;
            font-size: 0.85rem;
            line-height: 1.5;
          }

          /* Cause breakdown companion card on Delay Analysis */
          .cause-panel {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.05rem 1.15rem;
            height: 100%;
          }
          .cause-panel-title {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 0.85rem;
          }
          .cause-row {
            margin-bottom: 0.72rem;
          }
          .cause-row-top {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
          }
          .cause-name {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.84rem;
            font-weight: 500;
            color: var(--text-primary);
          }
          .cause-dot {
            width: 9px;
            height: 9px;
            border-radius: 999px;
            flex-shrink: 0;
          }
          .cause-vals {
            font-size: 0.82rem;
            font-variant-numeric: tabular-nums;
            color: #CBD5E1;
            white-space: nowrap;
          }
          .cause-pct {
            color: var(--text-secondary);
            margin-left: 0.35rem;
            font-size: 0.77rem;
          }
          .cause-bar-track {
            height: 5px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.14);
            overflow: hidden;
          }
          .cause-bar-fill {
            height: 100%;
            border-radius: 999px;
          }
          .cause-total {
            margin-top: 0.9rem;
            padding-top: 0.7rem;
            border-top: 1px solid var(--border-subtle);
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.6rem;
            flex-wrap: wrap;
            font-size: 0.83rem;
          }
          .cause-total-label {
            color: var(--text-secondary);
            font-weight: 500;
          }
          .cause-total-val {
            color: #F8FAFC;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
          }

          /* Plotly Chart & Dataframe Surface Cards */
          div[data-testid="stPlotlyChart"] {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 0.55rem 0.55rem 0.35rem 0.55rem;
            overflow: hidden;
          }
          div[data-testid="stDataFrame"] {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            overflow: hidden;
          }
          [data-testid="stExpander"] {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
          }
          [data-testid="stExpander"] summary p {
            font-weight: 600;
            color: var(--text-primary);
          }

          .methodology-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.05rem 1.2rem;
            color: #CBD5E1;
            font-size: 0.88rem;
            line-height: 1.62;
          }
          .methodology-card code {
            background: var(--bg-elevated);
            color: #FDE68A;
            padding: 0.1rem 0.38rem;
            border-radius: 5px;
            font-size: 0.82rem;
          }

          .chart-caption {
            color: var(--text-secondary);
            font-size: 0.78rem;
            line-height: 1.45;
            margin-top: 0.35rem;
            margin-bottom: 0.75rem;
          }

          /* Responsive adjustments */
          @media (max-width: 960px) {
            .block-container {
              padding-left: 1.15rem;
              padding-right: 1.15rem;
            }
            .kpi-grid {
              grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
            }
          }
          @media (max-width: 640px) {
            .app-brand-subtitle {
              display: none;
            }
            .kpi-grid, .kpi-grid-4, .kpi-grid-3 {
              grid-template-columns: 1fr;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_header() -> None:
    """Render the consistent global top header with top-right TR | EN switcher."""
    lang = get_lang()
    left, right = st.columns([4.2, 1.55], vertical_alignment="center")
    with left:
        st.markdown(
            '<div class="app-brand-lockup">'
            f'{_BRAND_MARK_SVG}'
            '<div class="app-brand-text">'
            '<div class="app-brand-title-row">'
            f'<span class="app-brand-title">{escape(t("brand.name"))}</span>'
            f'<span class="app-brand-badge">{escape(t("brand.badge"))}</span>'
            '</div>'
            f'<div class="app-brand-subtitle">{escape(t("brand.subtitle"))}</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with right:
        with st.container(key="lang_switcher_shell"):
            c_tr, c_sep, c_en = st.columns([1, 0.2, 1], gap="small", vertical_alignment="center")
            with c_tr:
                st.button(
                    "TR",
                    key="lang_btn_tr",
                    type="primary" if lang == "tr" else "secondary",
                    on_click=set_lang,
                    args=("tr",),
                    help=t("lang.tr_help"),
                    width="stretch",
                )
            with c_sep:
                st.markdown('<div class="lang-sep">|</div>', unsafe_allow_html=True)
            with c_en:
                st.button(
                    "EN",
                    key="lang_btn_en",
                    type="primary" if lang == "en" else "secondary",
                    on_click=set_lang,
                    args=("en",),
                    help=t("lang.en_help"),
                    width="stretch",
                )
    st.markdown('<div class="app-header-divider"></div>', unsafe_allow_html=True)


def brand_header() -> None:
    """Alias kept for backward compatibility; delegates to render_top_header()."""
    render_top_header()


def page_heading(title: str, description: str, section: str = "FLIGHT ANALYTICS") -> None:
    """Render a consistent page header with kicker, title, and description."""
    st.markdown(
        '<div class="page-hero">'
        f'<div class="page-kicker">{escape(section)}</div>'
        f'<h1 class="page-title">{escape(title)}</h1>'
        f'<p class="page-description">{escape(description)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def scope_strip(filters: Mapping[str, Any], *, extra_chips: Sequence[str] = ()) -> None:
    """Render compact active-scope pills under the page title."""
    months = tuple(filters.get("months", ()))
    airlines = tuple(filters.get("airlines", ()))
    defaults = st.session_state.get("dashboard_filter_defaults", {})
    total_airlines = len(defaults.get("airlines", airlines)) or 14

    if len(months) == 12:
        month_chip = t("scope.months_all")
    elif not months:
        month_chip = t("scope.months_none")
    elif len(months) <= 3:
        month_chip = ", ".join(month_name(m) for m in sorted(months))
    else:
        month_chip = t("scope.months_count", count=len(months))

    if len(airlines) == total_airlines:
        airline_chip = t("scope.airlines_all", count=total_airlines)
    elif not airlines:
        airline_chip = t("scope.airlines_none")
    elif len(airlines) <= 3:
        airline_chip = ", ".join(sorted(airlines))
    else:
        airline_chip = t("scope.airlines_count", count=len(airlines), total=total_airlines)

    chips = [
        f'<span class="scope-chip">{escape(month_chip)}</span>',
        f'<span class="scope-chip">{escape(airline_chip)}</span>',
    ]
    for extra in extra_chips:
        chips.append(f'<span class="scope-chip scope-chip-accent">{escape(extra)}</span>')

    st.markdown(f'<div class="scope-strip">{"".join(chips)}</div>', unsafe_allow_html=True)


def section_heading(title: str, subtitle: str = "") -> None:
    """Render a structured section header above charts or tables."""
    sub_html = f'<p class="sec-sub">{escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="sec-header"><h2 class="sec-title">{escape(title)}</h2>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(
    label: str,
    value: str,
    note: str = "",
    *,
    unit: str = "",
    icon: str = "",
    tone: str = "gold",
) -> None:
    """Render a single KPI card (for standalone use)."""
    kpi_grid([{"label": label, "value": value, "note": note, "unit": unit, "icon": icon, "tone": tone}])


def kpi_grid(cards: Sequence[Mapping[str, str]], *, columns_hint: int = 5) -> None:
    """Render a responsive CSS-grid strip of polished KPI cards."""
    grid_class = "kpi-grid"
    if columns_hint == 4:
        grid_class = "kpi-grid kpi-grid-4"
    elif columns_hint == 3:
        grid_class = "kpi-grid kpi-grid-3"

    parts: list[str] = []
    for card in cards:
        tone = card.get("tone", "gold")
        accent = _TONE_COLORS.get(tone, _TONE_COLORS["gold"])[0]
        icon_svg = _ICONS.get(card.get("icon", ""), "")
        icon_html = f'<span class="kpi-icon">{icon_svg}</span>' if icon_svg else ""
        unit = card.get("unit", "")
        unit_html = f'<span class="kpi-unit">{escape(unit)}</span>' if unit else ""
        note = card.get("note", "")
        note_html = f'<div class="kpi-note">{escape(note)}</div>' if note else ""
        parts.append(
            f'<div class="kpi-card" style="--kpi-accent:{accent};">'
            '<div class="kpi-top">'
            f'<div class="kpi-label">{escape(card["label"])}</div>'
            f'{icon_html}'
            '</div>'
            f'<div class="kpi-value">{escape(card["value"])}{unit_html}</div>'
            f'{note_html}'
            '</div>'
        )
    st.markdown(f'<div class="{grid_class}">{"".join(parts)}</div>', unsafe_allow_html=True)


def status_banner(body: str, *, title: str = "", tone: str = "gold", icon: str = "") -> None:
    """Render a restrained semantic callout / insight / validation banner."""
    accent, bg, border = _TONE_COLORS.get(tone, _TONE_COLORS["gold"])
    icon_svg = _ICONS.get(icon, "")
    icon_html = f'<div class="callout-icon">{icon_svg}</div>' if icon_svg else ""
    title_html = f'<div class="callout-title">{escape(title)}</div>' if title else ""
    st.markdown(
        f'<div class="callout-banner" style="--callout-accent:{accent};--callout-bg:{bg};--callout-border:{border};">'
        f'{icon_html}'
        f'<div>{title_html}<div class="callout-body">{escape(body)}</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def chart_caption(text: str) -> None:
    """Render a crisp, restrained methodological caption beneath a chart."""
    st.markdown(f'<div class="chart-caption">{escape(text)}</div>', unsafe_allow_html=True)


def empty_state(message: str | None = None) -> None:
    """Render a localized empty-filter state banner."""
    status_banner(message or t("status.empty"), tone="slate", icon="alert")


def build_hover(
    header_label: str,
    header_expr: str,
    rows: Sequence[tuple[str, str]],
    *,
    subtitle_expr: str = "",
) -> str:
    """Build a consistent, airy, left-aligned Plotly hovertemplate with no extra trace tag."""
    lines = [
        f"<span style='color:#94A3B8;font-size:10.5px'>{escape(upper_localized(header_label))}</span>",
        f"<b style='font-size:13.5px;color:#F8FAFC'>{header_expr}</b>",
    ]
    if subtitle_expr:
        lines.append(f"<span style='color:#94A3B8;font-size:11.5px'>{subtitle_expr}</span>")
    lines.append("")
    for label, value_expr in rows:
        lines.append(
            f"<span style='color:#94A3B8'>{escape(label)}:</span> "
            f"<b style='color:#F1F5F9'>{value_expr}</b>"
        )
    return "<br>".join(lines) + "<extra></extra>"


def chart_theme(
    fig: go.Figure,
    *,
    height: int = 380,
    show_legend: bool = True,
    legend_orientation: str = "h",
    hovermode: str = "closest",
    margin: dict[str, int] | None = None,
) -> go.Figure:
    """Apply the unified aviation analytics theme and legible hover styling to a Plotly figure."""
    default_margin = {"l": 20, "r": 24, "t": 44, "b": 28}
    if margin:
        default_margin.update(margin)

    legend_cfg: dict[str, Any] = {
        "orientation": legend_orientation,
        "font": {"size": 12, "color": "#CBD5E1"},
        "bgcolor": "rgba(0,0,0,0)",
        "itemsizing": "constant",
    }
    if legend_orientation == "h":
        legend_cfg.update({"y": 1.13, "x": 0, "yanchor": "bottom", "xanchor": "left", "title": None})
    else:
        legend_cfg.update({"y": 0.5, "x": 1.03, "yanchor": "middle", "xanchor": "left", "title": None})

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, system-ui, sans-serif", "color": "#CBD5E1", "size": 12},
        title={"text": None},
        height=height,
        margin=default_margin,
        showlegend=show_legend,
        legend=legend_cfg,
        hovermode=hovermode,
        hoverdistance=28,
        hoverlabel={
            "bgcolor": "#1B2B43",
            "bordercolor": "#3B5578",
            "font": {"family": "Inter, Segoe UI, system-ui, sans-serif", "size": 12, "color": "#F1F5F9"},
            "align": "left",
            "namelength": -1,
        },
        bargap=0.26,
        bargroupgap=0.10,
    )
    fig.update_xaxes(
        showgrid=False,
        gridcolor="rgba(148, 163, 184, 0.12)",
        zerolinecolor="rgba(148, 163, 184, 0.24)",
        tickfont={"color": "#94A3B8", "size": 11.5},
        title_font={"color": "#CBD5E1", "size": 12.5},
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, 0.12)",
        zerolinecolor="rgba(148, 163, 184, 0.24)",
        tickfont={"color": "#94A3B8", "size": 11.5},
        title_font={"color": "#CBD5E1", "size": 12.5},
        automargin=True,
    )
    return fig


def show_chart(
    fig: go.Figure,
    *,
    height: int = 380,
    key: str | None = None,
    show_legend: bool = True,
    legend_orientation: str = "h",
    hovermode: str = "closest",
    margin: dict[str, int] | None = None,
) -> None:
    """Theme and render a responsive Plotly chart without deprecated Streamlit flags."""
    chart_theme(
        fig,
        height=height,
        show_legend=show_legend,
        legend_orientation=legend_orientation,
        hovermode=hovermode,
        margin=margin,
    )
    st.plotly_chart(
        fig,
        width="stretch",
        config={"displaylogo": False, "responsive": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
        key=key,
    )


def month_label(month: Any, *, short: bool = True) -> str:
    """Return the localized month label for the active UI language."""
    return month_name(month, short=short)


def format_number(value: Any, decimals: int = 0) -> str:
    """Format a numeric KPI value with thousands separators, or em-dash for NULL/NaN."""
    if value is None:
        return "—"
    try:
        if value != value:
            return "—"
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"

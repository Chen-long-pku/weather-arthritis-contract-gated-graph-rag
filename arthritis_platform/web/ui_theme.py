"""
Streamlit visual theme helpers for the arthritis knowledge graph platform.
"""

from html import escape
from typing import Iterable, Mapping

import streamlit as st


THEMES = {
    "home": {
        "accent": "#4d7f70",
        "accent_dark": "#2f5c50",
        "accent_soft": "#eaf4ef",
        "warm": "#b8745e",
        "warm_soft": "#fff0e8",
        "surface": "#ffffff",
        "page": "#f7faf6",
        "muted": "#68746f",
        "ink": "#202b27",
    },
    "public": {
        "accent": "#2f8f7b",
        "accent_dark": "#1f6457",
        "accent_soft": "#e8f5f1",
        "warm": "#d46b4d",
        "warm_soft": "#fff1ea",
        "surface": "#ffffff",
        "page": "#f6faf8",
        "muted": "#66736f",
        "ink": "#1d2926",
    },
    "medical": {
        "accent": "#3f7893",
        "accent_dark": "#28546a",
        "accent_soft": "#e8f2f6",
        "warm": "#c8644d",
        "warm_soft": "#fff1ec",
        "surface": "#ffffff",
        "page": "#f7faf9",
        "muted": "#687278",
        "ink": "#1f2b32",
    },
    "researcher": {
        "accent": "#687b55",
        "accent_dark": "#4c5f3d",
        "accent_soft": "#eef4e9",
        "warm": "#bd7053",
        "warm_soft": "#fff2eb",
        "surface": "#ffffff",
        "page": "#fafbf7",
        "muted": "#6e7368",
        "ink": "#272b22",
    },
}


def inject_theme(role: str) -> None:
    """Inject a polished, restrained Streamlit theme."""
    theme = THEMES.get(role, THEMES["public"])
    st.markdown(
        f"""
        <style>
        :root {{
            --kg-accent: {theme["accent"]};
            --kg-accent-dark: {theme["accent_dark"]};
            --kg-accent-soft: {theme["accent_soft"]};
            --kg-warm: {theme["warm"]};
            --kg-warm-soft: {theme["warm_soft"]};
            --kg-surface: {theme["surface"]};
            --kg-page: {theme["page"]};
            --kg-muted: {theme["muted"]};
            --kg-ink: {theme["ink"]};
            --kg-border: #d9e2de;
            --kg-shadow: 0 18px 45px rgba(38, 55, 49, 0.08);
        }}

        .stApp {{
            background:
                linear-gradient(180deg, var(--kg-page) 0%, #ffffff 58%, #f7f6f1 100%);
            color: var(--kg-ink);
        }}

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        footer {{
            display: none !important;
            visibility: hidden !important;
        }}

        [data-testid="stAppViewContainer"] > .main .block-container {{
            max-width: 1220px;
            padding-top: 0.65rem;
            padding-bottom: 3rem;
        }}

        [data-testid="stSidebar"] {{
            background: #f2f6f4;
            border-right: 1px solid var(--kg-border);
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] li {{
            color: #47544f;
            line-height: 1.65;
        }}

        h1, h2, h3 {{
            color: var(--kg-ink);
            letter-spacing: 0;
        }}

        .kg-hero {{
            border: 1px solid var(--kg-border);
            border-top: 5px solid var(--kg-accent);
            border-radius: 8px;
            padding: 1.45rem 1.6rem 1.35rem;
            margin: 0.25rem 0 1.25rem;
            background:
                linear-gradient(135deg, #ffffff 0%, var(--kg-accent-soft) 54%, var(--kg-warm-soft) 100%);
            box-shadow: var(--kg-shadow);
        }}

        .kg-kicker {{
            color: var(--kg-accent-dark);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0;
            margin-bottom: 0.4rem;
        }}

        .kg-hero h1 {{
            margin: 0;
            font-size: 2.15rem;
            line-height: 1.15;
        }}

        .kg-hero p {{
            margin: 0.7rem 0 0;
            max-width: 860px;
            color: #3f4b47;
            line-height: 1.7;
            font-size: 1rem;
        }}

        .kg-pill-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }}

        .kg-pill {{
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(47, 76, 67, 0.14);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.74);
            color: #2e3f39;
            font-size: 0.86rem;
            font-weight: 600;
            padding: 0.38rem 0.72rem;
            white-space: nowrap;
        }}

        .kg-sidebar-card {{
            border: 1px solid var(--kg-border);
            border-left: 4px solid var(--kg-accent);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.78);
            padding: 1rem;
            margin: 0.35rem 0 1rem;
        }}

        .kg-sidebar-card h2 {{
            font-size: 1.05rem;
            margin: 0 0 0.45rem;
        }}

        .kg-sidebar-card p {{
            margin: 0 0 0.65rem;
        }}

        .kg-sidebar-card ul {{
            margin: 0.35rem 0 0;
            padding-left: 1.15rem;
        }}

        .kg-section {{
            margin: 1.2rem 0 0.7rem;
        }}

        .kg-section h2 {{
            font-size: 1.15rem;
            margin: 0 0 0.25rem;
        }}

        .kg-section p {{
            color: var(--kg-muted);
            margin: 0;
            line-height: 1.6;
        }}

        .kg-entity-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 0.75rem;
            margin-top: 0.45rem;
        }}

        .kg-entity-card {{
            background: var(--kg-surface);
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            padding: 0.85rem;
            box-shadow: 0 8px 20px rgba(38, 55, 49, 0.05);
        }}

        .kg-entity-type {{
            color: var(--kg-accent-dark);
            font-size: 0.74rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }}

        .kg-entity-name {{
            color: var(--kg-ink);
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.28rem;
            overflow-wrap: anywhere;
        }}

        .kg-entity-meta {{
            color: var(--kg-muted);
            font-size: 0.85rem;
        }}

        .stButton > button {{
            min-height: 2.45rem;
            border-radius: 8px;
            border: 1px solid #c8d6d0;
            background: #ffffff;
            color: var(--kg-ink);
            font-weight: 650;
            box-shadow: 0 5px 16px rgba(31, 47, 41, 0.05);
        }}

        .stButton > button:hover {{
            border-color: var(--kg-accent);
            color: var(--kg-accent-dark);
            background: var(--kg-accent-soft);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.35rem;
            background: #edf3f0;
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            padding: 0.35rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 7px;
            color: #4e5a55;
            font-weight: 650;
        }}

        .stTabs [aria-selected="true"] {{
            background: #ffffff;
            color: var(--kg-accent-dark);
            box-shadow: 0 5px 16px rgba(31, 47, 41, 0.06);
        }}

        [data-testid="stMetric"] {{
            background: #ffffff;
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
            box-shadow: 0 8px 18px rgba(38, 55, 49, 0.05);
        }}

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {{
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 8px 18px rgba(38, 55, 49, 0.04);
        }}

        [data-testid="stChatMessage"] {{
            border: 1px solid rgba(199, 214, 208, 0.75);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.72);
            box-shadow: 0 8px 22px rgba(38, 55, 49, 0.04);
        }}

        div[data-testid="stExpander"] details {{
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.8);
        }}

        .kg-status {{
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: center;
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            padding: 0.8rem 0.95rem;
            background: #ffffff;
            margin: 0.85rem 0 1rem;
            box-shadow: 0 10px 24px rgba(38, 55, 49, 0.05);
        }}

        .kg-status-title {{
            color: var(--kg-ink);
            font-weight: 800;
            font-size: 0.96rem;
        }}

        .kg-status-detail {{
            color: var(--kg-muted);
            font-size: 0.86rem;
            line-height: 1.55;
        }}

        .kg-status-badge {{
            border-radius: 999px;
            border: 1px solid rgba(63, 120, 147, 0.22);
            background: var(--kg-accent-soft);
            color: var(--kg-accent-dark);
            font-weight: 800;
            font-size: 0.78rem;
            padding: 0.36rem 0.7rem;
            white-space: nowrap;
        }}

        .kg-metric-strip {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(125px, 1fr));
            gap: 0.72rem;
            margin: 0.85rem 0 1.1rem;
        }}

        .kg-metric-card {{
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            background: #ffffff;
            padding: 0.9rem 0.95rem;
            box-shadow: 0 10px 24px rgba(38, 55, 49, 0.05);
            min-height: 6.2rem;
        }}

        .kg-metric-label {{
            color: var(--kg-muted);
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
        }}

        .kg-metric-value {{
            color: var(--kg-ink);
            font-size: 1.55rem;
            font-weight: 850;
            margin-top: 0.25rem;
            line-height: 1.15;
        }}

        .kg-metric-detail {{
            color: var(--kg-muted);
            font-size: 0.82rem;
            margin-top: 0.24rem;
        }}

        .kg-workbench-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(235px, 1fr));
            gap: 0.78rem;
            margin: 0.8rem 0 1rem;
        }}

        .kg-workbench-card {{
            border: 1px solid var(--kg-border);
            border-top: 3px solid var(--kg-accent);
            border-radius: 8px;
            background: #ffffff;
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 24px rgba(38, 55, 49, 0.05);
        }}

        .kg-workbench-card h3 {{
            margin: 0 0 0.4rem;
            font-size: 1rem;
        }}

        .kg-workbench-card p {{
            margin: 0;
            color: var(--kg-muted);
            font-size: 0.9rem;
            line-height: 1.58;
        }}

        .kg-persona-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
            gap: 0.82rem;
            margin: 0.7rem 0 0.95rem;
        }}

        .kg-persona-card {{
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 12px 28px rgba(38, 55, 49, 0.06);
            padding: 1rem;
            min-height: 12.5rem;
        }}

        .kg-persona-audience {{
            color: var(--kg-accent-dark);
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
        }}

        .kg-persona-card h3 {{
            margin: 0 0 0.45rem;
            font-size: 1.03rem;
            line-height: 1.35;
        }}

        .kg-persona-need {{
            color: #3f4b47;
            font-size: 0.9rem;
            line-height: 1.58;
            margin: 0 0 0.62rem;
        }}

        .kg-persona-card ul {{
            margin: 0;
            padding-left: 1.05rem;
        }}

        .kg-persona-card li {{
            color: var(--kg-muted);
            font-size: 0.86rem;
            line-height: 1.52;
            margin: 0.18rem 0;
        }}

        .kg-entry-button {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            min-height: 8.4rem;
            border: 1px solid var(--kg-border);
            border-top: 4px solid var(--kg-accent);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 14px 30px rgba(38, 55, 49, 0.07);
            padding: 1rem;
            color: var(--kg-ink) !important;
            text-decoration: none !important;
            margin: 0.3rem 0 1rem;
        }}

        .kg-entry-button:hover {{
            border-color: var(--kg-accent);
            background: var(--kg-accent-soft);
        }}

        .kg-entry-button strong {{
            font-size: 1.05rem;
            line-height: 1.3;
        }}

        .kg-entry-button small {{
            color: var(--kg-muted);
            font-size: 0.86rem;
            line-height: 1.45;
        }}

        .kg-entry-audience {{
            color: var(--kg-accent-dark);
            font-size: 0.76rem;
            font-weight: 850;
            text-transform: uppercase;
        }}

        .kg-insight-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(255px, 1fr));
            gap: 0.82rem;
            margin: 0.72rem 0 1rem;
        }}

        .kg-insight-card {{
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdfb 100%);
            box-shadow: 0 12px 28px rgba(38, 55, 49, 0.055);
            padding: 1rem;
            min-height: 14.3rem;
        }}

        .kg-insight-tag {{
            display: inline-flex;
            border: 1px solid rgba(76, 95, 61, 0.18);
            border-radius: 999px;
            background: var(--kg-accent-soft);
            color: var(--kg-accent-dark);
            font-size: 0.72rem;
            font-weight: 850;
            padding: 0.24rem 0.55rem;
            margin-bottom: 0.55rem;
        }}

        .kg-insight-card h3 {{
            margin: 0 0 0.48rem;
            font-size: 1rem;
            line-height: 1.36;
        }}

        .kg-insight-statement {{
            color: #33423c;
            font-size: 0.91rem;
            line-height: 1.56;
            margin: 0 0 0.68rem;
        }}

        .kg-insight-meta {{
            display: grid;
            gap: 0.38rem;
            margin-top: 0.55rem;
        }}

        .kg-insight-meta div {{
            border-top: 1px solid #e4ebe7;
            padding-top: 0.38rem;
            color: var(--kg-muted);
            font-size: 0.82rem;
            line-height: 1.45;
        }}

        .kg-insight-meta strong {{
            color: var(--kg-ink);
        }}

        .kg-pipeline {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.55rem;
            margin: 0.75rem 0 1.1rem;
        }}

        .kg-pipeline-step {{
            position: relative;
            border: 1px solid var(--kg-border);
            border-radius: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdfc 100%);
            padding: 0.78rem 0.82rem;
            min-height: 5.15rem;
        }}

        .kg-pipeline-index {{
            color: var(--kg-accent-dark);
            font-weight: 900;
            font-size: 0.78rem;
        }}

        .kg-pipeline-title {{
            color: var(--kg-ink);
            font-weight: 800;
            font-size: 0.9rem;
            margin-top: 0.12rem;
        }}

        .kg-pipeline-body {{
            color: var(--kg-muted);
            font-size: 0.78rem;
            margin-top: 0.22rem;
            line-height: 1.45;
        }}

        .kg-evidence-table {{
            width: 100%;
            table-layout: fixed;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 8px;
            border: 1px solid var(--kg-border);
            background: #ffffff;
            box-shadow: 0 10px 24px rgba(38, 55, 49, 0.04);
        }}

        .kg-evidence-table th {{
            text-align: left;
            background: #edf3f0;
            color: var(--kg-ink);
            font-size: 0.82rem;
            padding: 0.72rem;
        }}

        .kg-evidence-table td {{
            border-top: 1px solid #e4ebe7;
            color: #3f4b47;
            font-size: 0.86rem;
            padding: 0.72rem;
            vertical-align: top;
            overflow-wrap: anywhere;
            word-break: normal;
        }}

        .kg-evidence-table th {{
            overflow-wrap: anywhere;
        }}

        .kg-bar-list {{
            display: grid;
            gap: 0.55rem;
            margin: 0.4rem 0 0.8rem;
        }}

        .kg-bar-row {{
            display: grid;
            grid-template-columns: minmax(85px, 1.25fr) minmax(120px, 2fr) minmax(36px, auto);
            gap: 0.55rem;
            align-items: center;
        }}

        .kg-bar-label {{
            color: var(--kg-ink);
            font-size: 0.84rem;
            font-weight: 650;
            overflow-wrap: anywhere;
        }}

        .kg-bar-track {{
            height: 0.62rem;
            border-radius: 999px;
            background: #e6eee9;
            overflow: hidden;
        }}

        .kg-bar-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--kg-accent), var(--kg-warm));
        }}

        .kg-bar-value {{
            color: var(--kg-muted);
            font-size: 0.82rem;
            font-weight: 750;
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}

        .stSlider [data-baseweb="slider"] > div {{
            color: var(--kg-accent);
        }}

        hr {{
            border-color: #dfe7e3;
        }}

        @media (max-width: 720px) {{
            [data-testid="stAppViewContainer"] > .main .block-container {{
                padding: 0.75rem 0.8rem 5.5rem;
            }}

            .kg-hero {{
                padding: 1rem;
                margin-top: 0;
            }}

            .kg-hero h1 {{
                font-size: 1.55rem;
                line-height: 1.22;
            }}

            .kg-hero p {{
                font-size: 0.94rem;
                line-height: 1.62;
            }}

            .kg-pill-row {{
                gap: 0.4rem;
            }}

            .kg-pill {{
                font-size: 0.78rem;
                padding: 0.32rem 0.58rem;
                white-space: normal;
            }}

            .kg-section {{
                margin-top: 1rem;
            }}

            .kg-section h2 {{
                font-size: 1.02rem;
            }}

            .kg-entity-grid {{
                grid-template-columns: 1fr;
            }}

            .kg-status {{
                align-items: flex-start;
                flex-direction: column;
            }}

            .kg-metric-strip {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}

            .kg-metric-card {{
                min-height: 5.7rem;
            }}

            .kg-metric-value {{
                font-size: 1.28rem;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                overflow-x: auto;
                flex-wrap: nowrap;
            }}

            .stTabs [data-baseweb="tab"] {{
                min-width: max-content;
            }}

            .stButton > button {{
                min-height: 2.75rem;
                white-space: normal;
            }}

            .kg-bar-row {{
                grid-template-columns: 1fr auto;
            }}

            .kg-bar-track {{
                grid-column: 1 / -1;
            }}

            .kg-persona-card {{
                min-height: auto;
            }}

            .kg-insight-card {{
                min-height: auto;
            }}

            .kg-evidence-table th,
            .kg-evidence-table td {{
                font-size: 0.76rem;
                padding: 0.55rem;
                line-height: 1.42;
            }}

            [data-testid="stChatMessage"] {{
                padding: 0.25rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, eyebrow: str, pills: Iterable[str]) -> None:
    """Render the top platform band."""
    pill_html = "".join(f'<span class="kg-pill">{escape(pill)}</span>' for pill in pills)
    st.markdown(
        f"""
        <section class="kg-hero">
            <div class="kg-kicker">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
            <div class="kg-pill-row">{pill_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_card(title: str, body: str, items: Iterable[str]) -> None:
    """Render a compact sidebar guidance card."""
    item_html = "".join(f"<li>{escape(item)}</li>" for item in items)
    st.markdown(
        f"""
        <div class="kg-sidebar-card">
            <h2>{escape(title)}</h2>
            <p>{escape(body)}</p>
            <ul>{item_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_banner(title: str, detail: str, badge: str) -> None:
    """Render live/demo status without blocking the user."""
    st.markdown(
        f"""
        <div class="kg-status">
            <div>
                <div class="kg-status-title">{escape(title)}</div>
                <div class="kg-status-detail">{escape(detail)}</div>
            </div>
            <div class="kg-status-badge">{escape(badge)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(metrics: Iterable[Mapping]) -> None:
    """Render compact platform metrics."""
    cards = []
    for metric in metrics:
        cards.append(
            '<div class="kg-metric-card">'
            f'<div class="kg-metric-label">{escape(str(metric.get("label", "")))}</div>'
            f'<div class="kg-metric-value">{escape(str(metric.get("value", "")))}</div>'
            f'<div class="kg-metric-detail">{escape(str(metric.get("detail", "")))}</div>'
            "</div>"
        )
    st.markdown(f'<div class="kg-metric-strip">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_workbench_cards(cards: Iterable[Mapping]) -> None:
    """Render role-specific capability cards."""
    rendered = []
    for card in cards:
        rendered.append(
            '<div class="kg-workbench-card">'
            f'<h3>{escape(str(card.get("title", "")))}</h3>'
            f'<p>{escape(str(card.get("body", "")))}</p>'
            "</div>"
        )
    st.markdown(f'<div class="kg-workbench-grid">{"".join(rendered)}</div>', unsafe_allow_html=True)


def render_persona_gateway(cards: Iterable[Mapping]) -> None:
    """Render the first-look tasks for public, clinical, and research users."""
    rendered = []
    for card in cards:
        outputs = card.get("outputs", [])
        output_html = "".join(f"<li>{escape(str(item))}</li>" for item in outputs)
        rendered.append(
            '<div class="kg-persona-card">'
            f'<div class="kg-persona-audience">{escape(str(card.get("audience", "")))}</div>'
            f'<h3>{escape(str(card.get("title", "")))}</h3>'
            f'<p class="kg-persona-need">{escape(str(card.get("need", "")))}</p>'
            f"<ul>{output_html}</ul>"
            "</div>"
        )
    st.markdown(f'<div class="kg-persona-grid">{"".join(rendered)}</div>', unsafe_allow_html=True)


def render_insight_cards(cards: Iterable[Mapping]) -> None:
    """Render dense evidence insights with translation and next-step value."""
    rendered = []
    for card in cards:
        meta_html = "".join(
            f"<div><strong>{escape(str(item.get('label', '')))}:</strong> {escape(str(item.get('value', '')))}</div>"
            for item in card.get("meta", [])
        )
        rendered.append(
            '<div class="kg-insight-card">'
            f'<div class="kg-insight-tag">{escape(str(card.get("tag", "")))}</div>'
            f'<h3>{escape(str(card.get("title", "")))}</h3>'
            f'<p class="kg-insight-statement">{escape(str(card.get("statement", "")))}</p>'
            f'<div class="kg-insight-meta">{meta_html}</div>'
            "</div>"
        )
    st.markdown(f'<div class="kg-insight-grid">{"".join(rendered)}</div>', unsafe_allow_html=True)


def render_pipeline(steps: Iterable[Mapping]) -> None:
    """Render a manuscript-style data-to-answer workflow."""
    rendered = []
    for index, step in enumerate(steps, start=1):
        rendered.append(
            '<div class="kg-pipeline-step">'
            f'<div class="kg-pipeline-index">{index:02d}</div>'
            f'<div class="kg-pipeline-title">{escape(str(step.get("title", "")))}</div>'
            f'<div class="kg-pipeline-body">{escape(str(step.get("body", "")))}</div>'
            "</div>"
        )
    st.markdown(f'<div class="kg-pipeline">{"".join(rendered)}</div>', unsafe_allow_html=True)


def render_evidence_snapshot(rows: Iterable[Mapping]) -> None:
    """Render a compact evidence interpretation table."""
    rows = list(rows)
    if not rows:
        return
    headers = list(rows[0].keys())
    header_html = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    body_html = ""
    for row in rows:
        body_html += "<tr>" + "".join(f"<td>{escape(str(row.get(header, '')))}</td>" for header in headers) + "</tr>"
    st.markdown(
        f"""
        <table class="kg-evidence-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{body_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def render_ranked_bar_list(
    rows: Iterable[Mapping],
    label_key: str,
    value_key: str,
    limit: int = 10,
    empty_message: str = "暂无足够数据生成排序图。",
) -> None:
    """Render stable ranked bars without invoking Vega charts."""
    normalized = []
    for row in list(rows)[:limit]:
        try:
            value = float(row.get(value_key, 0) or 0)
        except (TypeError, ValueError):
            value = 0
        normalized.append((str(row.get(label_key, "N/A")), value))

    normalized = [(label, value) for label, value in normalized if value > 0]
    if not normalized:
        st.info(empty_message)
        return

    max_value = max(value for _, value in normalized) or 1
    bars = []
    for label, value in normalized:
        width = max(6, min(100, round(value / max_value * 100, 1)))
        value_text = str(int(value)) if value.is_integer() else f"{value:.1f}"
        bars.append(
            '<div class="kg-bar-row">'
            f'<div class="kg-bar-label">{escape(label)}</div>'
            '<div class="kg-bar-track">'
            f'<div class="kg-bar-fill" style="width: {width}%"></div>'
            "</div>"
            f'<div class="kg-bar-value">{escape(value_text)}</div>'
            "</div>"
        )

    st.markdown(f'<div class="kg-bar-list">{"".join(bars)}</div>', unsafe_allow_html=True)


def render_section_header(title: str, body: str = "") -> None:
    """Render a consistent section title."""
    body_html = f"<p>{escape(body)}</p>" if body else ""
    st.markdown(
        f"""
        <div class="kg-section">
            <h2>{escape(title)}</h2>
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_entity_cards(entities: Iterable[Mapping], limit: int = 3, study_label: str = "篇文献提及") -> None:
    """Render knowledge-source entity cards."""
    cards = []
    for entity in list(entities)[:limit]:
        name = escape(str(entity.get("name", "N/A")))
        entity_type = escape(str(entity.get("type", "N/A")))
        study_count = escape(str(entity.get("study_count", 0)))
        cards.append(
            f"""
            <div class="kg-entity-card">
                <div class="kg-entity-type">{entity_type}</div>
                <div class="kg-entity-name">{name}</div>
                <div class="kg-entity-meta">{study_count} {escape(study_label)}</div>
            </div>
            """
        )

    st.markdown(
        f'<div class="kg-entity-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )

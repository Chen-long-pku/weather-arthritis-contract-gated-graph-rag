"""
Unified home page for the climate-sensitive chronic disease platform.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from arthritis_platform.web.navigation import language_selectbox  # noqa: E402
from arthritis_platform.web.ui_theme import (  # noqa: E402
    inject_theme,
    render_hero,
    render_metric_strip,
    render_persona_gateway,
    render_section_header,
)


HOME_TEXT = {
    "zh": {
        "page_title": "项目首页 - 气候敏感性慢性病证据平台",
        "language_hint": "语言选择会带入三个角色页面。",
        "hero": {
            "title": "气候敏感性慢性病证据平台",
            "subtitle": "一个面向公众、医务工作者和科研人员的中英双语入口：把天气、空气污染和常见慢病相关证据转成不同场景下可使用的解释、随访和研究分析工具。",
            "eyebrow": "统一入口 / 角色化证据转译",
            "pills": ["公众健康解释", "医务证据分诊", "科研证据分析", "中英双语", "常见慢病"],
        },
        "metrics": [
            {"label": "首页入口", "value": "3个", "detail": "公众、医务、科研"},
            {"label": "慢病主题", "value": "6类+", "detail": "心肺肾代谢、疼痛、关节炎"},
            {"label": "使用语言", "value": "2种", "detail": "中文、English"},
            {"label": "服务重点", "value": "解释", "detail": "记录、沟通、分析"},
        ],
        "sections": {
            "intro": ("平台简介", "本平台把天气和空气污染相关慢病证据按角色转译为可理解、可记录、可检索的信息；不提供个体诊断、治疗或风险预测。"),
            "choose": ("选择你的入口", "先选择语言，再进入最符合当前需求的页面。"),
        },
        "intro_cards": [
            {
                "audience": "使用边界",
                "title": "按角色控制解释深度，而不是给出个体诊疗结论。",
                "need": "普通用户看到通俗解释，医务人员看到随访边界，科研人员看到可检索证据和分析入口。",
                "outputs": ["公众解释", "医务随访", "科研检索"],
            },
            {
                "audience": "服务对象",
                "title": "同一证据基础，分别服务健康理解、临床沟通和科研探索。",
                "need": "页面不要求用户了解平台建立过程，只帮助他们完成当前角色最需要的任务。",
                "outputs": ["健康解释", "沟通清单", "研究假设"],
            },
        ],
        "roles": [
            {
                "key": "public",
                "audience": "公众",
                "title": "我想知道天气、污染和慢病症状有什么关系。",
                "need": "适合普通人理解热浪、雾霾、寒潮、潮湿和症状波动。",
                "outputs": ["通俗解释", "症状记录", "就医沟通小条", "红旗信号"],
                "button": "进入公众端",
            },
            {
                "key": "medical",
                "audience": "医务工作者",
                "title": "我需要门诊解释、随访边界和证据分诊。",
                "need": "适合把天气/污染暴露转成可记录、可复核、可交接的临床沟通材料。",
                "outputs": ["PMID溯源", "门诊随访记录要点", "证据等级", "红旗边界"],
                "button": "进入医务端",
            },
            {
                "key": "research",
                "audience": "科研人员",
                "title": "我需要研究问题、假设库和可导出证据。",
                "need": "适合查看研究热点、证据缺口、实体关系和可下载数据。",
                "outputs": ["证据检索", "研究假设库", "质量审计", "JSON/CSV导出"],
                "button": "进入科研端",
            },
        ],
    },
    "en": {
        "page_title": "Home - Climate-Sensitive Chronic Disease Evidence Platform",
        "language_hint": "The selected language is passed into each role-specific page.",
        "hero": {
            "title": "Climate-Sensitive Chronic Disease Evidence Platform",
            "subtitle": "A bilingual entry point for public, medical, and research users, turning weather, air-pollution, and chronic-disease evidence into usable explanation, follow-up, and research-analysis tools.",
            "eyebrow": "Unified gateway / role-specific evidence translation",
            "pills": ["Public explanation", "Clinical evidence triage", "Research analysis", "Bilingual", "Common chronic disease"],
        },
        "metrics": [
            {"label": "Entry routes", "value": "3", "detail": "public, medical, research"},
            {"label": "Disease scope", "value": "6+", "detail": "heart, lung, kidney, metabolic, pain, arthritis"},
            {"label": "Languages", "value": "2", "detail": "Chinese and English"},
            {"label": "Main service", "value": "Explain", "detail": "track, communicate, analyze"},
        ],
        "sections": {
            "intro": ("Platform Overview", "This platform translates weather- and air-pollution-related chronic-disease evidence into understandable, recordable, and searchable information for different roles. It does not provide individual diagnosis, treatment, or risk prediction."),
            "choose": ("Choose Your Entry", "Select a language first, then enter the page that matches your current role."),
        },
        "intro_cards": [
            {
                "audience": "Use boundary",
                "title": "Role-matched explanation, not individual clinical conclusions.",
                "need": "Public users see plain explanations, health professionals see follow-up boundaries, and researchers see searchable evidence and analysis tools.",
                "outputs": ["Public explanation", "Clinical follow-up", "Research retrieval"],
            },
            {
                "audience": "User groups",
                "title": "The same evidence base serves health understanding, clinical communication, and research exploration.",
                "need": "Users do not need to understand how the platform was built; each page focuses on the task they came to complete.",
                "outputs": ["Health explanation", "Communication checklist", "Research hypotheses"],
            },
        ],
        "roles": [
            {
                "key": "public",
                "audience": "Public",
                "title": "I want to understand weather, pollution, and chronic disease symptoms.",
                "need": "For plain-language explanations about heat, smog, cold, humidity, and symptom fluctuation.",
                "outputs": ["Plain explanation", "Symptom notes", "Visit note", "Red flags"],
                "button": "Enter Public Page",
            },
            {
                "key": "medical",
                "audience": "Health Professionals",
                "title": "I need outpatient explanation, follow-up boundaries, and evidence triage.",
                "need": "For turning weather or pollution exposure into recordable, reviewable, and handoff-ready clinical communication.",
                "outputs": ["PMID trace", "Follow-up documentation", "Evidence grade", "Warning boundaries"],
                "button": "Enter Medical Page",
            },
            {
                "key": "research",
                "audience": "Researchers",
                "title": "I need research questions, hypothesis banks, and exportable evidence.",
                "need": "For hotspots, evidence gaps, entity relationships, and downloadable data.",
                "outputs": ["Evidence retrieval", "Hypothesis bank", "Quality audit", "JSON/CSV export"],
                "button": "Enter Research Page",
            },
        ],
    },
}


PORTS = {
    "public": os.getenv("PLATFORM_PUBLIC_URL", "http://127.0.0.1:8501"),
    "medical": os.getenv("PLATFORM_MEDICAL_URL", "http://127.0.0.1:8502"),
    "research": os.getenv("PLATFORM_RESEARCH_URL", "http://127.0.0.1:8503"),
}


def role_url(role: str, lang: str) -> str:
    return f"{PORTS[role]}?lang={lang}"


def render_role_buttons(roles: list[dict], lang: str) -> None:
    columns = st.columns(3)
    for index, role in enumerate(roles):
        href = role_url(str(role["key"]), lang)
        with columns[index]:
            st.markdown(
                f"""
                <a class="kg-entry-button" href="{href}" target="_self">
                    <span class="kg-entry-audience">{role["audience"]}</span>
                    <strong>{role["button"]}</strong>
                    <small>{role["title"]}</small>
                </a>
                """,
                unsafe_allow_html=True,
            )


st.set_page_config(
    page_title="项目首页 / Platform Home",
    page_icon="C",
    layout="wide",
)

inject_theme("home")

selected_language, lang = language_selectbox(st, key="home_language")
t = HOME_TEXT[lang]
st.caption(t["language_hint"])

render_hero(**t["hero"])

render_metric_strip(t["metrics"])

render_section_header(*t["sections"]["choose"])
render_role_buttons(t["roles"], lang)
render_persona_gateway(t["roles"])

render_section_header(*t["sections"]["intro"])
render_persona_gateway(t["intro_cards"])

"""
Health-worker page for the climate-sensitive chronic disease KG platform.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from arthritis_platform.web.language import (  # noqa: E402
    get_text,
    localized_clinical_translation,
    localized_evidence_triage,
)
from arthritis_platform.web.navigation import language_selectbox  # noqa: E402
from arthritis_platform.web.runtime import create_runtime  # noqa: E402
from arthritis_platform.web.ui_theme import (  # noqa: E402
    inject_theme,
    render_evidence_snapshot,
    render_hero,
    render_insight_cards,
    render_metric_strip,
    render_pipeline,
    render_section_header,
    render_sidebar_card,
    render_workbench_cards,
)


st.set_page_config(
    page_title="慢性病临床工作台 / Chronic Disease Workbench",
    page_icon="M",
    layout="wide",
)

inject_theme("medical")

with st.sidebar:
    _, lang = language_selectbox(st, key="medical_language")
t = get_text("medical", lang)

render_hero(**t["hero"])


@st.cache_resource
def init_runtime():
    return create_runtime()


runtime = init_runtime()
rag = runtime.rag
graph = runtime.graph

render_metric_strip(t["metrics"])

render_section_header(*t["sections"]["value"])
render_insight_cards(t["cards"])

render_pipeline(t["pipeline"])
render_workbench_cards(t["workbench"])

with st.sidebar:
    render_sidebar_card(t["sidebar"]["title"], t["sidebar"]["body"], t["sidebar"]["items"])
    st.divider()
    st.subheader(t["sidebar"]["options"])
    show_pmid = st.checkbox(t["sidebar"]["show_pmid"], value=True)
    show_stats = st.checkbox(t["sidebar"]["show_stats"], value=True)
    max_results = st.slider(t["sidebar"]["max_results"], 5, 20, 10)
    st.divider()
    st.caption(t["sidebar"]["caption"])

tab_triage, tab_qa, tab_entity, tab_stats = st.tabs(t["tabs"])

with tab_triage:
    render_section_header(*t["sections"]["triage"])
    st.caption(t["triage"]["info"])
    render_section_header(*t["sections"]["clinical_brief"])
    render_evidence_snapshot(t["clinical_brief_rows"])
    st.divider()
    render_section_header(*t["sections"]["matrix"])
    render_evidence_snapshot(t["clinical_matrix"])
    st.divider()
    render_section_header(*t["sections"]["grade"])
    render_evidence_snapshot(localized_evidence_triage(graph, lang))
    st.divider()
    render_section_header(*t["sections"]["translation"])
    render_evidence_snapshot(localized_clinical_translation(graph, lang))
    st.divider()
    render_section_header(*t["sections"]["red_flags"])
    render_evidence_snapshot(t["red_flag_rows"])

with tab_qa:
    render_section_header(*t["sections"]["qa"])

    messages_key = f"medical_messages_{lang}"
    pending_key = f"medical_pending_prompt_{lang}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []
    if pending_key not in st.session_state:
        st.session_state[pending_key] = ""

    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.session_state[pending_key] or st.chat_input(t["chat"]["input"])
    st.session_state[pending_key] = ""

    if prompt:
        st.session_state[messages_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t["chat"]["spinner"]):
                try:
                    result = rag.answer_question(prompt, role="medical", max_results=max_results)
                    answer = result["answer"]
                    st.markdown(answer)

                    col_entities, col_studies = st.columns(2)
                    with col_entities:
                        if result["knowledge"]["entities"]:
                            with st.expander(t["chat"]["entities"], expanded=True):
                                entities_df = pd.DataFrame(result["knowledge"]["entities"][:5])
                                if not entities_df.empty:
                                    st.dataframe(entities_df, use_container_width=True)

                    with col_studies:
                        if show_pmid and result["knowledge"]["studies"]:
                            with st.expander(t["chat"]["studies"], expanded=True):
                                for study in result["knowledge"]["studies"][:3]:
                                    st.markdown(f"**PMID: {study['pmid']}**")
                                    st.caption(str(study.get("title", "N/A"))[:140])
                                    st.divider()

                    if result["knowledge"]["relations"]:
                        with st.expander(t["chat"]["relations"]):
                            for rel in result["knowledge"]["relations"][:5]:
                                st.text(
                                    f"{rel.get('source', 'N/A')} -> "
                                    f"{rel.get('relation', 'N/A')} -> "
                                    f"{rel.get('target', 'N/A')}"
                                )

                    if result["knowledge"].get("triage"):
                        with st.expander(t["chat"]["triage"], expanded=True):
                            st.dataframe(pd.DataFrame(result["knowledge"]["triage"]), use_container_width=True)

                    if result.get("boundary"):
                        with st.expander(t["chat"].get("boundary", "Evidence boundary"), expanded=True):
                            st.json(result["boundary"])

                    if result.get("claim_ledger"):
                        with st.expander(t["chat"].get("claim_ledger", "Claim-evidence ledger"), expanded=True):
                            st.dataframe(pd.DataFrame(result["claim_ledger"]), use_container_width=True)

                    st.session_state[messages_key].append({"role": "assistant", "content": answer})
                except Exception as exc:
                    error_msg = f"{t['chat']['error']}{exc}"
                    st.error(error_msg)
                    st.session_state[messages_key].append({"role": "assistant", "content": error_msg})

    st.divider()
    render_section_header(*t["sections"]["examples"])
    example_cols = st.columns(2)

    def ask_medical_question(question: str):
        st.session_state[pending_key] = question
        st.rerun()

    for index, example in enumerate(t["examples"]):
        with example_cols[index % 2]:
            if st.button(example["button"], key=f"medical_example_{lang}_{index}", use_container_width=True):
                ask_medical_question(example["prompt"])

with tab_entity:
    render_section_header(*t["sections"]["entity"])
    entity_text = t["entity_query"]

    col_name, col_type = st.columns([2, 1])
    with col_name:
        entity_name = st.text_input(entity_text["name"])
    with col_type:
        selected_type_label = st.selectbox(entity_text["type"], list(entity_text["types"].keys()))
        type_filter = entity_text["types"][selected_type_label]

    if st.button(entity_text["button"], key=f"medical_entity_query_{lang}", use_container_width=True):
        if entity_name:
            with st.spinner(entity_text["spinner"]):
                try:
                    results = graph.search_entity(entity_name, type_filter)
                    if results:
                        st.success(entity_text["found"].format(n=len(results)))
                        st.dataframe(pd.DataFrame(results), use_container_width=True)

                        selected = st.selectbox(entity_text["select"], [row["name"] for row in results])
                        if selected:
                            try:
                                relations = graph.get_entity_relations(selected)
                                if relations:
                                    st.subheader(entity_text["relations_of"].format(name=selected))
                                    st.dataframe(pd.DataFrame(relations), use_container_width=True)
                            except Exception as exc:
                                st.warning(f"{entity_text['relation_fail']}{exc}")

                            try:
                                studies = graph.get_entity_studies(selected)
                                if studies:
                                    st.subheader(entity_text["related_studies"].format(n=len(studies)))
                                    for study in studies[:5]:
                                        with st.expander(f"PMID: {study['pmid']}"):
                                            st.write(f"**{entity_text['title']}:** {study.get('title', 'N/A')}")
                                            st.write(f"**{entity_text['year']}:** {study.get('year', 'N/A')}")
                            except Exception as exc:
                                st.warning(f"{entity_text['study_fail']}{exc}")
                    else:
                        st.warning(entity_text["no_results"])
                except Exception as exc:
                    st.error(f"{entity_text['query_fail']}{exc}")
        else:
            st.info(entity_text["no_entity"])

with tab_stats:
    render_section_header(*t["sections"]["stats"])
    stats_text = t["stats"]

    if not show_stats:
        st.info(t["sidebar"]["show_stats"])
    elif st.button(stats_text["refresh"], key=f"medical_refresh_stats_{lang}", use_container_width=True):
        with st.spinner(stats_text["spinner"]):
            try:
                stats = graph.get_statistics()

                st.markdown(f"### {stats_text['nodes']}")
                if stats.get("nodes"):
                    nodes_df = pd.DataFrame(stats["nodes"])
                    col_chart, col_table = st.columns([2, 1])
                    with col_chart:
                        st.bar_chart(nodes_df.set_index("type")["count"])
                    with col_table:
                        st.dataframe(nodes_df, use_container_width=True)

                st.divider()
                st.markdown(f"### {stats_text['relations']}")
                if stats.get("relations"):
                    rels_df = pd.DataFrame(stats["relations"])
                    col_chart, col_table = st.columns([2, 1])
                    with col_chart:
                        st.bar_chart(rels_df.set_index("type")["count"].head(10))
                    with col_table:
                        st.dataframe(rels_df.head(10), use_container_width=True)

                st.divider()
                st.markdown(f"### {stats_text['top']}")
                col_climate, col_symptom, col_arthritis = st.columns(3)
                top_specs = [
                    (col_climate, stats_text["climate"], "ClimateFactor"),
                    (col_symptom, stats_text["symptom"], "Symptom"),
                    (col_arthritis, stats_text["arthritis"], "ChronicDisease"),
                ]
                for column, label, entity_type in top_specs:
                    with column:
                        st.write(f"**{label}**")
                        try:
                            for item in graph.get_top_entities(entity_type, 5):
                                st.metric(item["name"], f"{item.get('study_count', 0)} {stats_text['study_suffix']}")
                        except Exception as exc:
                            st.warning(f"{stats_text['load_fail']}{exc}")
            except Exception as exc:
                st.error(f"{stats_text['fail']}{exc}")

    st.divider()
    render_section_header(*t["sections"]["snapshot"])
    render_evidence_snapshot(t["evidence_snapshot"])

"""
Research-facing workbench for the climate-sensitive chronic disease KG platform.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from arthritis_platform.web.language import (  # noqa: E402
    get_text,
    localized_evidence_triage,
    localized_platform_metrics,
    localized_research_readiness,
)
from arthritis_platform.web.navigation import language_selectbox  # noqa: E402
from arthritis_platform.web.runtime import create_runtime, get_live_update_status  # noqa: E402
from arthritis_platform.web.ui_theme import (  # noqa: E402
    inject_theme,
    render_evidence_snapshot,
    render_hero,
    render_insight_cards,
    render_metric_strip,
    render_pipeline,
    render_ranked_bar_list,
    render_section_header,
    render_sidebar_card,
    render_workbench_cards,
)


st.set_page_config(
    page_title="气候-慢性病科研工作台 / Climate-Chronic Disease Research",
    page_icon="R",
    layout="wide",
)

inject_theme("researcher")

with st.sidebar:
    _, lang = language_selectbox(st, key="research_language")
t = get_text("research", lang)

render_hero(**t["hero"])


@st.cache_resource
def init_runtime():
    return create_runtime()


runtime = init_runtime()
rag = runtime.rag
graph = runtime.graph


def ask_research_question(question: str) -> None:
    st.session_state[f"researcher_pending_prompt_{lang}"] = question
    st.rerun()


def ranked(rows, label_key: str, value_key: str, limit: int = 10) -> None:
    render_ranked_bar_list(rows, label_key, value_key, limit=limit, empty_message=t["empty_bar"])


render_metric_strip(localized_platform_metrics(graph, lang))

render_section_header(*t["sections"]["value"])
render_insight_cards(t["original_cards"])

render_section_header(*t["sections"]["research_path"])
render_evidence_snapshot(t["research_path_rows"])

render_section_header(*t["sections"]["intelligence"])
render_insight_cards(t["intelligence_cards"])

render_section_header(*t["sections"]["hypotheses"])
render_evidence_snapshot(t["hypothesis_rows"])

render_section_header(*t["sections"]["readiness"])
render_evidence_snapshot(localized_research_readiness(graph, lang))

render_section_header(*t["sections"]["triage"])
render_evidence_snapshot(localized_evidence_triage(graph, lang))

render_pipeline(t["pipeline"])
render_workbench_cards(t["workbench"])

with st.sidebar:
    render_sidebar_card(t["sidebar"]["title"], t["sidebar"]["body"], t["sidebar"]["items"])
    st.divider()
    st.subheader(t["sidebar"]["options"])
    max_results = st.slider(t["sidebar"]["max_results"], 5, 30, 10)
    include_studies = st.checkbox(t["sidebar"]["include_studies"], value=True)
    export_format = st.selectbox(t["sidebar"]["export_format"], ["JSON", "CSV"])
    st.divider()
    st.caption(t["sidebar"]["caption"])

tab_qa, tab_query, tab_analysis, tab_cypher, tab_export, tab_governance = st.tabs(t["tabs"])

with tab_qa:
    render_section_header(*t["sections"]["qa"])

    messages_key = f"researcher_messages_{lang}"
    pending_key = f"researcher_pending_prompt_{lang}"
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []
    if pending_key not in st.session_state:
        st.session_state[pending_key] = ""

    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.session_state[pending_key] or st.chat_input(t["qa"]["input"])
    st.session_state[pending_key] = ""

    if prompt:
        st.session_state[messages_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t["qa"]["spinner"]):
                try:
                    result = rag.answer_question(prompt, role="researcher", max_results=max_results)
                    answer = result["answer"]
                    st.markdown(answer)

                    with st.expander(t["qa"]["details"], expanded=False):
                        st.json(result["question_analysis"])
                        st.write(f"**{t['qa']['entities']}:** {len(result['knowledge']['entities'])}")
                        st.write(f"**{t['qa']['relations']}:** {len(result['knowledge']['relations'])}")
                        st.write(f"**{t['qa']['studies']}:** {len(result['knowledge']['studies'])}")
                        st.write(f"**{t['qa']['triage']}:** {len(result['knowledge'].get('triage', []))}")
                        if result.get("boundary"):
                            st.write(f"**{t['qa'].get('boundary', 'Evidence boundary')}:**")
                            st.json(result["boundary"])
                        if result.get("claim_ledger"):
                            st.write(f"**{t['qa'].get('claim_ledger', 'Claim-evidence ledger')}:**")
                            st.dataframe(pd.DataFrame(result["claim_ledger"]), use_container_width=True)

                    if include_studies and result["knowledge"]["studies"]:
                        with st.expander(t["qa"]["study_list"]):
                            for study in result["knowledge"]["studies"]:
                                st.markdown(
                                    f"**PMID: {study['pmid']}** ({study.get('year', 'N/A')})  \n"
                                    f"{study.get('title', 'N/A')}"
                                )
                                st.divider()

                    st.session_state[messages_key].append({"role": "assistant", "content": answer})
                except Exception as exc:
                    st.error(f"{t['qa']['error']}{exc}")

    st.divider()
    render_section_header(*t["sections"]["examples"])
    example_cols = st.columns(2)
    for index, example in enumerate(t["examples"]):
        with example_cols[index % 2]:
            if st.button(example["button"], key=f"research_example_{lang}_{index}", use_container_width=True):
                ask_research_question(example["prompt"])

with tab_query:
    render_section_header(*t["sections"]["advanced"])
    q = t["advanced"]

    selected_query_label = st.selectbox(q["query_type"], list(q["types"].keys()))
    query_kind = q["types"][selected_query_label]

    if query_kind == "entity":
        entity_name = st.text_input(q["entity_name"])
        if st.button(q["search"], key=f"research_entity_search_{lang}"):
            try:
                results = graph.search_entity(entity_name)
                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                else:
                    st.warning(q["no_results"])
            except Exception as exc:
                st.error(f"{q['failed']}{exc}")

    elif query_kind == "path":
        col_source, col_target = st.columns(2)
        with col_source:
            entity1 = st.text_input(q["source"])
        with col_target:
            entity2 = st.text_input(q["target"])

        max_length = st.slider(q["max_path"], 1, 5, 3)
        if st.button(q["find_path"], key=f"research_find_path_{lang}"):
            if entity1 and entity2:
                try:
                    paths = graph.find_shortest_path(entity1, entity2, max_length)
                    if paths:
                        for index, path in enumerate(paths, start=1):
                            st.write(f"**{q['path'].format(i=index, n=path['length'])}:**")
                            path_nodes = [str(node) for node in path["path"] if node is not None]
                            path_rels = [str(rel) for rel in path["relations"] if rel is not None]
                            if path_nodes:
                                st.text(" -> ".join(path_nodes))
                            if path_rels:
                                st.caption(q["relations"].format(items=" -> ".join(path_rels)))
                            st.divider()
                    else:
                        st.warning(q["no_path"])
                except Exception as exc:
                    st.error(f"{q['failed']}{exc}")

    elif query_kind == "cooccurrence":
        entity = st.text_input(q["entity_name"])
        min_studies = st.number_input(q["min_studies"], 1, 10, 2)
        if st.button(q["analyze"], key=f"research_cooccurrence_{lang}"):
            try:
                results = graph.find_co_occurrence(entity, min_studies)
                if results:
                    st.write(f"**{q['cooccur'].format(entity=entity)}**")
                    df = pd.DataFrame(results)
                    value_key = "共同研究数"
                    if lang == "en":
                        df = df.rename(columns={"共同研究数": "co_occurring_studies"})
                        value_key = "co_occurring_studies"
                    st.dataframe(df, use_container_width=True)
                    if "entity" in df.columns and value_key in df.columns:
                        ranked(df.to_dict("records"), "entity", value_key)
                else:
                    st.warning(q["no_cooccur"])
            except Exception as exc:
                st.error(f"{q['analysis_failed']}{exc}")

    elif query_kind == "subgraph":
        entity = st.text_input(q["center"])
        depth = st.slider(q["depth"], 1, 3, 2)
        if st.button(q["extract"], key=f"research_extract_subgraph_{lang}"):
            try:
                subgraph = graph.get_subgraph(entity, depth)
                if subgraph and subgraph.get("nodes"):
                    st.success(
                        q["extracted"].format(
                            nodes=len(subgraph["nodes"]),
                            rels=len(subgraph.get("relationships", [])),
                        )
                    )
                    col_nodes, col_rels = st.columns(2)
                    with col_nodes:
                        st.write(f"**{q['nodes']}:**")
                        st.json(subgraph["nodes"])
                    with col_rels:
                        st.write(f"**{q['relationships']}:**")
                        st.json(subgraph.get("relationships", []))
                else:
                    st.warning(q["no_subgraph"])
            except Exception as exc:
                st.error(f"{q['extract_failed']}{exc}")

with tab_analysis:
    render_section_header(*t["sections"]["analysis"])
    render_evidence_snapshot(t["evidence_snapshot"])
    st.divider()
    render_section_header(*t["sections"]["triage"])
    render_evidence_snapshot(localized_evidence_triage(graph, lang))
    st.divider()

    a = t["analysis"]
    selected_analysis_label = st.radio(a["type"], list(a["types"].keys()), horizontal=True)
    analysis_kind = a["types"][selected_analysis_label]

    if analysis_kind == "hotspot":
        st.markdown(f"### {a['hotspots']}")
        col_climate, col_chronic, col_symptoms = st.columns(3)
        top_specs = [
            (col_climate, a["climate"], "ClimateFactor"),
            (col_chronic, a["arthritis"], "ChronicDisease"),
            (col_symptoms, a["symptoms"], "Symptom"),
        ]
        for column, label, entity_type in top_specs:
            with column:
                st.write(f"**{label}**")
                top_entities = graph.get_top_entities(entity_type, 10)
                if top_entities:
                    st.dataframe(pd.DataFrame(top_entities), use_container_width=True)
                    ranked(top_entities, "name", "study_count")

    elif analysis_kind == "gaps":
        st.markdown(f"### {a['gap_title']}")
        st.info(a["gap_info"])
        entity_type = st.selectbox(a["entity_type"], ["ClimateFactor", "ChronicDisease", "Symptom", "ArthritisType"])
        if st.button(a["detect"], key=f"research_identify_gaps_{lang}"):
            gaps = graph.find_research_gaps(entity_type)
            if gaps:
                st.warning(a["detected"].format(n=len(gaps), kind=entity_type))
                st.dataframe(pd.DataFrame(gaps), use_container_width=True)
                st.markdown(f"**{a['suggestions']}**")
                for gap in gaps[:5]:
                    st.write(f"- {gap['name']} ({a['supporting'].format(n=gap['study_count'])})")
            else:
                st.success(a["no_gaps"])

    elif analysis_kind == "relations":
        st.markdown(f"### {a['relationship_title']}")
        stats = graph.get_statistics()
        if stats.get("relations"):
            rel_df = pd.DataFrame(stats["relations"])
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                ranked(stats["relations"], "type", "count")
            with col_table:
                st.dataframe(rel_df, use_container_width=True)

            st.divider()
            entity = st.text_input(a["inspect_entity"])
            if entity and st.button(a["query"], key=f"research_relation_dist_{lang}"):
                dist = graph.get_relation_distribution(entity)
                if dist:
                    st.dataframe(pd.DataFrame(dist), use_container_width=True)
                    ranked(dist, "relation_type", "count")

with tab_cypher:
    render_section_header(*t["sections"]["cypher"])
    c = t["cypher"]
    st.caption(c["info"])

    query_map = {
        "All node counts": "MATCH (n) RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC",
        "All relationship counts": "MATCH ()-[r]->() RETURN type(r) as type, count(*) as count ORDER BY count DESC",
        "Highly connected entities": "MATCH (n)-[r]-() WITH n, count(r) as degree WHERE degree > 10 RETURN n.name as entity, labels(n)[0] as type, degree ORDER BY degree DESC LIMIT 20",
        "Recent studies": "MATCH (s:Study) WHERE s.publication_date IS NOT NULL RETURN s.pmid, s.title, s.publication_date ORDER BY s.publication_date DESC LIMIT 10",
    }
    preset_labels = [c["custom"]] + list(c["presets"].keys())
    selected_preset = st.selectbox(c["preset"], preset_labels)
    preset_key = c["presets"].get(selected_preset)
    cypher_query = query_map.get(preset_key, "")
    cypher_input = st.text_area(c["input"], value=cypher_query, height=150)

    col_run, col_example = st.columns([1, 4])
    with col_run:
        execute_btn = st.button(c["run"], key=f"research_cypher_execute_{lang}", use_container_width=True)
    with col_example:
        st.caption(c["example"])

    if execute_btn and cypher_input:
        try:
            with st.spinner(c["spinner"]):
                results = graph.execute_read_query(cypher_input)
                if results:
                    st.success(c["returned"].format(n=len(results)))
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    if export_format == "JSON":
                        st.download_button(
                            c["download_json"],
                            data=json.dumps(results, ensure_ascii=False, indent=2),
                            file_name="query_results.json",
                            mime="application/json",
                        )
                    elif export_format == "CSV":
                        st.download_button(
                            c["download_csv"],
                            data=df.to_csv(index=False),
                            file_name="query_results.csv",
                            mime="text/csv",
                        )
                else:
                    st.warning(c["none"])
        except Exception as exc:
            st.error(f"{c['failed']}{exc}")

with tab_export:
    render_section_header(*t["sections"]["export"])
    e = t["export"]
    selected_export_label = st.selectbox(e["type"], list(e["types"].keys()))
    export_kind = e["types"][selected_export_label]

    if st.button(e["button"], key=f"research_export_data_{lang}"):
        with st.spinner(e["spinner"]):
            try:
                if export_kind == "stats":
                    payload = graph.get_statistics()
                    filename = "graph_statistics.json"
                elif export_kind == "entities":
                    entities = []
                    for entity_type in ["ChronicDisease", "ArthritisType", "ClimateFactor", "Symptom"]:
                        entities.extend(graph.get_top_entities(entity_type, 100))
                    payload = entities
                    filename = "entities.json"
                elif export_kind == "relationships":
                    cypher = "MATCH (e1)-[r]->(e2) RETURN e1.name as source, type(r) as relation, e2.name as target LIMIT 1000"
                    payload = graph.execute_query(cypher)
                    filename = "relationships.json"
                else:
                    cypher = "MATCH (s:Study) RETURN s.pmid as pmid, s.title as title, s.year as year ORDER BY s.year DESC"
                    payload = graph.execute_query(cypher)
                    filename = "studies.json"

                data = json.dumps(payload, ensure_ascii=False, indent=2)
                st.success(e["success"])
                st.download_button(e["download"], data=data, file_name=filename, mime="application/json")
                with st.expander(e["preview"]):
                    st.json(json.loads(data))
            except Exception as exc:
                st.error(f"{e['failed']}{exc}")

with tab_governance:
    render_section_header(*t["sections"]["governance"])
    g = t["governance"]

    try:
        schema_overview = graph.get_schema_overview()
        quality_snapshot = graph.get_quality_snapshot()
        temporal_coverage = graph.get_temporal_coverage()

        provenance = quality_snapshot.get("provenance", {})
        entity_quality = quality_snapshot.get("entity_quality", {})
        relationship_quality = quality_snapshot.get("relationship_quality", {})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(g["assertions"], provenance.get("assertions", 0))
        with col2:
            st.metric(g["assertions_pmid"], provenance.get("assertions_with_study", 0))
        with col3:
            st.metric(g["missing_ids"], entity_quality.get("missing_ids", 0))
        with col4:
            st.metric(g["missing_pmids"], relationship_quality.get("missing_pmids", 0))

        st.divider()
        render_section_header(*t["sections"]["scope"])
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(g["window"], f"{temporal_coverage.get('start_year', 2006)}-{temporal_coverage.get('end_year', 'current')}")
        with col2:
            st.metric(g["covered_years"], temporal_coverage.get("covered_years", 0))
        with col3:
            st.metric(g["candidates"], f"{temporal_coverage.get('queried_pubmed_records', 'live KG')}")
        with col4:
            st.metric(g["gain"], f"+{temporal_coverage.get('additional_candidate_records', 'NA')}")

        annual_counts = temporal_coverage.get("annual_counts", [])
        if annual_counts:
            st.markdown(f"### {g['year_coverage']}")
            ranked(annual_counts, "year", "records", limit=len(annual_counts))

        st.caption(
            g["scope_source"].format(
                source=temporal_coverage.get("source", "PubMed"),
                start=temporal_coverage.get("publication_window_start", "2006/01/01"),
                end=temporal_coverage.get("publication_window_end", "current"),
                label=temporal_coverage.get("window_label", "near-20-year publication window"),
            )
        )

        st.divider()
        render_section_header(*t["sections"]["schema"])
        col_nodes, col_rels = st.columns(2)
        with col_nodes:
            st.markdown(f"### {g['node_schema']}")
            nodes_df = pd.DataFrame(schema_overview.get("nodes", []))
            if not nodes_df.empty:
                st.dataframe(nodes_df, use_container_width=True)
                if "type" in nodes_df.columns and "count" in nodes_df.columns:
                    ranked(nodes_df.to_dict("records"), "type", "count")
            else:
                st.info(g["no_node"])

        with col_rels:
            st.markdown(f"### {g['relationship_schema']}")
            rel_df = pd.DataFrame(schema_overview.get("relationships", []))
            if not rel_df.empty:
                st.dataframe(rel_df, use_container_width=True)
                value_key = "support_count" if "support_count" in rel_df.columns else "edge_count"
                if "relation_type" in rel_df.columns and value_key in rel_df.columns:
                    ranked(rel_df.to_dict("records"), "relation_type", value_key)
            else:
                st.info(g["no_rel"])

        st.divider()
        render_section_header(*t["sections"]["rationale"])
        render_workbench_cards(g["rationale_cards"])

        st.divider()
        render_section_header(*t["sections"]["live"])
        update_status = get_live_update_status()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(g["tracked"], update_status.get("seen_pmids", 0))
        with col2:
            st.metric(g["last_status"], update_status.get("last_run_status", "No runs yet"))
        with col3:
            live_state = g["enabled"] if update_status.get("enabled") else g["not_initialized"]
            st.metric(g["live_state"], live_state)
        st.caption(g["last_success"].format(value=update_status.get("last_success_at")))
        if update_status.get("last_manifest"):
            st.code(str(update_status["last_manifest"]), language="text")

    except Exception as exc:
        st.error(f"{g['failed']}{exc}")

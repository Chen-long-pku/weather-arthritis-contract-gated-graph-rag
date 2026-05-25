"""
Public-facing health education page for the climate-sensitive chronic disease KG platform.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from arthritis_platform.web.language import (  # noqa: E402
    get_text,
)
from arthritis_platform.web.navigation import language_selectbox  # noqa: E402
from arthritis_platform.web.runtime import create_runtime  # noqa: E402
from arthritis_platform.web.ui_theme import (  # noqa: E402
    inject_theme,
    render_entity_cards,
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
    page_title="天气与慢性病 / Weather and Chronic Disease",
    page_icon="H",
    layout="wide",
)

inject_theme("public")

with st.sidebar:
    _, lang = language_selectbox(st, key="public_language")
t = get_text("public", lang)

render_hero(**t["hero"])


@st.cache_resource
def init_runtime():
    return create_runtime()


runtime = init_runtime()
rag = runtime.rag

render_metric_strip(t["metrics"])

render_section_header(*t["sections"]["value"])
render_insight_cards(t["cards"])

render_section_header(*t["sections"]["self_check"])
render_evidence_snapshot(t["self_check_rows"])

render_section_header(*t["sections"]["visit_note"])
render_evidence_snapshot(t["visit_note_rows"])

render_pipeline(t["pipeline"])
render_workbench_cards(t["workbench"])

with st.sidebar:
    render_sidebar_card(t["sidebar"]["title"], t["sidebar"]["body"], t["sidebar"]["items"])
    st.divider()
    st.caption(t["sidebar"]["caption"])

messages_key = f"public_messages_{lang}"
pending_key = f"public_pending_prompt_{lang}"
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
                result = rag.answer_question(prompt, role="public", max_results=5)
                answer = result["answer"]
                st.markdown(answer)

                with st.expander(t["chat"]["sources"]):
                    if result.get("boundary"):
                        st.write(f"**{t['chat'].get('boundary', 'Evidence boundary')}**")
                        st.json(result["boundary"])
                    if result.get("claim_ledger"):
                        st.write(f"**{t['chat'].get('claim_ledger', 'Claim-evidence ledger')}**")
                        st.dataframe(result["claim_ledger"], use_container_width=True)
                    if result["knowledge"]["entities"]:
                        st.write(f"**{t['chat']['concepts']}**")
                        render_entity_cards(
                            result["knowledge"]["entities"],
                            limit=3,
                            study_label=t["chat"]["study_label"],
                        )
                    else:
                        st.info(t["chat"]["no_knowledge"])

                st.session_state[messages_key].append({"role": "assistant", "content": answer})
            except Exception as exc:
                error_msg = f"{t['chat']['error']}{exc}"
                st.error(error_msg)
                st.session_state[messages_key].append({"role": "assistant", "content": error_msg})

st.divider()
render_section_header(*t["sections"]["quick"])

quick_cols = st.columns(3)


def ask_quick_question(question: str):
    st.session_state[pending_key] = question
    st.rerun()


for index, question in enumerate(t["quick_questions"]):
    with quick_cols[index]:
        if st.button(question["button"], key=f"public_quick_{lang}_{index}", use_container_width=True):
            ask_quick_question(question["prompt"])

if st.session_state[messages_key]:
    if st.button(t["chat"]["clear"], key=f"public_clear_history_{lang}"):
        st.session_state[messages_key] = []
        st.session_state[pending_key] = ""
        st.rerun()

st.divider()
render_section_header(*t["sections"]["snapshot"])
render_evidence_snapshot(t["evidence_snapshot"])

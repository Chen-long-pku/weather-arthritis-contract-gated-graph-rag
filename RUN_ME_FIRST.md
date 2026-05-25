# Run Me First

This package can be run in two modes.

## Local Evidence-Base Mode

This mode does not require Neo4j or an external LLM key. It uses an embedded climate-sensitive chronic disease evidence graph plus a clinically bounded evidence triage layer, so the three user-facing pages can be opened immediately and reviewed offline.

## Tested Environment

The review environment was tested with Python 3.10.x. Python 3.11 is expected to work but should be verified locally; Python 3.12 has not been fully tested for this package.

Check Python before installing:

```bash
python --version
```

Install the interface dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_platform.txt
```

Launch the home page and the three role-specific pages. Open one terminal window for each command:

```bash
./run_home_demo.sh
./run_public_demo.sh
./run_medical_demo.sh
./run_researcher_demo.sh
```

On Windows PowerShell, use:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements_platform.txt
.\run_home_demo.ps1
.\run_public_demo.ps1
.\run_medical_demo.ps1
.\run_researcher_demo.ps1
```

Open the unified home page first:

- Home page: http://localhost:8500

The home page contains the language selector and three role buttons. The buttons pass the selected language into:

- Public chronic disease page: http://localhost:8501
- Medical evidence triage workbench: http://localhost:8502
- Climate-chronic disease research studio with research-readiness stratification: http://localhost:8503

Each role page still keeps a sidebar language selector for quick switching after entry.

Recommended review sequence:

1. Open the public page and inspect the visit-note and care-boundary content.
2. Open the medical page and inspect `Evidence Triage / 证据分诊` and follow-up documentation points.
3. Open the research page and inspect `Research Evidence Intelligence / 科研证据智能` and `Research Readiness / 研究就绪度`.

## Live Graph-RAG Mode

1. Copy `.env.example` to `.env`.
2. Fill in `DEEPSEEK_API_KEY`, `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`.
3. Start Neo4j.
4. Install the full requirements:

```bash
pip install -r requirements.txt
pip install -r requirements_platform.txt
pip install -r requirements_extraction.txt
```

5. Run one interface:

```bash
streamlit run arthritis_platform/web/researcher_app.py --server.port 8503
```

## Living Knowledge Base Update

After filling PubMed, LLM, and Neo4j settings in `.env`, run one update:

```bash
python update_knowledge_base.py --verbose
```

Run as a scheduled updater every six hours:

```bash
python update_knowledge_base.py --watch --interval-minutes 360 --verbose
```

The updater writes manifests and state files under `data/live_updates/`.

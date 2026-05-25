# Usage

## Literature Retrieval

Use `pubmed_searcher.py` to retrieve PubMed metadata and `pdf_downloader.py` to download open-access PDFs when available.

The default PubMed scope is a rolling near-20-year publication window:

```text
PUBMED_START_DATE=2006/01/01
PUBMED_END_DATE=auto
PUBMED_DISEASE_SCOPE=common_chronic
```

With the current arthritis feasibility query, the 2006-current window returned 1,992 PubMed candidate records on 2026-05-07. The earlier 2015-current window returned 1,339 records, so the expanded feasibility KG scope adds approximately 653 candidate records before PDF filtering and LLM extraction. Broader common-chronic-disease searches use the same configurable PubMed window and graph construction workflow.

To reproduce the manuscript arthritis feasibility corpus exactly, set:

```text
PUBMED_DISEASE_SCOPE=arthritis_pilot
```

## Entity-Relation Extraction

Run the extraction workflow with `run_extraction.py`. The extraction modules support abstract-level and optional full-text workflows. The manuscript reports abstract-level extraction to maximize corpus coverage.

## Graph Construction

The graph builder imports extracted entities and relationships into Neo4j. Primary node labels are:

- `Study`
- `ChronicDisease`
- `ArthritisType`
- `ClimateFactor`
- `Symptom`

Build the provenance-aware evidence graph:

```bash
python -m knowledge_graph.graph_builder \
  data/extraction_results/extraction_results_20251210_183902.json \
  --report-file data/graph_reports/build_report.json
```

Run a quality audit after import:

```python
from knowledge_graph.neo4j_connector import Neo4jConnector
from knowledge_graph.quality_audit import GraphQualityAuditor

connector = Neo4jConnector("bolt://localhost:7687", "neo4j", "password")
GraphQualityAuditor(connector).write_report("data/graph_reports/quality_audit.json")
connector.close()
```

Primary relationship labels include:

- `STUDIED_IN`
- `CORRELATES_WITH`
- `INCREASES`
- `DECREASES`
- `NO_EFFECT`
- `AFFECTS`
- `EXACERBATES`
- `AMELIORATES`

## Web Interfaces

For product screenshots or manuscript demonstration, the apps can run without live infrastructure:

```bash
PLATFORM_DEMO_MODE=1 streamlit run arthritis_platform/web/public_app.py --server.port 8501
```

The demo mode uses a deterministic in-memory evidence graph and clearly labels the session as client demo mode. If credentials or dependencies are missing, the apps fall back to this mode automatically.

Public interface:

```bash
streamlit run arthritis_platform/web/public_app.py --server.port 8501
```

Medical interface:

```bash
streamlit run arthritis_platform/web/medical_app.py --server.port 8502
```

Researcher interface:

```bash
streamlit run arthritis_platform/web/researcher_app.py --server.port 8503
```

The platform is organized as three separate client-facing pages:

- Public page: plain-language explanation, symptom/risk recording prompts, care-seeking boundaries, and common climate-sensitive chronic disease questions.
- Medical page: clinical evidence summary, evidence triage grades, mechanism explanation, PMID tracing, patient counseling language, warning-signal boundaries, and entity lookup for chronic disease scenarios.
- Research page: Original Research framing, research-readiness stratification, chronic-disease evidence intelligence, hypothesis bank, advanced graph queries, KG governance, and export.

Each page has a sidebar language selector with full Chinese and full English versions of the visible interface. The three pages share the same underlying KG but avoid mixing audiences in one interface. The public page is practical and non-diagnostic, the medical page is evidence-aware and traceable, and the research page is designed for manuscript results, hypothesis generation, and downloadable outputs.

## Evidence Triage Layer

The clinical and research pages expose a triage layer above the graph. This layer does not change the underlying evidence; it classifies modules for safer translation and manuscript interpretation:

- Evidence interpretation: literature-based scaffold, plausible scaffold, expert-adjudicated feasibility evidence, or hypothesis-generating service-continuity scaffold.
- Validation status: preliminary expert adjudication for the arthritis/weather-pain module, or ontology-supported extension requiring disease-specific extraction and expert validation.
- Communication/documentation action: communication or follow-up use that remains separate from diagnosis, prediction, and medication adjustment.
- Research readiness: whether a module is ready for immediate follow-up study design or requires additional extraction and expert review.

## Claim-Level Evidence Ledger

The Graph-RAG answer object includes a claim-level ledger. The ledger records:

- answer scope and validation status;
- evidence triage claims;
- PMID-traceable literature context;
- abstention or clinical-decision blocking triggers;
- role-specific use boundaries.

This is intended to make the answer auditable at the claim level. It does not prove clinical validity.

## Safety Notes

The system is an evidence translation prototype. It does not provide diagnosis, individualized medical advice, or clinical decision support.

## Living Knowledge Base Updates

Run one incremental update:

```bash
python update_knowledge_base.py --verbose
```

Keep the updater running every six hours:

```bash
python update_knowledge_base.py --watch --interval-minutes 360 --verbose
```

For a dry discovery pass that does not call the LLM or write to Neo4j:

```bash
python update_knowledge_base.py --discover-only --verbose
```

See `docs/live_update.md` for the full update design.

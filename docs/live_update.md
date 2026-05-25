# Scheduled Incremental Knowledge Base Updates

The platform can operate as a living evidence graph. Because PubMed is not a second-by-second streaming source, the update design uses scheduled incremental polling.

The historical KG build now uses a near-20-year publication scope. In this submission package, PubMed retrieval includes records from `2006/01/01` through `2026/05/24`. This broadens the candidate evidence pool while live updates still use Entrez/update dates to discover newly entered or modified records inside that publication window.

## Pipeline

1. Query PubMed for newly entered or updated records using an overlap window.
2. Filter PMIDs already stored in `data/live_updates/live_update_state.json`.
3. Save new metadata as `pubmed_delta_YYYYMMDD_HHMMSS.json`.
4. Run LLM-assisted entity-relation extraction on new abstracts.
5. Append new `Study`, `Entity`, `EvidenceAssertion`, and evidence edges to Neo4j.
6. Generate graph build and quality audit JSON reports.
7. Update the live state file and run manifest.

## One-Time Update

```bash
python update_knowledge_base.py --verbose
```

## Discovery Only

```bash
python update_knowledge_base.py --discover-only --verbose
```

## Watch Mode

Run every six hours:

```bash
python update_knowledge_base.py --watch --interval-minutes 360 --verbose
```

## Environment Variables

```text
PUBMED_EMAIL=your_email@example.com
NCBI_API_KEY=your_ncbi_api_key
PUBMED_START_DATE=2006/01/01
PUBMED_END_DATE=auto
DEEPSEEK_API_KEY=your_deepseek_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j
LIVE_UPDATE_MODEL=deepseek
LIVE_UPDATE_DIR=data/live_updates
LIVE_UPDATE_STATE_FILE=data/live_updates/live_update_state.json
LIVE_UPDATE_RETMAX=200
LIVE_UPDATE_LOOKBACK_DAYS=14
LIVE_UPDATE_INTERVAL_MINUTES=360
```

## Monitoring

The researcher interface includes a KG governance section that displays the live update status, tracked PMID count, last run status, and last successful update time.
It also displays the near-20-year publication window, annual study-node coverage, and the PubMed candidate-pool size used for the expanded KG scope.

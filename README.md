# Contract-gated Graph-RAG for weather-sensitive arthritis

This repository is the code-only public snapshot for the manuscript:

**Contract-gated Graph-RAG with an evidence ledger for weather-sensitive arthritis: a feasibility and clinician-adjudicated content-risk evaluation**

The repository contains source code, evaluation scripts, extraction workflow scripts, and run documentation. It does not contain raw clinician-review workbooks, question-level adjudication datasets, internal quality-control logs, API keys, or local cache files. Aggregate tables and figures are provided with the article and Supplementary Materials.

## Manuscript scope

The study evaluates a software method for answer-level governance in a PubMed-derived Graph-RAG prototype focused on weather-sensitive arthritis evidence. The evaluated method is a contract-gated pipeline: before generation, the system compiles an evidence contract that specifies risk tier, evidence sufficiency, forbidden actions, required answer elements, and allowed content; after generation, a verifier checks the answer against the contract and the system records a claim-level evidence ledger.

This software is research infrastructure. It is not certified medical software, not a clinical decision-support system, and must not be used to diagnose, predict, treat, or adjust medication for individual patients.

## What this repository contains

- `arthritis_platform/services/evidence_contract.py`: evidence-contract compiler and post-generation verifier.
- `arthritis_platform/services/rag_engine.py`: Graph-RAG orchestration for retrieval, answer generation, contract verification, and claim-ledger generation.
- `arthritis_platform/services/claim_ledger.py`: claim-level evidence ledger utilities.
- `evaluation/contract_gated/run_contract_gated_eval.py`: evaluation runner for the locked question/context file when available to authorized users.
- `evaluation/contract_gated/process_contract_gated_outputs.py`: conversion from generated answers to blinded review forms and analysis-ready files.
- `extraction/quote_first_extractor.py`: quote-first evidence-span anchoring workflow for graph-candidate extraction.
- `evaluation/quote_first_extraction/run_quote_first_extraction_audit.py`: replay script for the extraction quality-control workflow.
- `docs/`: installation, usage, validation, and extraction workflow notes.
- `requirements*.txt`: dependency lists for the platform and extraction workflows.

## Data availability used with this code release

The public release is intentionally code-only. Tables and figures are included in the article and Supplementary Materials. De-identified question-level and clinician-rating data supporting the reported analyses are available from the corresponding author upon reasonable request, subject to author approval and journal policy.

## Installation

For a quick local review, start with `RUN_ME_FIRST.md`. A typical setup is:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_platform.txt
pip install -r requirements_extraction.txt
```

If using external model calls, provide API keys through a local `.env` file. Do not commit `.env` files or API keys.

## Evaluation scripts

The paired evaluation script expects a locked question/context CSV supplied by the study team or by an authorized reproducer:

```bash
python evaluation/contract_gated/run_contract_gated_eval.py --input path/to/questions.csv --output-dir outputs/contract_gated
python evaluation/contract_gated/process_contract_gated_outputs.py --input-dir outputs/contract_gated --output-dir outputs/review
```

Generated reviewer forms and analysis files should be handled according to the study's data-sharing statement and should not be committed unless public release has been approved.

## Extraction quality-control workflow

The quote-first extractor anchors candidate graph relations to exact source sentences before graph insertion. It prioritizes traceability and expert-auditable candidates over automatic graph expansion.

```bash
python evaluation/quote_first_extraction/run_quote_first_extraction_audit.py --input-workbook path/to/audit.xlsx --output-dir outputs/extraction_qc
```

Human review remains required before extracted candidates are described as curated graph edges.

## Citation

After publication, cite the article and the archived Zenodo/OSF code release DOI.

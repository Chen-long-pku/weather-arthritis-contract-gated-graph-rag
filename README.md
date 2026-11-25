# Auditable evidence governance for weather-sensitive arthritis Graph-RAG

## Current code and data release: v2.0.0

The corrected, versioned code-and-data archive was published on Zenodo on 24 November 2026:

**[Zenodo v2.0.0: 10.5281/zenodo.24496084](https://doi.org/10.5281/zenodo.24496084)**

Download `weather-arthritis-evidence-governance-v2.0.0-code-data.zip` from that record and follow the README and reproduction instructions inside the archive. It includes de-identified question-level records, stored retrieval contexts, model answers, clinician ratings, correction records, and analysis code supporting the revised paired evaluation. The archive contains 180 stored answers per workflow, including recorded elapsed times.

This GitHub repository retains the earlier code snapshot. Its source tree, configuration defaults, historical documentation, and v1 tags have not been replaced by the v2.0.0 archive. Use the fixed Zenodo version for the revised analyses; do not treat the legacy GitHub defaults as a complete record of the primary-run configuration. Offline reanalysis of the retained outputs is distinct from regenerating the original model responses.

The Zenodo archive is distributed under CC BY 4.0, subject to the scope and third-party notices stated in its license files. Manuscripts, submission figures, graphical abstracts, response letters, author signatures, and private correspondence are not part of the public release.

## Study scope

The study evaluates a bundled evidence-governance workflow for a PubMed-derived Graph-RAG prototype using weather-sensitive arthritis questions. It examines adjudicated answer-level content-risk outcomes, source-linked evidence records, and the trade-off with perceived usefulness. The paired comparison does not isolate the causal effect of any single workflow component. This is research software, not a validated clinical decision-support tool.

## Legacy GitHub snapshot

The following files and usage notes describe the earlier implementation retained in this repository. For the revised reproducibility release, use the Zenodo link above.

### Files in the earlier snapshot

- `arthritis_platform/services/evidence_contract.py`: evidence-contract compiler and post-generation verifier.
- `arthritis_platform/services/rag_engine.py`: Graph-RAG orchestration for retrieval, answer generation, contract verification, and claim-ledger generation.
- `arthritis_platform/services/claim_ledger.py`: claim-level evidence ledger utilities.
- `evaluation/contract_gated/run_contract_gated_eval.py`: evaluation runner for the locked question/context file when available to authorized users.
- `evaluation/contract_gated/process_contract_gated_outputs.py`: conversion from generated answers to blinded review forms and analysis-ready files.
- `extraction/quote_first_extractor.py`: quote-first evidence-span anchoring workflow for graph-candidate extraction.
- `evaluation/quote_first_extraction/run_quote_first_extraction_audit.py`: replay script for the extraction quality-control workflow.
- `docs/`: installation, usage, validation, and extraction workflow notes.
- `requirements*.txt`: dependency lists for the platform and extraction workflows.

### Data availability

The earlier GitHub snapshot was code-only. The updated de-identified code-and-data release is now openly available in [Zenodo v2.0.0](https://doi.org/10.5281/zenodo.24496084). This statement supersedes the request-only data-access wording in historical repository documentation.

### Legacy installation

For a quick local review, start with `RUN_ME_FIRST.md`. A typical setup is:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_platform.txt
pip install -r requirements_extraction.txt
```

If using external model calls, provide API keys through a local `.env` file. Do not commit `.env` files or API keys.

### Legacy evaluation scripts

The paired evaluation script expects a locked question/context CSV supplied by the study team or by an authorized reproducer:

```bash
python evaluation/contract_gated/run_contract_gated_eval.py --input path/to/questions.csv --output-dir outputs/contract_gated
python evaluation/contract_gated/process_contract_gated_outputs.py --input-dir outputs/contract_gated --output-dir outputs/review
```

Generated reviewer forms and analysis files should be handled according to the study's data-sharing statement and should not be committed unless public release has been approved.

### Legacy extraction quality-control workflow

The quote-first extractor anchors candidate graph relations to exact source sentences before graph insertion. It prioritizes traceability and expert-auditable candidates over automatic graph expansion.

```bash
python evaluation/quote_first_extraction/run_quote_first_extraction_audit.py --input-workbook path/to/audit.xlsx --output-dir outputs/extraction_qc
```

Human review remains required before extracted candidates are described as curated graph edges.

## Citation

For the corrected code and data, cite Zenodo version 2.0.0, DOI: [10.5281/zenodo.24496084](https://doi.org/10.5281/zenodo.24496084), using the citation metadata supplied by the record. Cite the associated article separately once published.

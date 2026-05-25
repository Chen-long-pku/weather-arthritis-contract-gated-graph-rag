# Public Repository Candidate

This folder is a cleaned code snapshot for the final contract-gated Graph-RAG feasibility analysis. It excludes temporary reruns, review workbooks, virtual environments, API keys, local cache files, and question-level adjudication datasets.

Key implementation files:

- `arthritis_platform/services/evidence_contract.py`: evidence-contract compiler and post-generation contract verifier.
- `arthritis_platform/services/rag_engine.py`: Graph-RAG orchestration that calls retrieval, boundary assessment, evidence contract compilation, answer generation, verification, and claim-ledger generation.
- `evaluation/contract_gated/run_contract_gated_eval.py`: paired evaluation runner for authorized question/context files.
- `evaluation/contract_gated/process_contract_gated_outputs.py`: conversion from generated answers to blinded review materials and analysis-ready outputs.
- `extraction/quote_first_extractor.py`: quote-first evidence-span anchoring for graph-candidate extraction.

Before public upload, inspect `.env`, notebooks, cache files, and any local logs to ensure no API keys or personal data are present.

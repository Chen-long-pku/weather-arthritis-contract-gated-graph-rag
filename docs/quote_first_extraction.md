# Quote-first evidence-span anchored extraction

The quote-first extraction workflow is used as a supplementary quality-control method for graph-candidate extraction. It is designed to make each candidate relation traceable to an exact source sentence before any candidate is considered for graph insertion.

## Core workflow

1. Split each abstract into source sentences.
2. Select candidate evidence sentences.
3. Apply the study contract before graph insertion:
   - keep environmental weather/climate exposure;
   - withhold therapeutic heat/cold interventions;
   - withhold traditional medicine syndrome labels unless explicitly tied to meteorological exposure;
   - withhold non-weather or title-only relationships.
4. Emit a graph candidate only when the evidence sentence is an exact substring of the abstract.
5. Treat the output as a candidate for expert-auditable curation, not as an automatically accepted medical fact.

## Files

- `extraction/quote_first_extractor.py`: deterministic quote-first gate.
- `extraction/prompt_templates.py`: optional LLM quote-first prompt.
- `extraction/deepseek_extractor.py`: optional DeepSeek quote-first extraction method with deterministic quote post-validation.
- `evaluation/quote_first_extraction/run_quote_first_extraction_audit.py`: replay script for the extraction quality-control workflow.

## Interpretation

The quote-first workflow prioritizes precision and traceability over coverage. A lower candidate count is expected when the goal is a curated evidence graph. Candidate yield and expert-validated graph insertion should be reported separately.

AI or LLM outputs from this workflow are candidates. They should not be described as expert-reviewed graph edges unless independent human review has been completed and documented.

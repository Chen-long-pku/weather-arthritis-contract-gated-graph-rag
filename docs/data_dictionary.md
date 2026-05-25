# Data Dictionary

## Study Node

| Field | Description |
|---|---|
| `pmid` | PubMed identifier |
| `title` | Article title |
| `publication_date` | Publication date when available |

## ChronicDisease Node

Represents common chronic disease categories in the expanded platform, such as cardiovascular disease, hypertension, heart failure, COPD, asthma, diabetes, chronic kidney disease, chronic mental-health conditions, chronic pain, arthritis, and multimorbidity.

## ArthritisType Node

Represents arthritis or rheumatic disease entities extracted from the preliminary expert-adjudicated feasibility literature, such as osteoarthritis, rheumatoid arthritis, gout, psoriatic arthritis, and ankylosing spondylitis.

## ClimateFactor Node

Represents weather, climate, meteorological, or environmental exposures, such as temperature, humidity, barometric pressure, precipitation, cold exposure, air pollution, and seasonality.

## Symptom Node

Represents symptoms, outcomes, or disease-burden terms, such as pain, stiffness, dyspnea, acute exacerbation, hospitalization, blood-pressure instability, glycemic instability, renal stress, disability, and outpatient visits.

## Relationship Labels

| Label | Meaning |
|---|---|
| `CORRELATES_WITH` | Non-directional association |
| `INCREASES` | Positive directional relationship in the source evidence |
| `DECREASES` | Negative directional relationship in the source evidence |
| `NO_EFFECT` | No significant relationship reported |
| `AFFECTS` | Broad influence relationship |
| `EXACERBATES` | Worsening or aggravating relationship |
| `AMELIORATES` | Improvement or alleviation relationship |
| `STUDIED_IN` | Entity mentioned or studied in a literature source |

## Evidence Graph Governance Fields

Entity-level fields:

| Field | Description |
|---|---|
| `entity_id` | Deterministic identifier in the form `{EntityType}:{canonical_slug}` |
| `canonical_name` | Lower-case normalized entity name for deduplication and search |
| `type` | Controlled entity type used by the graph schema |
| `study_count` | Number of distinct studies linked through `STUDIED_IN` |
| `degree` | Number of graph relationships involving the entity |

Relationship-level fields:

| Field | Description |
|---|---|
| `support_count` | Number of distinct PMIDs supporting the direct relationship edge |
| `pmids` | PMID list supporting the relationship |
| `confidence_score` | Numeric confidence derived from extracted confidence and evidence length |
| `evidence_tier` | `high`, `moderate`, or `low` |
| `latest_evidence` | Most recent evidence snippet retained on the direct edge |

Evidence assertion fields:

| Field | Description |
|---|---|
| `assertion_id` | Stable relationship-level assertion identifier |
| `head_name`, `relation_type`, `tail_name` | Extracted triple |
| `evidence` | Source evidence snippet |
| `key_finding` | Article-level extracted finding when available |
| `source`, `model` | Extraction source and model metadata |

## Evidence Triage Module

The demo backend and role-specific interfaces expose a role-facing evidence triage layer.

| Field | Description |
|---|---|
| `module` | Triage module name, such as heat-cardio-renal-metabolic or weather-pain-rheumatology feasibility case |
| `exposure` | Climate, meteorological, pollution, or disruption exposure represented by the module |
| `disease_domain` | Chronic disease categories covered by the module |
| `evidence_grade` | Translation label used to separate literature-based scaffolds, plausible scaffolds, expert-adjudicated feasibility evidence, and emerging signals |
| `validation_status` | Whether the module is preliminary expert-adjudicated, ontology-supported pending validation, or hypothesis-generating |
| `clinical_translation` | Clinician-facing communication or follow-up use that stays outside diagnosis and treatment adjustment |
| `research_readiness` | Practical readiness for follow-up epidemiologic or implementation research |
| `next_study` | Suggested follow-up study design derived from the graph module |

## Claim Evidence Ledger

Each Graph-RAG answer can also return a claim-level evidence ledger.

| Field | Description |
|---|---|
| `claim_type` | Scope, triage module, literature trace, abstention/block, or role-specific use-boundary claim |
| `claim_text` | Short claim that should travel with the generated answer |
| `evidence_source` | Boundary gate, evidence triage layer, retrieved Study nodes, or role-specific policy |
| `support_status` | Whether the claim is rule-assigned, PMID-traceable, scaffold-based, or safety-triggered |
| `pmids` | PMID list attached to the retrieved answer context when available |
| `boundary_status` | Whether the claim is bounded, blocked, citation-trace only, or education-only |
| `reviewer_note` | Human-readable interpretation note for auditing |

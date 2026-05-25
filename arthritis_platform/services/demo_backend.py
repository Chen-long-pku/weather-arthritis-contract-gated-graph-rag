"""
Deterministic demo backend for reviewer-facing and client-facing runs.

The live platform uses Neo4j plus an external LLM. For manuscript review,
teaching, client discussions, or screenshots, this module provides a small
in-memory backend with the same public methods used by the Streamlit apps. It
keeps the interface usable even when credentials or a local graph database are
not available.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List

from .evidence_boundary import EvidenceBoundaryGate


DEMO_ENTITIES = [
    {"name": "temperature", "type": "ClimateFactor", "study_count": 312, "relation_count": 88},
    {"name": "humidity", "type": "ClimateFactor", "study_count": 181, "relation_count": 57},
    {"name": "barometric pressure", "type": "ClimateFactor", "study_count": 96, "relation_count": 31},
    {"name": "seasonal variation", "type": "ClimateFactor", "study_count": 221, "relation_count": 64},
    {"name": "cold exposure", "type": "ClimateFactor", "study_count": 72, "relation_count": 24},
    {"name": "heat wave", "type": "ClimateFactor", "study_count": 138, "relation_count": 51},
    {"name": "extreme heat", "type": "ClimateFactor", "study_count": 164, "relation_count": 62},
    {"name": "air pollution", "type": "ClimateFactor", "study_count": 229, "relation_count": 82},
    {"name": "wildfire smoke", "type": "ClimateFactor", "study_count": 58, "relation_count": 18},
    {"name": "flooding", "type": "ClimateFactor", "study_count": 41, "relation_count": 13},
    {"name": "climate change", "type": "ClimateFactor", "study_count": 216, "relation_count": 75},
    {"name": "temperature variability", "type": "ClimateFactor", "study_count": 146, "relation_count": 46},
    {"name": "cardiovascular disease", "type": "ChronicDisease", "study_count": 352, "relation_count": 96},
    {"name": "hypertension", "type": "ChronicDisease", "study_count": 188, "relation_count": 54},
    {"name": "ischemic heart disease", "type": "ChronicDisease", "study_count": 141, "relation_count": 42},
    {"name": "heart failure", "type": "ChronicDisease", "study_count": 126, "relation_count": 39},
    {"name": "chronic obstructive pulmonary disease", "type": "ChronicDisease", "study_count": 213, "relation_count": 68},
    {"name": "asthma", "type": "ChronicDisease", "study_count": 237, "relation_count": 71},
    {"name": "diabetes", "type": "ChronicDisease", "study_count": 169, "relation_count": 48},
    {"name": "chronic kidney disease", "type": "ChronicDisease", "study_count": 94, "relation_count": 28},
    {"name": "chronic mental health conditions", "type": "ChronicDisease", "study_count": 82, "relation_count": 25},
    {"name": "osteoarthritis", "type": "ChronicDisease", "study_count": 336, "relation_count": 96},
    {"name": "rheumatoid arthritis", "type": "ChronicDisease", "study_count": 284, "relation_count": 81},
    {"name": "gout", "type": "ChronicDisease", "study_count": 103, "relation_count": 34},
    {"name": "multimorbidity", "type": "ChronicDisease", "study_count": 111, "relation_count": 37},
    {"name": "joint pain", "type": "Symptom", "study_count": 298, "relation_count": 92},
    {"name": "stiffness", "type": "Symptom", "study_count": 149, "relation_count": 49},
    {"name": "exacerbation", "type": "Symptom", "study_count": 244, "relation_count": 76},
    {"name": "hospital admission", "type": "Symptom", "study_count": 268, "relation_count": 83},
    {"name": "dyspnea", "type": "Symptom", "study_count": 171, "relation_count": 53},
    {"name": "blood pressure instability", "type": "Symptom", "study_count": 104, "relation_count": 31},
    {"name": "glycemic instability", "type": "Symptom", "study_count": 66, "relation_count": 20},
    {"name": "renal stress", "type": "Symptom", "study_count": 59, "relation_count": 17},
    {"name": "medication safety", "type": "Symptom", "study_count": 52, "relation_count": 16},
    {"name": "functional limitation", "type": "Symptom", "study_count": 74, "relation_count": 22},
    {"name": "mental distress", "type": "Symptom", "study_count": 69, "relation_count": 19},
]

DEMO_RELATIONS = [
    {"source": "temperature", "relation": "ASSOCIATED_WITH", "target": "joint pain", "support_count": 92},
    {"source": "temperature", "relation": "ASSOCIATED_WITH", "target": "osteoarthritis", "support_count": 71},
    {"source": "humidity", "relation": "ASSOCIATED_WITH", "target": "stiffness", "support_count": 48},
    {"source": "barometric pressure", "relation": "MAY_TRIGGER", "target": "joint pain", "support_count": 31},
    {"source": "cold exposure", "relation": "WORSENS", "target": "osteoarthritis", "support_count": 26},
    {"source": "seasonal variation", "relation": "MODULATES", "target": "rheumatoid arthritis", "support_count": 44},
    {"source": "heat wave", "relation": "ASSOCIATED_WITH", "target": "cardiovascular disease", "support_count": 86},
    {"source": "heat wave", "relation": "ASSOCIATED_WITH", "target": "hospital admission", "support_count": 74},
    {"source": "extreme heat", "relation": "WORSENS", "target": "heart failure", "support_count": 42},
    {"source": "extreme heat", "relation": "WORSENS", "target": "diabetes", "support_count": 37},
    {"source": "extreme heat", "relation": "WORSENS", "target": "chronic kidney disease", "support_count": 24},
    {"source": "air pollution", "relation": "ASSOCIATED_WITH", "target": "chronic obstructive pulmonary disease", "support_count": 91},
    {"source": "air pollution", "relation": "ASSOCIATED_WITH", "target": "asthma", "support_count": 88},
    {"source": "air pollution", "relation": "ASSOCIATED_WITH", "target": "cardiovascular disease", "support_count": 79},
    {"source": "wildfire smoke", "relation": "MAY_TRIGGER", "target": "exacerbation", "support_count": 33},
    {"source": "wildfire smoke", "relation": "ASSOCIATED_WITH", "target": "asthma", "support_count": 29},
    {"source": "temperature variability", "relation": "ASSOCIATED_WITH", "target": "blood pressure instability", "support_count": 39},
    {"source": "temperature variability", "relation": "ASSOCIATED_WITH", "target": "heart failure", "support_count": 28},
    {"source": "cold exposure", "relation": "ASSOCIATED_WITH", "target": "hypertension", "support_count": 35},
    {"source": "cold exposure", "relation": "ASSOCIATED_WITH", "target": "ischemic heart disease", "support_count": 32},
    {"source": "humidity", "relation": "MODULATES", "target": "dyspnea", "support_count": 27},
    {"source": "humidity", "relation": "ASSOCIATED_WITH", "target": "chronic obstructive pulmonary disease", "support_count": 31},
    {"source": "flooding", "relation": "DISRUPTS", "target": "medication safety", "support_count": 14},
    {"source": "climate change", "relation": "CONTEXTUALIZES", "target": "multimorbidity", "support_count": 43},
    {"source": "climate change", "relation": "CONTEXTUALIZES", "target": "chronic mental health conditions", "support_count": 23},
    {"source": "heat wave", "relation": "MAY_TRIGGER", "target": "renal stress", "support_count": 21},
    {"source": "extreme heat", "relation": "ASSOCIATED_WITH", "target": "glycemic instability", "support_count": 19},
    {"source": "multimorbidity", "relation": "CO_OCCURS_WITH", "target": "functional limitation", "support_count": 36},
    {"source": "gout", "relation": "ASSOCIATED_WITH", "target": "seasonal variation", "support_count": 27},
    {"source": "rheumatoid arthritis", "relation": "CO_OCCURS_WITH", "target": "joint pain", "support_count": 62},
]

DEMO_STUDIES = [
    {"pmid": "16700001", "title": "Seasonal weather variation and patient-reported joint symptoms", "year": 2006},
    {"pmid": "17400002", "title": "Ambient temperature, cardiovascular admissions, and chronic disease vulnerability", "year": 2007},
    {"pmid": "18100003", "title": "Humidity, pressure, and chronic musculoskeletal pain", "year": 2008},
    {"pmid": "19500004", "title": "Cold spells, blood pressure variation, and ischemic heart disease", "year": 2009},
    {"pmid": "20400005", "title": "Seasonality of gout attacks in population-based records", "year": 2010},
    {"pmid": "21400006", "title": "Barometric pressure changes and joint pain diary data", "year": 2011},
    {"pmid": "22600007", "title": "Meteorological exposures and rheumatoid arthritis activity", "year": 2012},
    {"pmid": "23800008", "title": "Heat exposure and chronic kidney disease service risk", "year": 2013},
    {"pmid": "24700009", "title": "Weather sensitivity and osteoarthritis pain across European cohorts", "year": 2014},
    {"pmid": "25800010", "title": "Temperature variability and blood pressure instability", "year": 2015},
    {"pmid": "26900011", "title": "Humidity and stiffness in inflammatory joint disease", "year": 2016},
    {"pmid": "28100012", "title": "Air pollution, climate context, and chronic respiratory outcomes", "year": 2017},
    {"pmid": "29400013", "title": "Heat exposure and chronic disease symptom vulnerability", "year": 2018},
    {"pmid": "31813510", "title": "Weather sensitivity and daily pain variation in people with osteoarthritis", "year": 2019},
    {"pmid": "33141022", "title": "Meteorological factors and musculoskeletal pain: evidence from longitudinal symptom tracking", "year": 2020},
    {"pmid": "34578112", "title": "Seasonality, humidity, and symptom burden in inflammatory arthritis", "year": 2021},
    {"pmid": "36187204", "title": "Digital evidence translation for climate-sensitive chronic disease management", "year": 2022},
    {"pmid": "37591084", "title": "Knowledge graph retrieval for transparent biomedical question answering", "year": 2023},
    {"pmid": "38900019", "title": "Graph-based retrieval for climate-sensitive chronic disease literature", "year": 2024},
    {"pmid": "39700020", "title": "Living evidence systems for climate and common chronic disease", "year": 2025},
    {"pmid": "40100021", "title": "Scheduled incremental surveillance of climate-sensitive chronic disease evidence graphs", "year": 2026},
]

DEMO_PUBMED_SCOPE = {
    "source": "PubMed",
    "publication_window_start": "2006/01/01",
    "publication_window_end": "2026/05/07",
    "window_label": "near-20-year arthritis feasibility window with embedded chronic-disease extension",
    "queried_pubmed_records": 1992,
    "previous_2015_window_records": 1339,
    "additional_candidate_records": 653,
    "queried_at": "2026-05-07",
}

DEMO_EVIDENCE_TRIAGE = [
    {
        "module": "Heat-cardio-renal-metabolic",
        "exposure": "heat wave / extreme heat",
        "disease_domain": "cardiovascular disease; heart failure; diabetes; chronic kidney disease",
        "evidence_grade": "Literature-based scaffold: external evidence; no in-study validation",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use for risk communication about hydration, medication safety, blood pressure/glucose monitoring, kidney stress, and follow-up thresholds.",
        "research_readiness": "High",
        "next_study": "Time-stratified case-crossover or DLNM using emergency, outpatient, or claims records.",
    },
    {
        "module": "Pollution-respiratory-cardiovascular",
        "exposure": "air pollution / wildfire smoke",
        "disease_domain": "COPD; asthma; cardiovascular disease",
        "evidence_grade": "Literature-based scaffold: external evidence; no in-study validation",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use for action-plan checks, inhaler adherence review, exacerbation recognition, and follow-up planning during smog or smoke events.",
        "research_readiness": "High",
        "next_study": "Multi-pollutant time-series or case-crossover analysis with weather interaction terms.",
    },
    {
        "module": "Cold-blood pressure-ischemic risk",
        "exposure": "cold exposure / temperature variability",
        "disease_domain": "hypertension; ischemic heart disease; heart failure",
        "evidence_grade": "Plausible scaffold: clinically important but no in-study validation",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use to organize blood-pressure logs, medication adherence checks, chest-pain triage, and warnings not to delay acute evaluation.",
        "research_readiness": "Moderate-high",
        "next_study": "Self-controlled case series or DLNM linking cold spells with blood pressure and visit records.",
    },
    {
        "module": "Weather-pain-rheumatology feasibility case",
        "exposure": "temperature; humidity; barometric pressure; seasonal variation",
        "disease_domain": "osteoarthritis; rheumatoid arthritis; gout; chronic pain",
        "evidence_grade": "Expert-adjudicated feasibility evidence: heterogeneous weather-pain signal",
        "validation_status": "Empirical extraction and preliminary dual-expert adjudication completed",
        "clinical_translation": "Use symptom diaries and standard disease assessment; do not treat weather sensitivity as diagnosis or disease activity.",
        "research_readiness": "High for feasibility extension",
        "next_study": "Repeated symptom diary study with local meteorology and within-person controls.",
    },
    {
        "module": "Extreme events-medication access",
        "exposure": "flooding / disrupted services / climate change",
        "disease_domain": "multimorbidity; chronic mental health conditions; medication safety",
        "evidence_grade": "Hypothesis-generating scaffold: service-continuity signal",
        "validation_status": "Ontology-supported extension; disease-specific extraction and expert validation pending",
        "clinical_translation": "Use for preparedness counseling, medication continuity planning, and vulnerability screening in chronic disease follow-up.",
        "research_readiness": "Moderate",
        "next_study": "Mixed-methods or interrupted time-series study of service disruption and medication continuity.",
    },
]


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


class DemoGraphQueryService:
    """In-memory graph query service used when live infrastructure is absent."""

    database = "demo-chronic-disease-graph"

    def close(self) -> None:
        return None

    def execute_query(self, cypher: str, parameters: Dict | None = None) -> List[Dict]:
        return self.execute_read_query(cypher, parameters)

    def execute_read_query(self, cypher: str, parameters: Dict | None = None) -> List[Dict]:
        lowered = cypher.lower()
        if "type(r)" in lowered or "relationship" in lowered:
            return self.get_statistics()["relations"]
        if "study" in lowered or "pmid" in lowered:
            return DEMO_STUDIES
        if "degree" in lowered:
            return [
                {"entity": item["name"], "type": item["type"], "degree": item["relation_count"]}
                for item in sorted(DEMO_ENTITIES, key=lambda x: x["relation_count"], reverse=True)[:10]
            ]
        return self.get_statistics()["nodes"]

    def search_entity(self, entity_name: str, entity_type: str | None = None) -> List[Dict]:
        query = (entity_name or "").strip().lower()
        matches = []
        for entity in DEMO_ENTITIES:
            if entity_type and entity["type"] != entity_type:
                continue
            if not query or query in entity["name"].lower() or _contains_any(query, entity["name"].split()):
                matches.append(entity)
        return sorted(matches, key=lambda item: item["study_count"], reverse=True)[:10]

    def get_entity_details(self, entity_name: str) -> Dict | None:
        results = self.search_entity(entity_name)
        return results[0] if results else None

    def get_entity_relations(self, entity_name: str, direction: str = "both") -> List[Dict]:
        lowered = entity_name.lower()
        rows = []
        for relation in DEMO_RELATIONS:
            if lowered in relation["source"].lower() or lowered in relation["target"].lower():
                rows.append(
                    {
                        "entity1": relation["source"],
                        "relation": relation["relation"],
                        "entity2": relation["target"],
                        "type1": self._entity_type(relation["source"]),
                        "type2": self._entity_type(relation["target"]),
                        "support_count": relation["support_count"],
                    }
                )
        return rows[:20]

    def find_relation(self, entity1: str, entity2: str) -> List[Dict]:
        left = entity1.lower()
        right = entity2.lower()
        return [
            relation
            for relation in DEMO_RELATIONS
            if {relation["source"].lower(), relation["target"].lower()} == {left, right}
        ]

    def find_shortest_path(self, entity1: str, entity2: str, max_length: int = 3) -> List[Dict]:
        direct = self.find_relation(entity1, entity2)
        if direct:
            relation = direct[0]
            return [{"path": [relation["source"], relation["target"]], "relations": [relation["relation"]], "length": 1}]
        return [
            {
                "path": [entity1, "chronic disease burden", entity2],
                "relations": ["ASSOCIATED_WITH", "CONTEXTUALIZES"],
                "length": 2,
            }
        ]

    def get_entity_studies(self, entity_name: str) -> List[Dict]:
        lowered = entity_name.lower()
        if "temperature" in lowered or "osteoarthritis" in lowered or "joint" in lowered:
            return [DEMO_STUDIES[0], DEMO_STUDIES[8], DEMO_STUDIES[13]]
        if "humidity" in lowered or "rheumatoid" in lowered or "stiffness" in lowered:
            return [DEMO_STUDIES[2], DEMO_STUDIES[10], DEMO_STUDIES[15]]
        if "heat" in lowered or "kidney" in lowered or "diabetes" in lowered or "heart failure" in lowered:
            return [DEMO_STUDIES[7], DEMO_STUDIES[12], DEMO_STUDIES[16]]
        if "air pollution" in lowered or "asthma" in lowered or "pulmonary" in lowered or "copd" in lowered:
            return [DEMO_STUDIES[11], DEMO_STUDIES[16], DEMO_STUDIES[18]]
        if "cold" in lowered or "hypertension" in lowered or "ischemic" in lowered:
            return [DEMO_STUDIES[3], DEMO_STUDIES[9], DEMO_STUDIES[12]]
        return DEMO_STUDIES[:3]

    def get_relation_studies(self, entity1: str, entity2: str) -> List[Dict]:
        return self.get_entity_studies(f"{entity1} {entity2}")[:3]

    def get_statistics(self) -> Dict:
        node_counts = Counter(entity["type"] for entity in DEMO_ENTITIES)
        relation_counts = Counter(relation["relation"] for relation in DEMO_RELATIONS)
        return {
            "nodes": [{"type": key, "count": value} for key, value in node_counts.items()],
            "relations": [{"type": key, "count": value} for key, value in relation_counts.items()],
        }

    def get_top_entities(self, entity_type: str, limit: int = 10) -> List[Dict]:
        items = [
            {"name": entity["name"], "study_count": entity["study_count"]}
            for entity in DEMO_ENTITIES
            if entity["type"] == entity_type
        ]
        return sorted(items, key=lambda item: item["study_count"], reverse=True)[:limit]

    def get_relation_distribution(self, entity_name: str) -> List[Dict]:
        counts = Counter(row["relation"] for row in self.get_entity_relations(entity_name))
        return [{"relation_type": key, "count": value} for key, value in counts.items()]

    def find_research_gaps(self, entity_type: str = "ClimateFactor") -> List[Dict]:
        items = [
            {"name": entity["name"], "study_count": entity["study_count"]}
            for entity in DEMO_ENTITIES
            if entity["type"] == entity_type and entity["study_count"] < 25
        ]
        return sorted(items, key=lambda item: item["study_count"])[:20]

    def find_co_occurrence(self, entity1: str, min_studies: int = 2) -> List[Dict]:
        lowered = entity1.lower()
        related = []
        for relation in DEMO_RELATIONS:
            if lowered in relation["source"].lower():
                related.append(
                    {
                        "entity": relation["target"],
                        "type": self._entity_type(relation["target"]),
                        "共同研究数": max(relation["support_count"], min_studies),
                    }
                )
            elif lowered in relation["target"].lower():
                related.append(
                    {
                        "entity": relation["source"],
                        "type": self._entity_type(relation["source"]),
                        "共同研究数": max(relation["support_count"], min_studies),
                    }
                )
        return related[:15]

    def get_subgraph(self, entity_name: str, depth: int = 2) -> Dict:
        rows = self.get_entity_relations(entity_name)
        node_names = {entity_name}
        relationships = []
        for row in rows:
            node_names.add(row["entity1"])
            node_names.add(row["entity2"])
            relationships.append({"source": row["entity1"], "target": row["entity2"], "type": row["relation"]})
        return {
            "nodes": [{"name": name, "type": self._entity_type(name)} for name in sorted(node_names)],
            "relationships": relationships,
        }

    def get_schema_overview(self) -> Dict:
        node_counts = Counter(entity["type"] for entity in DEMO_ENTITIES)
        relation_counts = Counter(relation["relation"] for relation in DEMO_RELATIONS)
        return {
            "nodes": [
                {
                    "type": entity_type,
                    "count": count,
                    "mean_study_count": round(
                        sum(e["study_count"] for e in DEMO_ENTITIES if e["type"] == entity_type) / count,
                        2,
                    ),
                }
                for entity_type, count in node_counts.items()
            ],
            "relationships": [
                {
                    "relation_type": relation_type,
                    "edge_count": count,
                    "support_count": sum(
                        relation["support_count"] for relation in DEMO_RELATIONS if relation["relation"] == relation_type
                    ),
                }
                for relation_type, count in relation_counts.items()
            ],
        }

    def get_quality_snapshot(self) -> Dict:
        return {
            "provenance": {
                "assertions": len(DEMO_RELATIONS),
                "assertions_with_study": len(DEMO_RELATIONS),
                "supporting_studies": len(DEMO_STUDIES),
            },
            "entity_quality": {
                "entities": len(DEMO_ENTITIES),
                "missing_ids": 0,
            },
            "relationship_quality": {
                "evidence_edges": len(DEMO_RELATIONS),
                "missing_pmids": 0,
                "mean_support_count": round(
                    sum(relation["support_count"] for relation in DEMO_RELATIONS) / len(DEMO_RELATIONS),
                    2,
                ),
            },
        }

    def get_temporal_coverage(self) -> Dict:
        """Return near-20-year publication coverage for the demo KG."""
        years = [int(study["year"]) for study in DEMO_STUDIES if study.get("year")]
        year_counts = Counter(years)
        start_year = min(years)
        end_year = max(years)
        annual_counts = [
            {"year": year, "records": year_counts.get(year, 0)}
            for year in range(start_year, end_year + 1)
        ]
        return {
            **DEMO_PUBMED_SCOPE,
            "start_year": start_year,
            "end_year": end_year,
            "covered_years": end_year - start_year + 1,
            "demo_study_nodes": len(DEMO_STUDIES),
            "annual_counts": annual_counts,
            "earliest_demo_study": min(DEMO_STUDIES, key=lambda study: study["year"]),
            "latest_demo_study": max(DEMO_STUDIES, key=lambda study: study["year"]),
        }

    def get_evidence_triage(self) -> List[Dict]:
        """Return clinically bounded evidence triage modules for the demo platform."""
        return [dict(row) for row in DEMO_EVIDENCE_TRIAGE]

    def get_research_readiness(self) -> List[Dict]:
        """Return research-readiness rows derived from the evidence triage layer."""
        return [
            {
                "module": row["module"],
                "readiness": row["research_readiness"],
                "validation_status": row["validation_status"],
                "follow_up_design": row["next_study"],
                "evidence_scope": (
                    "Preliminary expert-adjudicated feasibility result"
                    if "adjudication" in row["validation_status"].lower()
                    else "Expansion module requiring disease-specific extraction"
                ),
            }
            for row in DEMO_EVIDENCE_TRIAGE
        ]

    def get_clinical_translation_modules(self) -> List[Dict]:
        """Return clinician-facing actions separated from causal interpretation."""
        return [
            {
                "scenario": row["module"],
                "exposure": row["exposure"],
                "disease_domain": row["disease_domain"],
                "clinical_action": row["clinical_translation"],
                "boundary": "Evidence translation only; not diagnosis, prediction, or medication adjustment.",
            }
            for row in DEMO_EVIDENCE_TRIAGE
        ]

    def get_safety_boundary_benchmark(self) -> Dict:
        """Return deterministic scope-gate benchmark metrics and rows."""
        return EvidenceBoundaryGate().run_safety_benchmark()

    @staticmethod
    def _entity_type(name: str) -> str:
        for entity in DEMO_ENTITIES:
            if entity["name"].lower() == name.lower():
                return entity["type"]
        return "Concept"


class DemoLLMService:
    """Deterministic answer generator with the same interface as LLMService."""

    model_name = "deterministic-chronic-disease-demo"

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096) -> str:
        user_content = messages[-1]["content"] if messages else ""
        if "User question:" in user_content:
            question = user_content.split("User question:")[-1].strip()
        elif "用户问题：" in user_content:
            question = user_content.split("用户问题：")[-1].strip()
        else:
            question = user_content
        system = messages[0]["content"] if messages else ""

        if "health professionals" in system or "clinical" in system or "医务工作者" in system or "临床辅助" in system:
            return (
                "Demo-mode clinical evidence triage: the retrieved graph context separates externally "
                "supported scaffolds from the empirically extracted and expert-adjudicated arthritis/weather-pain "
                "feasibility case. Broader heat, pollution, cold, and extreme-event modules are communication and "
                "documentation scaffolds until disease-specific extraction and validation are completed.\n\n"
                "Clinical use:\n"
                "1. Treat exposure as a contextual risk modifier, not an individualized diagnosis or prescription trigger.\n"
                "2. For heat waves, review hydration, medication safety, blood pressure/glucose monitoring, kidney/cardiovascular risk, and follow-up thresholds.\n"
                "3. For pollution or smoke episodes, review respiratory action plans, inhaler adherence, symptom escalation, and urgent-care boundaries.\n"
                "4. For weather-sensitive pain, use symptom diaries alongside standard disease activity and function assessment.\n\n"
                "Example evidence traces: PMID 29400013, 36187204, 38900019."
            )

        if "research exploration" in system or "researcher" in system or "研究人员" in system or "科研探索" in system:
            return (
                "Demo-mode research answer: this question can be framed as a clinically bounded evidence triage "
                "problem linking climate stressors, chronic disease domains, outcomes, provenance, evidence "
                "grade, validation status, claim-level evidence ledger, and research readiness. The preliminary expert-adjudicated "
                "arthritis/weather-pain feasibility corpus remains the empirical case; the broader chronic-disease layer is an ontology and service "
                "extension that should be extracted and expert-validated disease by disease.\n\n"
                "Research value: the platform converts a literature corpus into a Graph-RAG evidence "
                "infrastructure and adds a scope-aware boundary gate plus claim-level evidence ledger that distinguishes expert-adjudicated examples, "
                "external-literature scaffolds, out-of-scope questions, and answer claims requiring visible evidence status. Its contribution is provenance, "
                "role-specific retrieval, safety-gated interpretation, claim accountability, and research-readiness classification "
                "rather than causal effect estimation."
            )

        return (
            "Demo-mode public answer: weather and climate events may matter for people living with chronic "
            "diseases, but the meaning depends on the condition. Heat can increase risk for dehydration, "
            "cardiovascular stress, kidney stress, or blood-sugar instability; air pollution can aggravate "
            "asthma or COPD symptoms; cold may affect blood pressure or pain. This page is for education and "
            "symptom organization. Seek medical advice for chest tightness, severe breathlessness, fainting, "
            "confusion, persistent swelling, fever, or rapidly worsening symptoms."
        )

    def generate_stream(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 4096):
        answer = self.generate(messages, temperature=temperature, max_tokens=max_tokens)
        for token in answer.split():
            yield token + " "

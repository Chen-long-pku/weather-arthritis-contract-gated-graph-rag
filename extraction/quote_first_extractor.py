"""
Quote-first, evidence-span-anchored extraction for weather-sensitive arthritis.

This module is intentionally conservative. It does not try to turn an entire
abstract into a graph edge in one model call. Instead it first selects an exact
sentence from the source text, checks whether that sentence falls within the
declared study contract, and only then emits a candidate relation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


WEATHER_TERMS = {
    "temperature": ["temperature", "ambient temperature", "hot", "heat", "cold", "cool", "warm"],
    "humidity": ["humidity", "relative humidity", "humid"],
    "pressure": ["barometric pressure", "atmospheric pressure", "air pressure", "pressure"],
    "precipitation": ["rain", "rainfall", "precipitation", "snow"],
    "season": ["season", "seasonal", "winter", "summer", "spring", "autumn", "fall"],
    "weather": ["weather", "meteorological", "climate", "climatic"],
}

ARTHRITIS_TERMS = [
    "arthritis",
    "osteoarthritis",
    "rheumatoid arthritis",
    "gout",
    "gouty arthritis",
    "psoriatic arthritis",
    "inflammatory arthritis",
    "rheumatic",
    "rheumatologic",
]

SYMPTOM_OUTCOME_TERMS = [
    "pain",
    "joint pain",
    "flare",
    "stiffness",
    "swelling",
    "disease activity",
    "hospital admission",
    "emergency",
    "consultation",
    "visit",
    "prevalence",
    "incidence",
]

THERAPEUTIC_COLD_HEAT_TERMS = [
    "cryotherapy",
    "whole-body cryotherapy",
    "heat therapy",
    "thermal therapy",
    "thermal treatment",
    "far-infrared",
    "infrared",
    "cold therapy",
    "hot pack",
    "cold pack",
]

TCM_SYNDROME_TERMS = [
    "cold-dampness",
    "dampness-heat",
    "wind-cold",
    "wind-dampness",
    "cold dampness",
    "damp heat",
]

RELATION_PATTERNS: Sequence[Tuple[str, str]] = [
    ("no_effect", r"\b(no|not|without)\s+(significant\s+)?(association|correlation|effect|relationship)\b"),
    ("increases", r"\b(increase[sd]?|higher|elevated|raise[sd]?|greater|risk factor|positively associated)\b"),
    ("decreases", r"\b(decrease[sd]?|lower|reduced|protective|negatively associated|inverse association)\b"),
    ("correlates_with", r"\b(associated|association|correlat(?:e|ed|ion)|related|linked)\b"),
]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def find_terms(text: str, terms: Iterable[str]) -> List[str]:
    lower = text.lower()
    hits = []
    for term in terms:
        if re.search(r"\b" + re.escape(term.lower()) + r"\b", lower):
            hits.append(term)
    return hits


def find_weather_terms(text: str) -> List[str]:
    hits: List[str] = []
    for canonical, variants in WEATHER_TERMS.items():
        if find_terms(text, variants):
            hits.append(canonical)
    return sorted(set(hits))


def split_sentences(text: str) -> List[Tuple[str, int, int]]:
    """Return sentence, start, end triples using conservative punctuation rules."""
    clean = normalize_space(text)
    if not clean:
        return []
    spans: List[Tuple[str, int, int]] = []
    start = 0
    for match in re.finditer(r"(?<=[.!?])\s+(?=[A-Z0-9])", clean):
        end = match.start()
        sent = clean[start:end].strip()
        if sent:
            spans.append((sent, start, end))
        start = match.end()
    tail = clean[start:].strip()
    if tail:
        spans.append((tail, start, len(clean)))
    return spans


def classify_relation(sentence: str) -> str:
    lower = sentence.lower()
    for label, pattern in RELATION_PATTERNS:
        if re.search(pattern, lower):
            return label
    return "mentions"


@dataclass
class EvidenceSentence:
    sentence: str
    start_char: int
    end_char: int
    weather_terms: List[str]
    arthritis_terms: List[str]
    symptom_outcome_terms: List[str]
    therapeutic_terms: List[str]
    tcm_terms: List[str]
    relation_type: str
    scope_status: str
    scope_reason: str
    evidence_quote_exact_match: bool


@dataclass
class QuoteFirstExtraction:
    pmid: str
    title: str
    abstract: str
    evidence_sentences: List[Dict]
    selected_relationships: List[Dict]
    content_graph_candidate_count: int
    strict_evidence_trace_candidate_count: int
    extraction_mode: str = "quote_first_evidence_span_anchored"


class QuoteFirstEvidenceExtractor:
    """A deterministic gate that can run before or after an LLM relation step."""

    def classify_sentence(self, sentence: str, start: int, end: int, abstract: str) -> EvidenceSentence:
        weather = find_weather_terms(sentence)
        arthritis = find_terms(sentence, ARTHRITIS_TERMS)
        symptoms = find_terms(sentence, SYMPTOM_OUTCOME_TERMS)
        therapeutic = find_terms(sentence, THERAPEUTIC_COLD_HEAT_TERMS)
        tcm = find_terms(sentence, TCM_SYNDROME_TERMS)
        relation_type = classify_relation(sentence)

        if therapeutic and not weather:
            scope_status = "out_of_scope"
            reason = "Therapeutic cold/heat intervention without environmental weather exposure."
        elif tcm and not weather:
            scope_status = "out_of_scope"
            reason = "Traditional medicine syndrome label without meteorological exposure."
        elif weather and (arthritis or symptoms):
            scope_status = "in_scope"
            reason = "Environmental weather/climate term co-occurs with arthritis or arthritis-relevant symptom/outcome."
        elif weather:
            scope_status = "borderline"
            reason = "Weather/climate term is present but arthritis-specific target is unclear."
        else:
            scope_status = "out_of_scope"
            reason = "No environmental weather/climate exposure in the evidence sentence."

        return EvidenceSentence(
            sentence=sentence,
            start_char=start,
            end_char=end,
            weather_terms=weather,
            arthritis_terms=arthritis,
            symptom_outcome_terms=symptoms,
            therapeutic_terms=therapeutic,
            tcm_terms=tcm,
            relation_type=relation_type,
            scope_status=scope_status,
            scope_reason=reason,
            evidence_quote_exact_match=sentence in normalize_space(abstract),
        )

    def extract(self, pmid: str, title: str, abstract: str) -> QuoteFirstExtraction:
        evidence_sentences: List[EvidenceSentence] = []
        selected_relationships: List[Dict] = []
        clean_abstract = normalize_space(abstract)

        for sentence, start, end in split_sentences(clean_abstract):
            evidence = self.classify_sentence(sentence, start, end, clean_abstract)
            evidence_sentences.append(evidence)
            if evidence.scope_status != "in_scope":
                continue
            if not evidence.evidence_quote_exact_match:
                continue
            if not evidence.weather_terms:
                continue
            if not (evidence.arthritis_terms or evidence.symptom_outcome_terms):
                continue

            selected_relationships.append(
                {
                    "climate_factor": "; ".join(evidence.weather_terms),
                    "effect_on": "; ".join(evidence.arthritis_terms or evidence.symptom_outcome_terms),
                    "relationship_type": evidence.relation_type,
                    "evidence_quote": evidence.sentence,
                    "quote_start_char": evidence.start_char,
                    "quote_end_char": evidence.end_char,
                    "evidence_quote_exact_match": True,
                    "scope_status": evidence.scope_status,
                    "scope_reason": evidence.scope_reason,
                    "graph_insertion_status": "eligible_candidate",
                }
            )

        content_candidates = len(selected_relationships)
        strict_candidates = sum(1 for rel in selected_relationships if rel["evidence_quote_exact_match"])
        return QuoteFirstExtraction(
            pmid=str(pmid),
            title=title,
            abstract=clean_abstract,
            evidence_sentences=[asdict(item) for item in evidence_sentences],
            selected_relationships=selected_relationships,
            content_graph_candidate_count=content_candidates,
            strict_evidence_trace_candidate_count=strict_candidates,
        )


def extract_quote_first(pmid: str, title: str, abstract: str) -> Dict:
    """Convenience wrapper returning a JSON-serializable dict."""
    return asdict(QuoteFirstEvidenceExtractor().extract(pmid, title, abstract))

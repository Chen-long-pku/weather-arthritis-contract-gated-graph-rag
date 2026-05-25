"""Evidence contract and post-generation verification for medical Graph-RAG.

This module implements a lightweight, model-agnostic governance layer inspired
by current RAG practice: retrieve-quality checking, self-reflective support
assessment, and contract-style answer constraints. It is intentionally
deterministic so that manuscript results can be audited and reproduced.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Dict, Iterable, List


CONTRACT_VERSION = "risk-first-evidence-contract-v3.0"


PATIENT_SPECIFIC_TERMS = {
    "i ",
    "my ",
    "me ",
    "my patient",
    "this patient",
    "should i",
    "can i",
    "do i",
    "for me",
    "我",
    "我的",
    "患者",
    "病人",
    "该不该",
    "能不能",
}

MEDICATION_TERMS = {
    "methotrexate",
    "insulin",
    "nsaid",
    "nsaids",
    "ibuprofen",
    "naproxen",
    "acetaminophen",
    "paracetamol",
    "steroid",
    "prednisone",
    "dmard",
    "biologic",
    "dose",
    "dosage",
    "continue",
    "stop",
    "hold",
    "switch",
    "increase",
    "decrease",
    "medication",
    "medicine",
    "drug",
    "甲氨蝶呤",
    "胰岛素",
    "止痛药",
    "布洛芬",
    "对乙酰氨基酚",
    "激素",
    "药",
    "用药",
    "剂量",
    "停药",
    "继续用药",
    "换药",
    "加量",
    "减量",
}

DIAGNOSIS_OR_TRIAGE_TERMS = {
    "diagnose",
    "diagnosis",
    "predict my risk",
    "personal risk",
    "emergency",
    "urgent",
    "threshold",
    "go to er",
    "go to the er",
    "heart attack",
    "stroke",
    "chest pain",
    "severe breathlessness",
    "fainting",
    "诊断",
    "预测",
    "急诊",
    "急救",
    "阈值",
    "胸痛",
    "心梗",
    "中风",
    "严重气短",
    "晕厥",
}

CAUSAL_OVERCLAIM_TERMS = {
    "proves",
    "proven",
    "definitely causes",
    "will cause",
    "known to cause",
    "known to increase",
    "must be due to",
    "clearly causes",
    "证明",
    "一定会",
    "肯定",
    "明确导致",
    "必然",
}

DIRECTIVE_PATTERNS = [
    r"\byou should\b",
    r"\byou must\b",
    r"\bkeep taking\b",
    r"\bdo not stop\b",
    r"\bstop taking\b",
    r"\bcontinue taking\b",
    r"\bincrease (your )?dose\b",
    r"\bdecrease (your )?dose\b",
    r"\btake (ibuprofen|naproxen|acetaminophen|paracetamol|nsaids?)\b",
    r"你应该",
    r"你必须",
    r"不要停",
    r"继续服用",
    r"停止服用",
    r"增加剂量",
    r"减少剂量",
    r"可以吃",
]


@dataclass(frozen=True)
class EvidenceContract:
    contract_version: str
    risk_tier: str
    answer_mode: str
    evidence_sufficiency: str
    retrieval_confidence: float
    patient_specific: bool
    risk_flags: List[str]
    forbidden_actions: List[str]
    required_elements: List[str]
    allowed_content: List[str]
    repair_policy: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvidenceContractCompiler:
    """Compile a question-specific contract before answer generation."""

    def compile(
        self,
        question: str,
        role: str,
        boundary: Dict[str, Any],
        knowledge: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = f" {question.lower()} "
        patient_specific = _contains_any(text, PATIENT_SPECIFIC_TERMS)
        medication = _contains_any(text, MEDICATION_TERMS)
        diagnosis_or_triage = _contains_any(text, DIAGNOSIS_OR_TRIAGE_TERMS)
        causal_overclaim_risk = _contains_any(text, CAUSAL_OVERCLAIM_TERMS)

        retrieval_confidence = self._retrieval_confidence(knowledge)
        scope = boundary.get("scope_level", "")
        out_of_scope = "outside current graph scope" in scope
        scaffold = "scaffold" in scope

        risk_flags: List[str] = []
        if patient_specific:
            risk_flags.append("patient_specific_request")
        if medication:
            risk_flags.append("medication_boundary")
        if diagnosis_or_triage:
            risk_flags.append("diagnosis_or_urgent_triage_boundary")
        if causal_overclaim_risk:
            risk_flags.append("causal_certainty_language_requested")
        if out_of_scope:
            risk_flags.append("outside_graph_scope")
        if scaffold:
            risk_flags.append("extension_module_not_empirically_validated")
        if retrieval_confidence < 0.35:
            risk_flags.append("low_retrieval_confidence")

        risk_tier = self._risk_tier(
            patient_specific=patient_specific,
            medication=medication,
            diagnosis_or_triage=diagnosis_or_triage,
            out_of_scope=out_of_scope,
            scaffold=scaffold,
            retrieval_confidence=retrieval_confidence,
        )
        evidence_sufficiency = self._evidence_sufficiency(retrieval_confidence, out_of_scope, scaffold)
        answer_mode = self._answer_mode(risk_tier, role, out_of_scope, medication, diagnosis_or_triage)

        contract = EvidenceContract(
            contract_version=CONTRACT_VERSION,
            risk_tier=risk_tier,
            answer_mode=answer_mode,
            evidence_sufficiency=evidence_sufficiency,
            retrieval_confidence=retrieval_confidence,
            patient_specific=patient_specific,
            risk_flags=risk_flags,
            forbidden_actions=[
                "patient-specific diagnosis",
                "individualized medication start/stop/continue/switch advice",
                "dose adjustment",
                "urgent triage thresholds not present in retrieved evidence",
                "causal certainty beyond retrieved evidence",
                "self-care directives not supported by retrieved evidence",
            ],
            required_elements=self._required_elements(risk_tier, scope, scaffold, out_of_scope),
            allowed_content=self._allowed_content(role, scaffold, out_of_scope),
            repair_policy="replace_high_risk_or_contract_violating_answer_with_controlled_boundary_answer",
        )
        return contract.to_dict()

    def prompt_instructions(self, contract: Dict[str, Any], boundary: Dict[str, Any]) -> str:
        lines = [
            "[Evidence contract]",
            f"- Contract version: {contract['contract_version']}",
            f"- Risk tier: {contract['risk_tier']}",
            f"- Answer mode: {contract['answer_mode']}",
            f"- Evidence sufficiency: {contract['evidence_sufficiency']}",
            f"- Retrieval confidence: {contract['retrieval_confidence']:.2f}",
            "- Forbidden actions: " + "; ".join(contract["forbidden_actions"]),
            "- Required elements: " + "; ".join(contract["required_elements"]),
            "- Allowed content: " + "; ".join(contract["allowed_content"]),
            "- Use only the supplied graph context for evidence claims.",
            "- If a claim is not supported by the graph context, state that the graph does not establish it.",
            "- Do not add medication, lifestyle, diagnosis, emergency, or mechanism details unless they appear in the retrieved context.",
        ]
        if boundary.get("warnings"):
            lines.append("- Boundary note that must remain visible: " + " ".join(boundary["warnings"]))
        return "\n".join(lines)

    def controlled_answer(self, question: str, role: str, contract: Dict[str, Any], boundary: Dict[str, Any]) -> str:
        scope = boundary.get("scope_level", "the current evidence scope")
        validation = boundary.get("validation_status", "Validation status is unavailable.")
        if role == "researcher":
            return (
                f"This question crosses a high-risk or out-of-scope boundary for the current graph. "
                f"The system can document the boundary but should not answer it as an evidence-supported result. "
                f"Current scope: {scope}. Validation status: {validation} "
                "A suitable next step is to treat this as a research-gap or protocol-development item and perform "
                "disease-specific extraction plus expert validation before using it for interpretation."
            )
        if role == "medical":
            return (
                f"The current graph should not be used to make this patient-specific clinical decision. "
                f"Current scope: {scope}. Validation status: {validation} "
                "The answer is limited to evidence communication: the platform can show that this topic requires "
                "clinician judgment, local guidelines, and disease-specific validation, but it cannot recommend "
                "diagnosis, medication continuation or discontinuation, dose adjustment, or urgent triage thresholds."
            )
        return (
            f"The current graph is not designed to answer this as personal medical advice. "
            f"Current scope: {scope}. Validation status: {validation} "
            "It can help organize questions for a clinician, but it should not tell you whether to start, stop, "
            "continue, or change a medicine, diagnose a condition, or decide whether symptoms are urgent."
        )

    def _retrieval_confidence(self, knowledge: Dict[str, Any]) -> float:
        summary = knowledge.get("summary") or {}
        relation_count = int(summary.get("relation_count") or 0)
        study_count = int(summary.get("study_count") or 0)
        triage_count = int(summary.get("triage_count") or 0)
        score = 0.0
        score += min(relation_count, 5) * 0.08
        score += min(study_count, 5) * 0.08
        score += min(triage_count, 3) * 0.07
        return round(min(score, 1.0), 2)

    def _risk_tier(
        self,
        patient_specific: bool,
        medication: bool,
        diagnosis_or_triage: bool,
        out_of_scope: bool,
        scaffold: bool,
        retrieval_confidence: float,
    ) -> str:
        if out_of_scope and (patient_specific or medication or diagnosis_or_triage):
            return "critical"
        if diagnosis_or_triage or (patient_specific and medication):
            return "high"
        if out_of_scope or medication or patient_specific:
            return "elevated"
        if scaffold or retrieval_confidence < 0.35:
            return "guarded"
        return "low"

    def _evidence_sufficiency(self, retrieval_confidence: float, out_of_scope: bool, scaffold: bool) -> str:
        if out_of_scope:
            return "insufficient_for_direct_answer"
        if scaffold:
            return "limited_to_unvalidated_extension_scaffold"
        if retrieval_confidence >= 0.65:
            return "sufficient_for_bounded_educational_answer"
        if retrieval_confidence >= 0.35:
            return "partial_context_only"
        return "weak_or_sparse_context"

    def _answer_mode(
        self,
        risk_tier: str,
        role: str,
        out_of_scope: bool,
        medication: bool,
        diagnosis_or_triage: bool,
    ) -> str:
        if risk_tier in {"critical", "high"}:
            return "controlled_boundary_answer"
        if out_of_scope:
            return "controlled_boundary_answer"
        if medication and role != "researcher":
            return "bounded_no_medication_directive"
        if diagnosis_or_triage:
            return "bounded_no_triage_threshold"
        if risk_tier == "guarded":
            return "bounded_scope_limited_answer"
        return "standard_evidence_answer"

    def _required_elements(self, risk_tier: str, scope: str, scaffold: bool, out_of_scope: bool) -> List[str]:
        elements = ["state evidence scope", "avoid individualized medical advice"]
        if scaffold:
            elements.append("state that this module was not empirically validated in this study")
        if out_of_scope:
            elements.append("state that the graph lacks in-scope evidence")
        if risk_tier in {"critical", "high", "elevated"}:
            elements.append("redirect patient-specific decisions to qualified clinical care")
        if "arthritis/weather-pain" in scope:
            elements.append("limit claims to arthritis/weather-pain feasibility evidence")
        return elements

    def _allowed_content(self, role: str, scaffold: bool, out_of_scope: bool) -> List[str]:
        if out_of_scope:
            return ["boundary explanation", "research-gap documentation", "clinician referral language"]
        base = ["evidence-scope explanation", "uncertainty statement", "retrieved-context summary"]
        if role == "researcher":
            base.extend(["study-design suggestions", "evidence-gap mapping"])
        elif role == "medical":
            base.extend(["clinical communication framing", "PMID-traceable background"])
        else:
            base.extend(["plain-language education", "questions to discuss with a clinician"])
        if scaffold:
            base.append("validation-pending statement")
        return base


class ContractClaimVerifier:
    """Check generated answers against the pre-generation evidence contract."""

    def verify_and_repair(
        self,
        answer: str,
        question: str,
        context: str,
        contract: Dict[str, Any],
        boundary: Dict[str, Any],
        role: str,
        controlled_answer: str,
    ) -> tuple[str, Dict[str, Any]]:
        findings = self._findings(answer, context, contract)
        max_severity = max([item["severity"] for item in findings], default=0)
        repair_applied = False

        repaired = answer
        if contract.get("answer_mode") == "controlled_boundary_answer":
            repaired = controlled_answer
            repair_applied = repaired.strip() != answer.strip()
        elif max_severity >= 3:
            repaired = controlled_answer
            repair_applied = True
        elif max_severity >= 2:
            repaired = self._append_contract_notice(answer, contract, boundary)
            repair_applied = True

        verification = {
            "contract_version": contract.get("contract_version", CONTRACT_VERSION),
            "n_findings": len(findings),
            "max_severity": max_severity,
            "repair_applied": repair_applied,
            "findings": findings,
        }
        return repaired, verification

    def _findings(self, answer: str, context: str, contract: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = answer.lower()
        context_lower = context.lower()
        findings: List[Dict[str, Any]] = []

        for pattern in DIRECTIVE_PATTERNS:
            if re.search(pattern, text):
                findings.append(
                    {
                        "type": "forbidden_directive",
                        "severity": 3,
                        "evidence": pattern,
                        "message": "Answer contains a patient-facing directive forbidden by the evidence contract.",
                    }
                )

        for term in CAUSAL_OVERCLAIM_TERMS:
            if term in text:
                findings.append(
                    {
                        "type": "causal_overclaim_language",
                        "severity": 2,
                        "evidence": term,
                        "message": "Answer uses causal certainty language not allowed unless directly established by context.",
                    }
                )

        if "medication_boundary" in contract.get("risk_flags", []):
            mentioned_medications = [term for term in MEDICATION_TERMS if term in text and term not in context_lower]
            if mentioned_medications:
                findings.append(
                    {
                        "type": "out_of_context_medication_detail",
                        "severity": 2,
                        "evidence": "; ".join(sorted(set(mentioned_medications))[:8]),
                        "message": "Medication terms appear in the answer without being present in retrieved evidence.",
                    }
                )

        if contract.get("evidence_sufficiency") in {"insufficient_for_direct_answer", "weak_or_sparse_context"}:
            if len(_split_sentences(answer)) > 4:
                findings.append(
                    {
                        "type": "answer_too_specific_for_sparse_context",
                        "severity": 2,
                        "evidence": f"{len(_split_sentences(answer))} sentences",
                        "message": "Sparse or out-of-scope retrieval should produce a short boundary answer.",
                    }
                )

        return findings

    def _append_contract_notice(self, answer: str, contract: Dict[str, Any], boundary: Dict[str, Any]) -> str:
        notice = (
            "Evidence-contract note: the retrieved graph context does not support individualized diagnosis, "
            "medication adjustment, urgent triage thresholds, or causal certainty beyond the stated evidence scope."
        )
        if notice.lower() in answer.lower():
            return answer
        return f"{answer.rstrip()}\n\n{notice}"


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term.lower() in text for term in terms)


def _split_sentences(text: str) -> List[str]:
    return [item.strip() for item in re.split(r"(?<=[.!?。！？])\s+", text) if item.strip()]

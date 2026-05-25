"""
Claim-level evidence ledger for Graph-RAG answers.

The ledger is a lightweight, model-agnostic accountability layer. It does not
verify clinical truth by itself; it records what evidence source, scope label,
and use boundary should travel with each generated answer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ClaimRecord:
    claim_type: str
    claim_text: str
    evidence_source: str
    support_status: str
    pmids: List[str]
    boundary_status: str
    reviewer_note: str

    def to_dict(self) -> Dict:
        return asdict(self)


class ClaimEvidenceLedger:
    """Build claim-level trace records from retrieved KG context and boundary state."""

    def build(self, question: str, answer: str, knowledge: Dict, boundary: Dict, role: str) -> List[Dict]:
        records: List[ClaimRecord] = []

        scope = boundary.get("scope_level", "unknown scope")
        validation = boundary.get("validation_status", "unknown validation status")
        modules = boundary.get("matched_modules") or ["no matched module"]

        records.append(
            ClaimRecord(
                claim_type="scope",
                claim_text=f"The answer is constrained to: {scope}.",
                evidence_source="EvidenceBoundaryGate",
                support_status="rule-assigned",
                pmids=[],
                boundary_status="bounded",
                reviewer_note=validation,
            )
        )

        for row in knowledge.get("triage", [])[:3]:
            module = row.get("module", "unknown module")
            status = row.get("validation_status", "unknown status")
            support_status = (
                "preliminary expert-adjudicated feasibility evidence"
                if "adjudication" in status.lower() or "expert" in status.lower()
                else "ontology-supported scaffold; disease-specific validation pending"
            )
            records.append(
                ClaimRecord(
                    claim_type="triage_module",
                    claim_text=f"{module}: {row.get('evidence_grade', 'evidence interpretation unavailable')}.",
                    evidence_source="Evidence triage layer",
                    support_status=support_status,
                    pmids=[],
                    boundary_status="requires visible validation status",
                    reviewer_note=status,
                )
            )

        pmids = [str(study.get("pmid")) for study in knowledge.get("studies", []) if study.get("pmid")]
        if pmids:
            records.append(
                ClaimRecord(
                    claim_type="literature_trace",
                    claim_text="The retrieved answer context includes PMID-traceable literature.",
                    evidence_source="Retrieved Study nodes",
                    support_status="PMID-traceable context",
                    pmids=pmids[:5],
                    boundary_status="citation trace only; not causal proof",
                    reviewer_note="PMID retrieval supports traceability, not automatic validity.",
                )
            )

        if boundary.get("blocks_clinical_recommendation") or boundary.get("abstention_required"):
            records.append(
                ClaimRecord(
                    claim_type="abstention_or_block",
                    claim_text="Individualized diagnosis, prediction, treatment, or medication adjustment is blocked.",
                    evidence_source="EvidenceBoundaryGate",
                    support_status="safety rule triggered",
                    pmids=[],
                    boundary_status="blocked",
                    reviewer_note="The platform is research and education infrastructure, not clinical decision support.",
                )
            )

        if role == "researcher":
            records.append(
                ClaimRecord(
                    claim_type="research_use",
                    claim_text="The output can be used for hypothesis generation and evidence-gap mapping.",
                    evidence_source="Role-specific Graph-RAG policy",
                    support_status="workflow claim",
                    pmids=[],
                    boundary_status="requires external study validation",
                    reviewer_note="Research suggestions are not epidemiologic effect estimates.",
                )
            )
        elif role == "medical":
            records.append(
                ClaimRecord(
                    claim_type="clinical_use_boundary",
                    claim_text="The output can support communication and documentation, not patient-specific decisions.",
                    evidence_source="Role-specific Graph-RAG policy",
                    support_status="bounded-use claim",
                    pmids=[],
                    boundary_status="no individualized clinical recommendation",
                    reviewer_note="Clinicians must use independent clinical judgment and guidelines.",
                )
            )
        else:
            records.append(
                ClaimRecord(
                    claim_type="public_use_boundary",
                    claim_text="The output can help organize questions and symptom notes for a clinician visit.",
                    evidence_source="Role-specific Graph-RAG policy",
                    support_status="bounded-use claim",
                    pmids=[],
                    boundary_status="education only",
                    reviewer_note="Warning symptoms should be assessed by qualified health professionals.",
                )
            )

        return [record.to_dict() for record in records]

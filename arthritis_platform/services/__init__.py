"""
核心服务模块
"""

from .demo_backend import DemoGraphQueryService, DemoLLMService
from .claim_ledger import ClaimEvidenceLedger
from .evidence_contract import ContractClaimVerifier, EvidenceContractCompiler
from .evidence_boundary import EvidenceBoundaryGate
from .rag_engine import RAGEngine

try:
    from .graph_query import GraphQueryService
except ImportError:
    GraphQueryService = None

def get_llm_service_class():
    """Import the external LLM client only when live mode actually needs it."""
    try:
        from .llm_service import LLMService
    except ImportError:
        return None
    return LLMService

__all__ = [
    "ClaimEvidenceLedger",
    "ContractClaimVerifier",
    "DemoGraphQueryService",
    "DemoLLMService",
    "EvidenceContractCompiler",
    "EvidenceBoundaryGate",
    "GraphQueryService",
    "get_llm_service_class",
    "RAGEngine",
]

"""Data models for verification results."""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

from core.hybrid_decisor import VerificationStrategy


class Verdict(Enum):
    """Verification verdict types."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNVERIFIABLE = "UNVERIFIABLE"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class VerificationResult:
    """Result of content verification."""

    verdict: Verdict
    confidence: float  # 0.0 to 100.0
    explanation: str
    sources: List[str]
    evidence: List[str]
    strategy_used: Optional[VerificationStrategy]
    processing_time: float
    timestamp: datetime
    metadata: Dict

    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return {
            "verdict": self.verdict.value,
            "confidence": round(self.confidence, 2),
            "explanation": self.explanation,
            "sources": self.sources,
            "evidence": self.evidence,
            "strategy": self.strategy_used.value if self.strategy_used else None,
            "processing_time": round(self.processing_time, 3),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

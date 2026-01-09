"""Response models for cloud API results."""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


class ClaimRating(Enum):
    """Standardized claim ratings across different APIs."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    MOSTLY_TRUE = "MOSTLY_TRUE"
    MOSTLY_FALSE = "MOSTLY_FALSE"
    MIXED = "MIXED"
    UNVERIFIABLE = "UNVERIFIABLE"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class FactCheckSource:
    """A source that fact-checked a claim."""

    name: str
    url: Optional[str]
    date: Optional[datetime]
    rating: ClaimRating
    title: Optional[str] = None
    excerpt: Optional[str] = None


@dataclass
class CloudVerificationResult:
    """Standardized result from a cloud API."""

    claim: str
    rating: ClaimRating
    confidence: float  # 0.0 to 100.0
    sources: List[FactCheckSource]
    explanation: Optional[str] = None
    api_name: str = ""
    raw_response: Optional[Dict] = None

    @property
    def has_sources(self) -> bool:
        """Check if result has fact-check sources."""
        return len(self.sources) > 0

    @property
    def source_count(self) -> int:
        """Get number of sources."""
        return len(self.sources)


def rating_to_score(rating: ClaimRating) -> float:
    """Convert rating to numeric score (0-100).

    Args:
        rating: Claim rating

    Returns:
        Numeric score from 0 (false) to 100 (true)
    """
    scores = {
        ClaimRating.TRUE: 100.0,
        ClaimRating.MOSTLY_TRUE: 75.0,
        ClaimRating.MIXED: 50.0,
        ClaimRating.MOSTLY_FALSE: 25.0,
        ClaimRating.FALSE: 0.0,
        ClaimRating.UNVERIFIABLE: 50.0,
        ClaimRating.UNCERTAIN: 50.0
    }
    return scores.get(rating, 50.0)


def normalize_rating(raw_rating: str) -> ClaimRating:
    """Normalize various rating formats to standard ClaimRating.

    Args:
        raw_rating: Raw rating string from API

    Returns:
        Standardized ClaimRating
    """
    rating_lower = raw_rating.lower().strip()

    # True variants
    if any(word in rating_lower for word in ['true', 'correct', 'accurate', 'verified']):
        if any(word in rating_lower for word in ['mostly', 'partially', 'somewhat']):
            return ClaimRating.MOSTLY_TRUE
        return ClaimRating.TRUE

    # False variants
    if any(word in rating_lower for word in ['false', 'incorrect', 'inaccurate', 'debunked']):
        if any(word in rating_lower for word in ['mostly', 'partially', 'somewhat']):
            return ClaimRating.MOSTLY_FALSE
        return ClaimRating.FALSE

    # Mixed/uncertain
    if any(word in rating_lower for word in ['mixed', 'half', 'partly']):
        return ClaimRating.MIXED

    if any(word in rating_lower for word in ['unverifiable', 'unproven', 'inconclusive']):
        return ClaimRating.UNVERIFIABLE

    # Default to uncertain
    return ClaimRating.UNCERTAIN

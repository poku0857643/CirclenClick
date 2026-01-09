"""Decision logic for choosing local vs cloud vs hybrid verification."""

from enum import Enum
from dataclasses import dataclass
from typing import List

from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VerificationStrategy(Enum):
    """Verification strategy types."""

    LOCAL_ONLY = "local_only"  # Fast, using only local models
    CLOUD_ONLY = "cloud_only"  # Comprehensive, using only cloud APIs
    HYBRID = "hybrid"  # Balanced, using both local and cloud


@dataclass
class DecisionFactors:
    """Factors used to decide verification strategy."""

    claim_complexity: float  # 0.0 to 1.0, higher is more complex
    claim_count: int
    has_numbers: bool  # Statistical claims need more verification
    has_superlatives: bool  # "largest", "first", etc.
    content_length: int
    cache_available: bool
    cloud_apis_available: bool
    user_preference: VerificationStrategy = VerificationStrategy.HYBRID


class HybridDecisor:
    """Decides which verification strategy to use based on content and context."""

    def __init__(self):
        """Initialize the hybrid decisor."""
        self.logger = logger

    def decide(
        self,
        claims: List[str],
        content_length: int,
        cache_available: bool = False,
        user_preference: VerificationStrategy = VerificationStrategy.HYBRID
    ) -> VerificationStrategy:
        """Decide which verification strategy to use.

        Args:
            claims: List of extracted claims
            content_length: Length of the content
            cache_available: Whether cached result is available
            user_preference: User's preferred strategy (if specified)

        Returns:
            Recommended verification strategy
        """
        # If cache is available and fresh, use it (handled upstream)
        if cache_available:
            self.logger.info("Using cached result, skipping verification")
            return VerificationStrategy.LOCAL_ONLY

        # Check if cloud APIs are available
        cloud_available = settings.has_cloud_apis() and not settings.local_only_mode

        # If user prefers local only or cloud APIs not available
        if not cloud_available or user_preference == VerificationStrategy.LOCAL_ONLY:
            self.logger.info("Using LOCAL_ONLY strategy (cloud unavailable or disabled)")
            return VerificationStrategy.LOCAL_ONLY

        # If user explicitly wants cloud only
        if user_preference == VerificationStrategy.CLOUD_ONLY:
            self.logger.info("Using CLOUD_ONLY strategy (user preference)")
            return VerificationStrategy.CLOUD_ONLY

        # Calculate decision factors
        factors = self._calculate_factors(claims, content_length, cloud_available, user_preference)

        # Decide based on factors
        strategy = self._make_decision(factors)

        self.logger.info(
            f"Selected {strategy.value} strategy "
            f"(complexity: {factors.claim_complexity:.2f}, claims: {factors.claim_count})"
        )

        return strategy

    def _calculate_factors(
        self,
        claims: List[str],
        content_length: int,
        cloud_apis_available: bool,
        user_preference: VerificationStrategy
    ) -> DecisionFactors:
        """Calculate decision factors from content.

        Args:
            claims: List of claims
            content_length: Content length
            cloud_apis_available: Whether cloud APIs are available
            user_preference: User's preferred strategy

        Returns:
            DecisionFactors instance
        """
        claim_count = len(claims)

        # Calculate complexity (0.0 to 1.0)
        complexity = 0.0

        if claim_count > 0:
            # More claims = higher complexity
            complexity += min(claim_count / 10, 0.3)

            # Longer claims = higher complexity
            avg_claim_length = sum(len(c.split()) for c in claims) / claim_count
            complexity += min(avg_claim_length / 50, 0.3)

            # Check for numbers, percentages, dates
            has_numbers = any(
                any(char.isdigit() for char in claim)
                for claim in claims
            )
            if has_numbers:
                complexity += 0.2

            # Check for superlatives (biggest, first, most, etc.)
            superlatives = ['biggest', 'largest', 'most', 'least', 'first', 'last', 'only']
            has_superlatives = any(
                any(word in claim.lower() for word in superlatives)
                for claim in claims
            )
            if has_superlatives:
                complexity += 0.2

        # Cap at 1.0
        complexity = min(complexity, 1.0)

        return DecisionFactors(
            claim_complexity=complexity,
            claim_count=claim_count,
            has_numbers=has_numbers if claim_count > 0 else False,
            has_superlatives=has_superlatives if claim_count > 0 else False,
            content_length=content_length,
            cache_available=False,
            cloud_apis_available=cloud_apis_available,
            user_preference=user_preference
        )

    def _make_decision(self, factors: DecisionFactors) -> VerificationStrategy:
        """Make strategy decision based on factors.

        Args:
            factors: Decision factors

        Returns:
            Chosen strategy
        """
        # No claims = local only (quick opinion/sentiment check)
        if factors.claim_count == 0:
            return VerificationStrategy.LOCAL_ONLY

        # Simple content with low complexity = local only
        if factors.claim_complexity < 0.3 and factors.claim_count <= 2:
            return VerificationStrategy.LOCAL_ONLY

        # High complexity or many claims = hybrid
        if factors.claim_complexity > 0.6 or factors.claim_count > 5:
            if factors.cloud_apis_available:
                return VerificationStrategy.HYBRID
            else:
                return VerificationStrategy.LOCAL_ONLY

        # Medium complexity with numbers or superlatives = hybrid
        if (factors.has_numbers or factors.has_superlatives) and factors.cloud_apis_available:
            return VerificationStrategy.HYBRID

        # Default to local for quick checks
        return VerificationStrategy.LOCAL_ONLY

    def estimate_time(self, strategy: VerificationStrategy) -> float:
        """Estimate verification time in seconds.

        Args:
            strategy: Verification strategy

        Returns:
            Estimated time in seconds
        """
        estimates = {
            VerificationStrategy.LOCAL_ONLY: 1.5,
            VerificationStrategy.CLOUD_ONLY: 10.0,
            VerificationStrategy.HYBRID: 5.0
        }
        return estimates.get(strategy, 2.0)

"""Aggregates verification results from multiple sources."""

from typing import List, Dict
from collections import Counter
from datetime import datetime

from core.models import Verdict, VerificationResult
from cloud.response_models import CloudVerificationResult, ClaimRating, rating_to_score
from utils.logger import get_logger

logger = get_logger(__name__)


class ResultAggregator:
    """Aggregates results from multiple verification sources."""

    def __init__(self):
        """Initialize result aggregator."""
        self.logger = logger

    def aggregate_cloud_results(
        self,
        results: List[CloudVerificationResult],
        original_claim: str
    ) -> VerificationResult:
        """Aggregate multiple cloud API results into single verdict.

        Args:
            results: List of cloud verification results
            original_claim: Original claim text

        Returns:
            Aggregated VerificationResult
        """
        if not results:
            return self._create_no_results_verdict(original_claim)

        # Extract ratings and scores
        ratings = [r.rating for r in results]
        confidences = [r.confidence for r in results]
        all_sources = []
        all_evidence = []

        for result in results:
            all_sources.extend([s.name for s in result.sources])
            if result.explanation:
                all_evidence.append(f"[{result.api_name}] {result.explanation}")

        # Determine consensus verdict
        verdict = self._determine_verdict(ratings)

        # Calculate aggregated confidence
        confidence = self._calculate_aggregated_confidence(ratings, confidences)

        # Generate explanation
        explanation = self._generate_explanation(results, verdict)

        # Get unique sources
        unique_sources = list(set(all_sources))

        return VerificationResult(
            verdict=verdict,
            confidence=confidence,
            explanation=explanation,
            sources=unique_sources,
            evidence=all_evidence,
            strategy_used=None,  # Will be set by engine
            processing_time=0.0,  # Will be set by engine
            timestamp=datetime.now(),
            metadata={
                "api_count": len(results),
                "source_count": len(unique_sources),
                "rating_distribution": self._get_rating_distribution(ratings)
            }
        )

    def _determine_verdict(self, ratings: List[ClaimRating]) -> Verdict:
        """Determine final verdict from multiple ratings.

        Args:
            ratings: List of ratings from different sources

        Returns:
            Final Verdict
        """
        if not ratings:
            return Verdict.UNCERTAIN

        # Count ratings
        rating_counts = Counter(ratings)
        most_common_rating = rating_counts.most_common(1)[0][0]

        # Map ClaimRating to Verdict
        rating_map = {
            ClaimRating.TRUE: Verdict.TRUE,
            ClaimRating.MOSTLY_TRUE: Verdict.TRUE,
            ClaimRating.MIXED: Verdict.MISLEADING,
            ClaimRating.MOSTLY_FALSE: Verdict.MISLEADING,
            ClaimRating.FALSE: Verdict.FALSE,
            ClaimRating.UNVERIFIABLE: Verdict.UNVERIFIABLE,
            ClaimRating.UNCERTAIN: Verdict.UNCERTAIN
        }

        verdict = rating_map.get(most_common_rating, Verdict.UNCERTAIN)

        # If ratings are split, mark as uncertain
        if len(rating_counts) >= 3 and len(ratings) >= 3:
            # Too much disagreement
            return Verdict.UNCERTAIN

        return verdict

    def _calculate_aggregated_confidence(
        self,
        ratings: List[ClaimRating],
        confidences: List[float]
    ) -> float:
        """Calculate aggregated confidence score.

        Args:
            ratings: List of ratings
            confidences: List of confidence scores

        Returns:
            Aggregated confidence (0-100)
        """
        if not ratings:
            return 0.0

        # Base confidence on average
        avg_confidence = sum(confidences) / len(confidences)

        # Bonus for agreement
        rating_counts = Counter(ratings)
        agreement_ratio = rating_counts.most_common(1)[0][1] / len(ratings)

        agreement_bonus = (agreement_ratio - 0.5) * 40  # Up to +20% for full agreement

        # Bonus for multiple sources
        source_bonus = min(len(ratings) * 5, 15)

        total_confidence = avg_confidence + agreement_bonus + source_bonus

        return min(max(total_confidence, 0.0), 100.0)

    def _generate_explanation(
        self,
        results: List[CloudVerificationResult],
        verdict: Verdict
    ) -> str:
        """Generate human-readable explanation.

        Args:
            results: Cloud verification results
            verdict: Final verdict

        Returns:
            Explanation text
        """
        api_count = len(results)
        total_sources = sum(len(r.sources) for r in results)

        verdict_text = {
            Verdict.TRUE: "supports this claim",
            Verdict.FALSE: "contradicts this claim",
            Verdict.MISLEADING: "finds this claim partially accurate but misleading",
            Verdict.UNVERIFIABLE: "cannot verify this claim",
            Verdict.UNCERTAIN: "provides mixed assessments of this claim"
        }

        base = f"Analysis from {api_count} fact-checking service(s) {verdict_text.get(verdict, 'analyzed this claim')}"

        if total_sources > 0:
            return f"{base}, citing {total_sources} source(s)."
        else:
            return f"{base}."

    def _get_rating_distribution(self, ratings: List[ClaimRating]) -> Dict[str, int]:
        """Get distribution of ratings.

        Args:
            ratings: List of ratings

        Returns:
            Dictionary of rating counts
        """
        rating_counts = Counter(ratings)
        return {rating.value: count for rating, count in rating_counts.items()}

    def _create_no_results_verdict(self, claim: str) -> VerificationResult:
        """Create verdict when no results available.

        Args:
            claim: Original claim

        Returns:
            Default VerificationResult
        """
        return VerificationResult(
            verdict=Verdict.UNCERTAIN,
            confidence=0.0,
            explanation="No fact-checking results available from cloud services.",
            sources=[],
            evidence=[],
            strategy_used=None,
            processing_time=0.0,
            timestamp=datetime.now(),
            metadata={"api_count": 0, "source_count": 0}
        )

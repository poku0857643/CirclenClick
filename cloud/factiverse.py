"""Factiverse API client."""

from typing import Optional, List
from datetime import datetime

from cloud.base_client import BaseAPIClient
from cloud.response_models import (
    CloudVerificationResult,
    FactCheckSource,
    ClaimRating,
    normalize_rating
)
from utils.config import settings


class FactiverseClient(BaseAPIClient):
    """Client for Factiverse API.

    Factiverse provides AI-powered fact-checking and evidence search.
    API Documentation: https://www.factiverse.ai/
    """

    BASE_URL = "https://api.factiverse.ai/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Factiverse client.

        Args:
            api_key: Factiverse API key (uses settings.factiverse_api_key if not provided)
        """
        super().__init__(
            api_key=api_key or settings.factiverse_api_key,
            timeout=settings.cloud_timeout_seconds
        )

    @property
    def api_name(self) -> str:
        """Get API name."""
        return "Factiverse"

    async def verify_claim(self, claim: str) -> Optional[CloudVerificationResult]:
        """Verify a claim using Factiverse API.

        Args:
            claim: The claim to verify

        Returns:
            CloudVerificationResult or None
        """
        if not self.is_configured:
            self.logger.warning(f"{self.api_name}: API key not configured")
            return None

        try:
            self.logger.info(f"{self.api_name}: Verifying claim: {claim[:50]}...")

            client = await self._get_client()

            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": claim,
                "language": "en"
            }

            # Note: Actual endpoint may vary - this is a generic implementation
            response = await client.post(
                f"{self.BASE_URL}/fact-check",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()

            return self._parse_response(claim, data)

        except Exception as e:
            self.logger.error(f"{self.api_name}: Error verifying claim: {e}")
            # Return placeholder result if API fails
            return self._create_placeholder_result(claim)

    def _parse_response(self, claim: str, data: dict) -> Optional[CloudVerificationResult]:
        """Parse Factiverse response.

        Args:
            claim: Original claim
            data: API response data

        Returns:
            CloudVerificationResult or None
        """
        try:
            # Parse response structure (adjust based on actual API)
            verdict = data.get("verdict", "uncertain")
            confidence_score = data.get("confidence", 0.5) * 100
            evidence = data.get("evidence", [])

            # Normalize verdict to our rating system
            rating = normalize_rating(verdict)

            # Extract sources from evidence
            sources: List[FactCheckSource] = []
            for item in evidence[:5]:  # Limit to 5 sources
                source = FactCheckSource(
                    name=item.get("source", "Unknown"),
                    url=item.get("url"),
                    date=datetime.now(),
                    rating=rating,
                    excerpt=item.get("text", "")[:200]
                )
                sources.append(source)

            # Generate explanation
            explanation = data.get("explanation", self._generate_explanation(rating, len(sources)))

            return CloudVerificationResult(
                claim=claim,
                rating=rating,
                confidence=confidence_score,
                sources=sources,
                explanation=explanation,
                api_name=self.api_name,
                raw_response=data
            )

        except Exception as e:
            self.logger.error(f"{self.api_name}: Error parsing response: {e}")
            return self._create_placeholder_result(claim)

    def _create_placeholder_result(self, claim: str) -> CloudVerificationResult:
        """Create a placeholder result when API is unavailable.

        Args:
            claim: The claim

        Returns:
            Placeholder CloudVerificationResult
        """
        return CloudVerificationResult(
            claim=claim,
            rating=ClaimRating.UNCERTAIN,
            confidence=30.0,
            sources=[],
            explanation=f"{self.api_name} API unavailable or not configured. Cannot verify this claim.",
            api_name=self.api_name,
            raw_response=None
        )

    def _generate_explanation(self, rating: ClaimRating, source_count: int) -> str:
        """Generate explanation based on rating and sources.

        Args:
            rating: Claim rating
            source_count: Number of sources

        Returns:
            Explanation text
        """
        rating_text = {
            ClaimRating.TRUE: "verified as accurate",
            ClaimRating.MOSTLY_TRUE: "largely supported",
            ClaimRating.MIXED: "partially supported with some inaccuracies",
            ClaimRating.MOSTLY_FALSE: "largely contradicted",
            ClaimRating.FALSE: "contradicted",
            ClaimRating.UNVERIFIABLE: "could not be verified",
            ClaimRating.UNCERTAIN: "requires further investigation"
        }

        base_text = f"Analysis found this claim to be {rating_text.get(rating, 'uncertain')}"

        if source_count > 0:
            return f"{base_text} based on {source_count} evidence source(s)."
        else:
            return f"{base_text}, but evidence is limited."

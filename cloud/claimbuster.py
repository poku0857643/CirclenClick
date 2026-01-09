"""ClaimBuster API client."""

from typing import Optional
from datetime import datetime

from cloud.base_client import BaseAPIClient
from cloud.response_models import (
    CloudVerificationResult,
    FactCheckSource,
    ClaimRating
)
from utils.config import settings


class ClaimBusterClient(BaseAPIClient):
    """Client for ClaimBuster API.

    ClaimBuster provides check-worthiness scores for claims.
    API Documentation: https://idir.uta.edu/claimbuster/
    """

    BASE_URL = "https://idir.uta.edu/claimbuster/api/v2/score/text"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize ClaimBuster client.

        Args:
            api_key: ClaimBuster API key (uses settings.claimbuster_api_key if not provided)
        """
        super().__init__(
            api_key=api_key or settings.claimbuster_api_key,
            timeout=settings.cloud_timeout_seconds
        )

    @property
    def api_name(self) -> str:
        """Get API name."""
        return "ClaimBuster"

    async def verify_claim(self, claim: str) -> Optional[CloudVerificationResult]:
        """Verify a claim using ClaimBuster API.

        Note: ClaimBuster provides check-worthiness scores, not fact-checking verdicts.
        A high score means the claim is worth fact-checking.

        Args:
            claim: The claim to analyze

        Returns:
            CloudVerificationResult with check-worthiness assessment
        """
        if not self.is_configured:
            self.logger.warning(f"{self.api_name}: API key not configured")
            return None

        try:
            self.logger.info(f"{self.api_name}: Analyzing claim: {claim[:50]}...")

            client = await self._get_client()

            # Make API request
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "input_text": claim
            }

            response = await client.post(
                self.BASE_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()

            return self._parse_response(claim, data)

        except Exception as e:
            self.logger.error(f"{self.api_name}: Error analyzing claim: {e}")
            return None

    def _parse_response(self, claim: str, data: dict) -> Optional[CloudVerificationResult]:
        """Parse ClaimBuster response.

        Args:
            claim: Original claim
            data: API response data

        Returns:
            CloudVerificationResult or None
        """
        try:
            results = data.get("results", [])

            if not results:
                return None

            # Get first result
            result = results[0]
            score = result.get("score", 0.0)

            # ClaimBuster score is 0-1, where higher means more check-worthy
            # Convert to our confidence scale
            confidence = score * 100

            # Determine rating based on check-worthiness
            # High score = worth checking = uncertain/needs verification
            if score >= 0.7:
                rating = ClaimRating.UNCERTAIN
                explanation = (
                    f"This claim has a high check-worthiness score ({score:.2f}), "
                    "indicating it makes factual assertions that should be verified. "
                    "Further fact-checking recommended."
                )
            elif score >= 0.5:
                rating = ClaimRating.UNCERTAIN
                explanation = (
                    f"This claim has a moderate check-worthiness score ({score:.2f}), "
                    "suggesting it contains some factual elements worth investigating."
                )
            else:
                rating = ClaimRating.UNVERIFIABLE
                explanation = (
                    f"This claim has a low check-worthiness score ({score:.2f}), "
                    "indicating it may be opinion-based or not contain verifiable factual claims."
                )

            # Create source
            source = FactCheckSource(
                name="ClaimBuster",
                url="https://idir.uta.edu/claimbuster/",
                date=datetime.now(),
                rating=rating,
                title=f"Check-worthiness Score: {score:.2f}",
                excerpt=claim
            )

            return CloudVerificationResult(
                claim=claim,
                rating=rating,
                confidence=confidence,
                sources=[source],
                explanation=explanation,
                api_name=self.api_name,
                raw_response=data
            )

        except Exception as e:
            self.logger.error(f"{self.api_name}: Error parsing response: {e}")
            return None

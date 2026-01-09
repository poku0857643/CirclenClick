"""Google Fact Check Tools API client."""

from typing import Optional, List
from datetime import datetime
import httpx

from cloud.base_client import BaseAPIClient
from cloud.response_models import (
    CloudVerificationResult,
    FactCheckSource,
    ClaimRating,
    normalize_rating
)
from utils.config import settings


class GoogleFactCheckClient(BaseAPIClient):
    """Client for Google Fact Check Tools API.

    API Documentation: https://developers.google.com/fact-check/tools/api
    """

    BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google Fact Check client.

        Args:
            api_key: Google API key (uses settings.google_factcheck_api_key if not provided)
        """
        super().__init__(
            api_key=api_key or settings.google_factcheck_api_key,
            timeout=settings.cloud_timeout_seconds
        )

    @property
    def api_name(self) -> str:
        """Get API name."""
        return "Google Fact Check"

    async def verify_claim(self, claim: str) -> Optional[CloudVerificationResult]:
        """Verify a claim using Google Fact Check API.

        Args:
            claim: The claim to verify

        Returns:
            CloudVerificationResult or None if no fact-checks found
        """
        if not self.is_configured:
            self.logger.warning(f"{self.api_name}: API key not configured")
            return None

        try:
            self.logger.info(f"{self.api_name}: Searching for claim: {claim[:50]}...")

            client = await self._get_client()

            # Make API request
            params = {
                "key": self.api_key,
                "query": claim,
                "languageCode": "en"
            }

            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # Parse response
            if "claims" not in data or len(data["claims"]) == 0:
                self.logger.info(f"{self.api_name}: No fact-checks found")
                return None

            # Process first claim match
            claim_data = data["claims"][0]

            return self._parse_claim_review(claim, claim_data)

        except httpx.HTTPStatusError as e:
            self.logger.error(f"{self.api_name}: HTTP error {e.response.status_code}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"{self.api_name}: Error verifying claim: {e}")
            return None

    def _parse_claim_review(self, original_claim: str, claim_data: dict) -> Optional[CloudVerificationResult]:
        """Parse claim review data from API response.

        Args:
            original_claim: Original claim text
            claim_data: Claim data from API

        Returns:
            CloudVerificationResult or None
        """
        try:
            claim_reviews = claim_data.get("claimReview", [])

            if not claim_reviews:
                return None

            sources: List[FactCheckSource] = []
            ratings: List[ClaimRating] = []

            # Extract all fact-check reviews
            for review in claim_reviews:
                publisher = review.get("publisher", {})
                textual_rating = review.get("textualRating", "")

                # Normalize rating
                rating = normalize_rating(textual_rating)
                ratings.append(rating)

                # Parse date
                review_date = None
                if "reviewDate" in review:
                    try:
                        review_date = datetime.fromisoformat(review["reviewDate"].replace("Z", "+00:00"))
                    except Exception:
                        pass

                # Create source
                source = FactCheckSource(
                    name=publisher.get("name", "Unknown"),
                    url=review.get("url"),
                    date=review_date,
                    rating=rating,
                    title=review.get("title"),
                    excerpt=claim_data.get("text")
                )
                sources.append(source)

            # Determine overall rating (use most common or most recent)
            if not ratings:
                overall_rating = ClaimRating.UNCERTAIN
            else:
                # Use first rating (Google usually orders by relevance)
                overall_rating = ratings[0]

            # Calculate confidence based on source count and agreement
            confidence = self._calculate_confidence(ratings)

            # Generate explanation
            explanation = self._generate_explanation(sources, overall_rating)

            return CloudVerificationResult(
                claim=claim_data.get("text", original_claim),
                rating=overall_rating,
                confidence=confidence,
                sources=sources,
                explanation=explanation,
                api_name=self.api_name,
                raw_response=claim_data
            )

        except Exception as e:
            self.logger.error(f"{self.api_name}: Error parsing claim review: {e}")
            return None

    def _calculate_confidence(self, ratings: List[ClaimRating]) -> float:
        """Calculate confidence score based on ratings.

        Args:
            ratings: List of ratings from different sources

        Returns:
            Confidence score 0-100
        """
        if not ratings:
            return 0.0

        # Base confidence on number of sources
        source_confidence = min(len(ratings) * 15, 60)

        # Bonus if all sources agree
        if len(set(ratings)) == 1:
            source_confidence += 30

        # Bonus for multiple sources
        if len(ratings) >= 3:
            source_confidence += 10

        return min(source_confidence, 95.0)

    def _generate_explanation(self, sources: List[FactCheckSource], rating: ClaimRating) -> str:
        """Generate human-readable explanation.

        Args:
            sources: Fact-check sources
            rating: Overall rating

        Returns:
            Explanation text
        """
        source_count = len(sources)

        if source_count == 0:
            return "No fact-checks found for this claim."

        rating_text = {
            ClaimRating.TRUE: "verified as true",
            ClaimRating.MOSTLY_TRUE: "rated as mostly true",
            ClaimRating.MIXED: "received mixed ratings",
            ClaimRating.MOSTLY_FALSE: "rated as mostly false",
            ClaimRating.FALSE: "debunked as false",
            ClaimRating.UNVERIFIABLE: "could not be verified",
            ClaimRating.UNCERTAIN: "received uncertain ratings"
        }

        rating_desc = rating_text.get(rating, "was fact-checked")

        if source_count == 1:
            source_name = sources[0].name
            return f"This claim was {rating_desc} by {source_name}."
        else:
            return f"This claim was {rating_desc} by {source_count} independent fact-checkers."

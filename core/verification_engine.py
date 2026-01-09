"""Main verification engine that orchestrates the verification process."""

from typing import Optional
from datetime import datetime

from core.models import Verdict, VerificationResult
from core.content_processor import ContentProcessor
from core.hybrid_decisor import HybridDecisor, VerificationStrategy
from core.result_aggregator import ResultAggregator
from cloud.google_factcheck import GoogleFactCheckClient
from cloud.claimbuster import ClaimBusterClient
from cloud.factiverse import FactiverseClient
from storage.cache import cache
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VerificationEngine:
    """Main engine for content verification."""

    def __init__(self):
        """Initialize the verification engine."""
        self.logger = logger
        self.content_processor = ContentProcessor()
        self.hybrid_decisor = HybridDecisor()
        self.result_aggregator = ResultAggregator()

        # Initialize cloud API clients
        self.google_client = GoogleFactCheckClient()
        self.claimbuster_client = ClaimBusterClient()
        self.factiverse_client = FactiverseClient()

        self.logger.info("VerificationEngine initialized")

    async def verify(
        self,
        text: str,
        url: Optional[str] = None,
        platform: Optional[str] = None,
        author: Optional[str] = None,
        user_preference: VerificationStrategy = VerificationStrategy.HYBRID
    ) -> VerificationResult:
        """Verify content for misinformation.

        Args:
            text: Text content to verify
            url: Optional source URL
            platform: Optional platform name
            author: Optional author/username
            user_preference: User's preferred verification strategy

        Returns:
            VerificationResult with verdict and details
        """
        start_time = datetime.now()
        self.logger.info(f"Starting verification for content from {platform or 'unknown'}")

        try:
            # Step 1: Check cache first
            cached_result = cache.get(text)
            if cached_result is not None:
                self.logger.info("Using cached result")
                # Update processing time
                cached_result.processing_time = (datetime.now() - start_time).total_seconds()
                return cached_result

            # Step 2: Process content
            processed_content = self.content_processor.process(
                text=text,
                url=url,
                platform=platform,
                author=author
            )

            # Step 3: Decide verification strategy
            strategy = self.hybrid_decisor.decide(
                claims=processed_content.claims,
                content_length=len(processed_content.cleaned_text),
                cache_available=False,
                user_preference=user_preference
            )

            # Step 4: Perform verification based on strategy
            if strategy == VerificationStrategy.LOCAL_ONLY:
                result = await self._verify_local(processed_content)
            elif strategy == VerificationStrategy.CLOUD_ONLY:
                result = await self._verify_cloud(processed_content)
            else:  # HYBRID
                result = await self._verify_hybrid(processed_content)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            result.strategy_used = strategy

            # Cache the result
            cache.set(text, result)

            self.logger.info(
                f"Verification complete: {result.verdict.value} "
                f"({result.confidence:.1f}% confidence) in {processing_time:.2f}s"
            )

            return result

        except Exception as e:
            self.logger.error(f"Verification failed: {e}", exc_info=True)

            # Return uncertain result on error
            processing_time = (datetime.now() - start_time).total_seconds()
            return VerificationResult(
                verdict=Verdict.UNCERTAIN,
                confidence=0.0,
                explanation=f"Verification failed due to error: {str(e)}",
                sources=[],
                evidence=[],
                strategy_used=VerificationStrategy.LOCAL_ONLY,
                processing_time=processing_time,
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )

    async def _verify_local(self, content) -> VerificationResult:
        """Perform local verification using local models.

        Args:
            content: Processed content

        Returns:
            Verification result
        """
        self.logger.debug("Running local verification")

        # TODO: Implement actual local model verification
        # For now, return a basic result based on simple heuristics

        # Check if no claims found
        if not content.has_claims:
            return VerificationResult(
                verdict=Verdict.UNVERIFIABLE,
                confidence=50.0,
                explanation="No factual claims detected in the content. This appears to be an opinion or subjective statement.",
                sources=[],
                evidence=["No check-worthy claims identified"],
                strategy_used=VerificationStrategy.LOCAL_ONLY,
                processing_time=0.0,
                timestamp=datetime.now(),
                metadata=content.metadata
            )

        # Basic sentiment-based placeholder
        # In real implementation, this would use trained models
        text_lower = content.cleaned_text.lower()

        # Check for obvious false claim patterns (very basic)
        false_indicators = ['earth is flat', 'vaccines cause autism', '5g causes covid']
        if any(indicator in text_lower for indicator in false_indicators):
            return VerificationResult(
                verdict=Verdict.FALSE,
                confidence=95.0,
                explanation="This claim has been repeatedly debunked by scientific evidence.",
                sources=["Scientific consensus"],
                evidence=["Multiple peer-reviewed studies contradict this claim"],
                strategy_used=VerificationStrategy.LOCAL_ONLY,
                processing_time=0.0,
                timestamp=datetime.now(),
                metadata=content.metadata
            )

        # Default: uncertain with local only
        return VerificationResult(
            verdict=Verdict.UNCERTAIN,
            confidence=40.0,
            explanation="Local analysis completed. Cloud verification recommended for higher confidence.",
            sources=["Local model analysis"],
            evidence=[f"Identified {len(content.claims)} claim(s) requiring fact-checking"],
            strategy_used=VerificationStrategy.LOCAL_ONLY,
            processing_time=0.0,
            timestamp=datetime.now(),
            metadata=content.metadata
        )

    async def _verify_cloud(self, content) -> VerificationResult:
        """Perform cloud verification using external APIs.

        Args:
            content: Processed content

        Returns:
            Verification result
        """
        self.logger.debug("Running cloud verification")

        if not settings.has_cloud_apis():
            self.logger.warning("No cloud APIs configured")
            return VerificationResult(
                verdict=Verdict.UNCERTAIN,
                confidence=0.0,
                explanation="Cloud API verification unavailable. Please configure API keys in .env file.",
                sources=[],
                evidence=["Cloud APIs: Not configured"],
                strategy_used=VerificationStrategy.CLOUD_ONLY,
                processing_time=0.0,
                timestamp=datetime.now(),
                metadata=content.metadata
            )

        # Use the best claim or the cleaned text
        claim_to_verify = content.claims[0] if content.claims else content.cleaned_text

        # Call all configured cloud APIs in parallel
        import asyncio
        cloud_results = []

        tasks = []
        if self.google_client.is_configured:
            tasks.append(self.google_client.verify_claim(claim_to_verify))
        if self.claimbuster_client.is_configured:
            tasks.append(self.claimbuster_client.verify_claim(claim_to_verify))
        if self.factiverse_client.is_configured:
            tasks.append(self.factiverse_client.verify_claim(claim_to_verify))

        if not tasks:
            return VerificationResult(
                verdict=Verdict.UNCERTAIN,
                confidence=0.0,
                explanation="No cloud APIs configured. Add API keys to .env to enable cloud verification.",
                sources=[],
                evidence=[],
                strategy_used=VerificationStrategy.CLOUD_ONLY,
                processing_time=0.0,
                timestamp=datetime.now(),
                metadata=content.metadata
            )

        # Run API calls in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        for result in results:
            if result is not None and not isinstance(result, Exception):
                cloud_results.append(result)

        # Aggregate results
        aggregated = self.result_aggregator.aggregate_cloud_results(
            cloud_results,
            claim_to_verify
        )

        # Add content metadata
        aggregated.metadata.update(content.metadata)

        return aggregated

    async def _verify_hybrid(self, content) -> VerificationResult:
        """Perform hybrid verification using both local and cloud.

        Args:
            content: Processed content

        Returns:
            Verification result
        """
        self.logger.debug("Running hybrid verification")

        # Run local verification first (fast)
        local_result = await self._verify_local(content)

        # If local is highly confident, return it
        if local_result.confidence > 90.0:
            self.logger.debug("Local verification highly confident, skipping cloud")
            return local_result

        # Otherwise, also check cloud (if available)
        if settings.has_cloud_apis():
            cloud_result = await self._verify_cloud(content)

            # Combine results
            # TODO: Implement proper result aggregation
            # For now, just return cloud result
            return cloud_result

        # Fall back to local if cloud unavailable
        return local_result

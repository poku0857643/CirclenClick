"""Base client class for cloud API integrations."""

from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
from datetime import datetime

from cloud.response_models import CloudVerificationResult
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAPIClient(ABC):
    """Base class for cloud API clients."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 15):
        """Initialize the API client.

        Args:
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logger
        self._client: Optional[httpx.AsyncClient] = None

    @property
    @abstractmethod
    def api_name(self) -> str:
        """Get the name of this API."""
        pass

    @property
    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return self.api_key is not None and len(self.api_key) > 0

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client.

        Returns:
            Async HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def verify_claim(self, claim: str) -> Optional[CloudVerificationResult]:
        """Verify a claim using this API.

        Args:
            claim: The claim to verify

        Returns:
            CloudVerificationResult or None if API unavailable/error
        """
        pass

    async def verify_claims(self, claims: List[str]) -> List[CloudVerificationResult]:
        """Verify multiple claims.

        Args:
            claims: List of claims to verify

        Returns:
            List of results (may be empty if all fail)
        """
        results = []
        for claim in claims:
            try:
                result = await self.verify_claim(claim)
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.warning(f"{self.api_name}: Failed to verify claim: {e}")
                continue
        return results

    def __del__(self):
        """Cleanup on deletion."""
        if self._client is not None:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception:
                pass

"""Caching layer for verification results."""

import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from diskcache import Cache

from core.models import VerificationResult, Verdict
from core.hybrid_decisor import VerificationStrategy
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VerificationCache:
    """Cache for verification results to reduce API calls."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache.

        Args:
            cache_dir: Directory for cache storage (uses settings.cache_dir if not provided)
        """
        self.cache_dir = cache_dir or settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize disk cache
        self.cache = Cache(
            directory=str(self.cache_dir),
            size_limit=settings.max_cache_size_mb * 1024 * 1024  # Convert MB to bytes
        )

        self.logger = logger
        self.logger.info(f"Cache initialized at {self.cache_dir}")

    def _generate_key(self, text: str) -> str:
        """Generate cache key from text.

        Args:
            text: Text to hash

        Returns:
            Cache key (hex string)
        """
        # Normalize text (lowercase, strip whitespace)
        normalized = text.lower().strip()

        # Generate SHA256 hash
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, text: str) -> Optional[VerificationResult]:
        """Get cached verification result.

        Args:
            text: Text to look up

        Returns:
            Cached VerificationResult or None if not found/expired
        """
        key = self._generate_key(text)

        try:
            cached_data = self.cache.get(key)

            if cached_data is None:
                self.logger.debug(f"Cache miss for key {key[:16]}...")
                return None

            # Check if expired
            cached_time = datetime.fromisoformat(cached_data["timestamp"])
            ttl = timedelta(hours=settings.cache_ttl_hours)

            if datetime.now() - cached_time > ttl:
                self.logger.debug(f"Cache expired for key {key[:16]}...")
                self.cache.delete(key)
                return None

            # Reconstruct VerificationResult
            result = self._deserialize_result(cached_data)

            self.logger.info(f"Cache hit for key {key[:16]}... (age: {datetime.now() - cached_time})")
            return result

        except Exception as e:
            self.logger.error(f"Error reading from cache: {e}")
            return None

    def set(self, text: str, result: VerificationResult):
        """Store verification result in cache.

        Args:
            text: Text that was verified
            result: Verification result to cache
        """
        key = self._generate_key(text)

        try:
            # Serialize result
            cached_data = self._serialize_result(result)

            # Store in cache
            self.cache.set(key, cached_data)

            self.logger.info(f"Cached result for key {key[:16]}... (verdict: {result.verdict.value})")

        except Exception as e:
            self.logger.error(f"Error writing to cache: {e}")

    def clear(self):
        """Clear all cached results."""
        try:
            self.cache.clear()
            self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        try:
            volume = self.cache.volume()
            size_mb = volume / (1024 * 1024)

            return {
                "size_mb": round(size_mb, 2),
                "item_count": len(self.cache),
                "cache_dir": str(self.cache_dir),
                "ttl_hours": settings.cache_ttl_hours,
                "max_size_mb": settings.max_cache_size_mb
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}

    def _serialize_result(self, result: VerificationResult) -> Dict[str, Any]:
        """Serialize VerificationResult to dict for caching.

        Args:
            result: VerificationResult to serialize

        Returns:
            Serializable dictionary
        """
        return {
            "verdict": result.verdict.value,
            "confidence": result.confidence,
            "explanation": result.explanation,
            "sources": result.sources,
            "evidence": result.evidence,
            "strategy_used": result.strategy_used.value if result.strategy_used else None,
            "processing_time": result.processing_time,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }

    def _deserialize_result(self, data: Dict[str, Any]) -> VerificationResult:
        """Deserialize dict to VerificationResult.

        Args:
            data: Serialized result data

        Returns:
            VerificationResult instance
        """
        return VerificationResult(
            verdict=Verdict(data["verdict"]),
            confidence=data["confidence"],
            explanation=data["explanation"],
            sources=data["sources"],
            evidence=data["evidence"],
            strategy_used=VerificationStrategy(data["strategy_used"]) if data.get("strategy_used") else None,
            processing_time=data["processing_time"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


# Global cache instance
cache = VerificationCache()

"""Verification API routes."""

from fastapi import APIRouter, HTTPException
from typing import Dict

from api.schemas import VerifyRequest, VerifyResponse, StatusResponse
from core.verification_engine import VerificationEngine
from core.hybrid_decisor import VerificationStrategy
from utils.config import settings
from storage.cache import cache
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize verification engine (singleton)
engine = VerificationEngine()


@router.post("/verify", response_model=VerifyResponse)
async def verify_content(request: VerifyRequest):
    """Verify content for misinformation.

    Args:
        request: Verification request

    Returns:
        Verification result
    """
    try:
        logger.info(f"Verification request from {request.platform or 'unknown'}")

        # Map strategy string to enum
        strategy_map = {
            "local": VerificationStrategy.LOCAL_ONLY,
            "cloud": VerificationStrategy.CLOUD_ONLY,
            "hybrid": VerificationStrategy.HYBRID
        }
        strategy = strategy_map.get(request.strategy, VerificationStrategy.HYBRID)

        # Run verification
        result = await engine.verify(
            text=request.text,
            url=request.url,
            platform=request.platform,
            author=request.author,
            user_preference=strategy
        )

        # Return response
        return VerifyResponse(**result.to_dict())

    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get service status.

    Returns:
        Status information
    """
    cache_stats = cache.stats()

    return StatusResponse(
        status="running",
        cloud_apis_configured=settings.has_cloud_apis(),
        cache=cache_stats
    )


@router.delete("/cache")
async def clear_cache():
    """Clear verification cache.

    Returns:
        Success message
    """
    try:
        cache.clear()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats() -> Dict:
    """Get cache statistics.

    Returns:
        Cache stats
    """
    return cache.stats()

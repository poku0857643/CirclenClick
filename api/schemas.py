"""Pydantic schemas for API requests and responses."""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    """Request schema for content verification."""

    text: str = Field(..., description="Text content to verify", min_length=1)
    url: Optional[str] = Field(None, description="Source URL of the content")
    platform: Optional[str] = Field(None, description="Platform name (facebook, twitter, threads)")
    author: Optional[str] = Field(None, description="Author/username")
    strategy: Optional[str] = Field("hybrid", description="Verification strategy (local, cloud, hybrid)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The Earth is flat",
                "url": "https://example.com/post/123",
                "platform": "twitter",
                "strategy": "hybrid"
            }
        }


class VerifyResponse(BaseModel):
    """Response schema for content verification."""

    verdict: str = Field(..., description="Verification verdict")
    confidence: float = Field(..., description="Confidence score (0-100)")
    explanation: str = Field(..., description="Human-readable explanation")
    sources: List[str] = Field(default_factory=list, description="Fact-check sources")
    evidence: List[str] = Field(default_factory=list, description="Evidence for verdict")
    strategy: str = Field(..., description="Strategy used")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="Timestamp")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")


class StatusResponse(BaseModel):
    """Response schema for status endpoint."""

    status: str = Field(..., description="Service status")
    cloud_apis_configured: bool = Field(..., description="Whether cloud APIs are configured")
    cache: Dict = Field(default_factory=dict, description="Cache statistics")


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")

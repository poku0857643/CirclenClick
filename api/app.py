"""FastAPI application for CircleNClick verification service."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from api.routes import verify
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CircleNClick Verification API",
    description="Content verification service for detecting misinformation",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(verify.router, prefix="/api/v1", tags=["verification"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "CircleNClick Verification API",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs"
    }


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    from utils.config import settings
    from storage.cache import cache

    return {
        "status": "healthy",
        "cloud_apis": settings.has_cloud_apis(),
        "cache": cache.stats()
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )

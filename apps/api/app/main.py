"""FastAPI application entry point."""

import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from redis import Redis
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.models import ErrorResponse, HealthResponse, MetricsResponse
from app.routes import jobs, styles
from app.services.job_service import JobService

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting StyleForge API", version="1.0.0")
    settings.ensure_directories()
    
    # Test Redis connection
    try:
        redis = Redis.from_url(settings.redis_url)
        redis.ping()
        logger.info("Redis connection established", url=settings.redis_url)
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down StyleForge API")


# Create FastAPI application
app = FastAPI(
    title="StyleForge API",
    description="AI-powered style transfer API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter


# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content=ErrorResponse(
            error="Rate limit exceeded",
            detail=f"Too many requests. Please try again later.",
            request_id=request.state.request_id if hasattr(request.state, 'request_id') else None
        ).model_dump()
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and logging middleware
@app.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    """Add request ID to each request and log request/response."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    response = await call_next(request)
    
    # Log response
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        "Request completed",
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2)
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


# Mount static files for outputs
app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")


# Include routers
app.include_router(styles.router, prefix="/api", tags=["Styles"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    redis_connected = True
    try:
        redis = Redis.from_url(settings.redis_url)
        redis.ping()
    except Exception:
        redis_connected = False
    
    return HealthResponse(
        status="healthy" if redis_connected else "degraded",
        version="1.0.0",
        redis_connected=redis_connected
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics():
    """Basic metrics endpoint."""
    job_service = JobService()
    return job_service.get_metrics()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "StyleForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


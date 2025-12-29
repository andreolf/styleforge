"""Job management API routes."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.models import ErrorResponse, JobResponse
from app.services.job_service import JobService
from app.services.storage import StorageService
from app.services.style_registry import get_style_registry
from app.services.validators import validate_image_file

logger = structlog.get_logger()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post(
    "/jobs",
    response_model=JobResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    }
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def create_job(
    request: Request,
    image: Annotated[UploadFile, File(description="Image file (jpg, png, webp)")],
    style_id: Annotated[str, Form(description="Style preset ID to apply")],
):
    """
    Create a new style transformation job.
    
    Upload an image and specify a style preset. The job will be processed
    asynchronously. Poll the job status endpoint to check progress.
    
    **Limits:**
    - Maximum file size: 10MB
    - Allowed formats: jpg, jpeg, png, webp
    - Rate limit: 30 requests per minute per IP
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Validate style exists
    registry = get_style_registry()
    style = registry.get_style(style_id)
    if not style:
        logger.warning("Invalid style requested", style_id=style_id, request_id=request_id)
        raise HTTPException(
            status_code=400,
            detail=f"Style '{style_id}' not found. Use GET /api/styles to see available options."
        )
    
    # Validate image file
    try:
        validate_image_file(image, settings)
    except ValueError as e:
        logger.warning("File validation failed", error=str(e), request_id=request_id)
        raise HTTPException(status_code=400, detail=str(e))
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    storage = StorageService()
    try:
        input_path = await storage.save_upload(image, job_id)
    except Exception as e:
        logger.error("Failed to save upload", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    # Create job and queue for processing
    job_service = JobService()
    job = job_service.create_job(
        job_id=job_id,
        style_id=style_id,
        input_filename=input_path.name
    )
    
    # Queue the job for background processing
    job_service.enqueue_job(job_id)
    
    logger.info(
        "Job created",
        job_id=job_id,
        style_id=style_id,
        request_id=request_id
    )
    
    return job


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    }
)
async def get_job(job_id: str):
    """
    Get the status and result of a job.
    
    Poll this endpoint to check job progress. When status is 'completed',
    the result_url will contain the path to the generated image.
    """
    job_service = JobService()
    job = job_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    
    return job


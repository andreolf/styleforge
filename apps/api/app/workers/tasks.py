"""Background worker tasks for image processing."""

import structlog

from app.config import get_settings
from app.generators.base import GenerationError
from app.generators.stub import StubGenerator
from app.models import JobStatus
from app.services.job_service import JobService
from app.services.storage import StorageService
from app.services.style_registry import get_style_registry

logger = structlog.get_logger()


def get_generator():
    """Get the appropriate image generator based on configuration."""
    settings = get_settings()
    
    if settings.image_generator == 'huggingface':
        from app.generators.huggingface import HuggingFaceGenerator
        return HuggingFaceGenerator()
    elif settings.image_generator == 'real':
        from app.generators.real import RealGenerator
        return RealGenerator()
    else:
        return StubGenerator(simulate_delay=True, delay_seconds=3.0)


def process_image(job_id: str) -> None:
    """
    Process an image transformation job.
    
    This function is called by RQ workers to process queued jobs.
    
    Args:
        job_id: The job ID to process
    """
    logger.info("Starting job processing", job_id=job_id)
    
    job_service = JobService()
    storage = StorageService()
    settings = get_settings()
    
    # Get job metadata
    job = job_service.get_job(job_id)
    if not job:
        logger.error("Job not found", job_id=job_id)
        return
    
    # Update status to processing
    job_service.update_job(job_id, status=JobStatus.PROCESSING, progress=5)
    
    try:
        # Get style
        registry = get_style_registry()
        style = registry.get_style(job.style_id)
        if not style:
            raise ValueError(f"Style not found: {job.style_id}")
        
        # Get input file path - extract filename from job metadata
        metadata = job_service._load_metadata(job_id)
        input_path = storage.get_upload_path(metadata.input_filename)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create output filename
        output_filename = f"{job_id}-output.png"
        output_path = storage.get_output_path(output_filename)
        
        # Get generator
        generator = get_generator()
        
        # Define progress callback
        def on_progress(progress: int):
            job_service.update_job(job_id, progress=progress)
        
        # Generate the styled image
        logger.info(
            "Generating styled image",
            job_id=job_id,
            style_id=style.id,
            generator=type(generator).__name__
        )
        
        generator.generate(
            input_path=input_path,
            style=style,
            output_path=output_path,
            progress_callback=on_progress
        )
        
        # Update job as completed
        job_service.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            progress=100,
            output_filename=output_filename
        )
        
        logger.info("Job completed successfully", job_id=job_id)
        
    except GenerationError as e:
        logger.error("Generation error", job_id=job_id, error=str(e))
        job_service.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=str(e)
        )
        
    except Exception as e:
        logger.error("Job processing failed", job_id=job_id, error=str(e))
        job_service.update_job(
            job_id,
            status=JobStatus.FAILED,
            error=f"Processing failed: {str(e)}"
        )


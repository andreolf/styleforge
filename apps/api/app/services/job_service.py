"""Job management service."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from redis import Redis
from rq import Queue

from app.config import get_settings
from app.models import JobMetadata, JobResponse, JobStatus, MetricsResponse

logger = structlog.get_logger()


class JobService:
    """Service for managing transformation jobs."""
    
    def __init__(self):
        self.settings = get_settings()
        self.metadata_dir = self.settings.metadata_dir
        self._redis: Optional[Redis] = None
        self._queue: Optional[Queue] = None
    
    @property
    def redis(self) -> Redis:
        """Lazy Redis connection."""
        if self._redis is None:
            self._redis = Redis.from_url(self.settings.redis_url)
        return self._redis
    
    @property
    def queue(self) -> Queue:
        """Lazy RQ queue."""
        if self._queue is None:
            self._queue = Queue('styleforge', connection=self.redis)
        return self._queue
    
    def _get_metadata_path(self, job_id: str) -> Path:
        """Get path to job metadata file."""
        return self.metadata_dir / f"{job_id}.json"
    
    def _save_metadata(self, metadata: JobMetadata) -> None:
        """Save job metadata to JSON file."""
        path = self._get_metadata_path(metadata.job_id)
        with open(path, 'w') as f:
            json.dump(metadata.model_dump(mode='json'), f, default=str)
    
    def _load_metadata(self, job_id: str) -> Optional[JobMetadata]:
        """Load job metadata from JSON file."""
        path = self._get_metadata_path(job_id)
        if not path.exists():
            return None
        
        with open(path, 'r') as f:
            data = json.load(f)
            return JobMetadata(**data)
    
    def create_job(
        self,
        job_id: str,
        style_id: str,
        input_filename: str
    ) -> JobResponse:
        """Create a new job and save its metadata."""
        now = datetime.utcnow()
        
        metadata = JobMetadata(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0,
            style_id=style_id,
            input_filename=input_filename,
            created_at=now,
            updated_at=now
        )
        
        self._save_metadata(metadata)
        
        logger.info("Job created", job_id=job_id, style_id=style_id)
        
        return self._metadata_to_response(metadata)
    
    def get_job(self, job_id: str) -> Optional[JobResponse]:
        """Get job status and result."""
        metadata = self._load_metadata(job_id)
        if metadata is None:
            return None
        
        return self._metadata_to_response(metadata)
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        output_filename: Optional[str] = None,
        error: Optional[str] = None
    ) -> Optional[JobResponse]:
        """Update job status."""
        metadata = self._load_metadata(job_id)
        if metadata is None:
            return None
        
        if status is not None:
            metadata.status = status
        if progress is not None:
            metadata.progress = progress
        if output_filename is not None:
            metadata.output_filename = output_filename
        if error is not None:
            metadata.error = error
        
        metadata.updated_at = datetime.utcnow()
        
        self._save_metadata(metadata)
        
        logger.info(
            "Job updated",
            job_id=job_id,
            status=metadata.status,
            progress=metadata.progress
        )
        
        return self._metadata_to_response(metadata)
    
    def enqueue_job(self, job_id: str) -> None:
        """Add job to processing queue."""
        from app.workers.tasks import process_image
        
        self.queue.enqueue(
            process_image,
            job_id,
            job_timeout='5m',
            result_ttl=3600
        )
        
        logger.info("Job enqueued", job_id=job_id)
    
    def _metadata_to_response(self, metadata: JobMetadata) -> JobResponse:
        """Convert job metadata to API response."""
        result_url = None
        if metadata.output_filename:
            result_url = f"/outputs/{metadata.output_filename}"
        
        return JobResponse(
            job_id=metadata.job_id,
            status=metadata.status,
            progress=metadata.progress,
            result_url=result_url,
            error=metadata.error,
            created_at=metadata.created_at,
            updated_at=metadata.updated_at,
            style_id=metadata.style_id
        )
    
    def get_metrics(self) -> MetricsResponse:
        """Get job metrics by counting metadata files."""
        total = 0
        completed = 0
        failed = 0
        pending = 0
        processing = 0
        
        for path in self.metadata_dir.glob("*.json"):
            total += 1
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    status = data.get('status', '')
                    
                    if status == JobStatus.COMPLETED:
                        completed += 1
                    elif status == JobStatus.FAILED:
                        failed += 1
                    elif status == JobStatus.PENDING:
                        pending += 1
                    elif status == JobStatus.PROCESSING:
                        processing += 1
            except Exception:
                pass
        
        return MetricsResponse(
            total_jobs=total,
            completed_jobs=completed,
            failed_jobs=failed,
            pending_jobs=pending,
            processing_jobs=processing
        )


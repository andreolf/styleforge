"""Pydantic models for API request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StylePreset(BaseModel):
    """Style preset definition."""
    id: str = Field(..., description="Unique style identifier (kebab-case)")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Style description")
    prompt: str = Field(..., description="Generation prompt template")
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "classic-tuxedo",
                "name": "Classic Tuxedo",
                "description": "Elegant spy archetype in formal evening wear",
                "prompt": "wearing an elegant black tuxedo with bow tie, sophisticated spy aesthetic",
                "thumbnail": "/thumbnails/classic-tuxedo.jpg"
            }
        }


class StyleListResponse(BaseModel):
    """Response for style list endpoint."""
    styles: list[StylePreset]
    count: int


class JobCreateRequest(BaseModel):
    """Request to create a new job (style_id from form data)."""
    style_id: str = Field(..., description="ID of the style preset to apply")


class JobResponse(BaseModel):
    """Job status response."""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    result_url: Optional[str] = Field(None, description="URL to result image when completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    style_id: str = Field(..., description="Applied style ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "progress": 100,
                "result_url": "/outputs/550e8400-result.png",
                "error": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:30Z",
                "style_id": "classic-tuxedo"
            }
        }


class JobMetadata(BaseModel):
    """Internal job metadata stored in JSON files."""
    job_id: str
    status: JobStatus
    progress: int = 0
    style_id: str
    input_filename: str
    output_filename: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    redis_connected: bool = True


class MetricsResponse(BaseModel):
    """Basic metrics response."""
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    pending_jobs: int = 0
    processing_jobs: int = 0


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


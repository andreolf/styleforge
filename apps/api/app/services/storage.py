"""File storage service for uploads and outputs."""

import shutil
from pathlib import Path
from typing import Optional

import aiofiles
import structlog
from fastapi import UploadFile

from app.config import get_settings
from app.services.validators import get_file_extension

logger = structlog.get_logger()


class StorageService:
    """Service for managing file storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = self.settings.upload_dir
        self.output_dir = self.settings.output_dir
    
    async def save_upload(self, file: UploadFile, job_id: str) -> Path:
        """
        Save an uploaded file to the uploads directory.
        
        Returns the path to the saved file.
        """
        # Get file extension
        ext = get_file_extension(file.filename or 'image.jpg')
        
        # Create filename with job ID
        filename = f"{job_id}-input.{ext}"
        file_path = self.upload_dir / filename
        
        # Save file
        try:
            contents = await file.read()
            with open(file_path, 'wb') as f:
                f.write(contents)
            
            logger.info("File saved", path=str(file_path), size=len(contents))
            return file_path
            
        except Exception as e:
            logger.error("Failed to save file", error=str(e))
            raise
    
    def get_upload_path(self, filename: str) -> Path:
        """Get full path for an uploaded file."""
        return self.upload_dir / filename
    
    def get_output_path(self, filename: str) -> Path:
        """Get full path for an output file."""
        return self.output_dir / filename
    
    def upload_exists(self, filename: str) -> bool:
        """Check if an upload file exists."""
        return (self.upload_dir / filename).exists()
    
    def output_exists(self, filename: str) -> bool:
        """Check if an output file exists."""
        return (self.output_dir / filename).exists()
    
    def delete_upload(self, filename: str) -> bool:
        """Delete an uploaded file."""
        file_path = self.upload_dir / filename
        if file_path.exists():
            file_path.unlink()
            logger.info("Upload deleted", path=str(file_path))
            return True
        return False
    
    def delete_output(self, filename: str) -> bool:
        """Delete an output file."""
        file_path = self.output_dir / filename
        if file_path.exists():
            file_path.unlink()
            logger.info("Output deleted", path=str(file_path))
            return True
        return False
    
    def copy_file(self, source: Path, destination: Path) -> Path:
        """Copy a file from source to destination."""
        shutil.copy2(source, destination)
        logger.info("File copied", source=str(source), destination=str(destination))
        return destination
    
    def get_output_url(self, filename: str) -> str:
        """Get the URL path for accessing an output file."""
        return f"/outputs/{filename}"


"""File and request validators."""

from pathlib import Path
from typing import Set

from fastapi import UploadFile

from app.config import Settings


# Magic bytes for image file type detection
IMAGE_SIGNATURES: dict[str, bytes] = {
    'jpg': b'\xff\xd8\xff',
    'jpeg': b'\xff\xd8\xff',
    'png': b'\x89PNG\r\n\x1a\n',
    'webp': b'RIFF',  # WebP files start with RIFF
}

# MIME types for images
ALLOWED_MIME_TYPES: Set[str] = {
    'image/jpeg',
    'image/png',
    'image/webp',
}


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower().lstrip('.')


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
    """Check if file extension is allowed."""
    ext = get_file_extension(filename)
    return ext in allowed_extensions


def validate_mime_type(content_type: str | None) -> bool:
    """Check if MIME type is allowed."""
    if content_type is None:
        return False
    return content_type.lower() in ALLOWED_MIME_TYPES


async def validate_file_signature(file: UploadFile) -> bool:
    """
    Validate file by checking magic bytes.
    
    This provides additional security by verifying the actual file content,
    not just the extension or MIME type which can be spoofed.
    """
    # Read first 12 bytes for signature check
    header = await file.read(12)
    await file.seek(0)  # Reset file pointer
    
    if len(header) < 3:
        return False
    
    # Check for JPEG
    if header[:3] == IMAGE_SIGNATURES['jpg']:
        return True
    
    # Check for PNG
    if header[:8] == IMAGE_SIGNATURES['png']:
        return True
    
    # Check for WebP (RIFF....WEBP)
    if header[:4] == IMAGE_SIGNATURES['webp'] and header[8:12] == b'WEBP':
        return True
    
    return False


async def get_file_size(file: UploadFile) -> int:
    """Get the size of an uploaded file in bytes."""
    # Seek to end
    await file.seek(0, 2)
    size = file.file.tell()
    # Reset to beginning
    await file.seek(0)
    return size


def validate_image_file(file: UploadFile, settings: Settings) -> None:
    """
    Validate an uploaded image file.
    
    Raises ValueError if validation fails.
    """
    # Check filename exists
    if not file.filename:
        raise ValueError("Filename is required")
    
    # Check extension
    if not validate_file_extension(file.filename, settings.allowed_extensions_list):
        allowed = ', '.join(settings.allowed_extensions_list)
        raise ValueError(f"File type not allowed. Allowed types: {allowed}")
    
    # Check MIME type
    if not validate_mime_type(file.content_type):
        raise ValueError(f"Invalid content type: {file.content_type}")


async def validate_image_file_async(file: UploadFile, settings: Settings) -> None:
    """
    Full async validation of an uploaded image file.
    
    Includes file signature validation and size check.
    Raises ValueError if validation fails.
    """
    # Basic validation first
    validate_image_file(file, settings)
    
    # Check file size
    size = await get_file_size(file)
    if size > settings.max_file_size_bytes:
        max_mb = settings.max_file_size_mb
        raise ValueError(f"File too large. Maximum size: {max_mb}MB")
    
    if size == 0:
        raise ValueError("File is empty")
    
    # Validate file signature (magic bytes)
    if not await validate_file_signature(file):
        raise ValueError("Invalid file content. File does not appear to be a valid image.")


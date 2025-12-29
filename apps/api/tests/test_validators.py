"""Tests for file validators."""

import io
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi import UploadFile

from app.services.validators import (
    get_file_extension,
    validate_file_extension,
    validate_mime_type,
    validate_image_file,
    ALLOWED_MIME_TYPES,
)


class TestGetFileExtension:
    """Tests for get_file_extension function."""
    
    def test_jpg_extension(self):
        assert get_file_extension("photo.jpg") == "jpg"
    
    def test_jpeg_extension(self):
        assert get_file_extension("photo.jpeg") == "jpeg"
    
    def test_png_extension(self):
        assert get_file_extension("image.png") == "png"
    
    def test_webp_extension(self):
        assert get_file_extension("image.webp") == "webp"
    
    def test_uppercase_extension(self):
        assert get_file_extension("PHOTO.JPG") == "jpg"
    
    def test_mixed_case_extension(self):
        assert get_file_extension("Photo.JpG") == "jpg"
    
    def test_no_extension(self):
        assert get_file_extension("filename") == ""
    
    def test_multiple_dots(self):
        assert get_file_extension("my.photo.image.png") == "png"
    
    def test_hidden_file(self):
        assert get_file_extension(".hidden") == "hidden"


class TestValidateFileExtension:
    """Tests for validate_file_extension function."""
    
    def test_valid_jpg(self):
        assert validate_file_extension("photo.jpg", ["jpg", "png"]) is True
    
    def test_valid_png(self):
        assert validate_file_extension("photo.png", ["jpg", "png"]) is True
    
    def test_invalid_gif(self):
        assert validate_file_extension("photo.gif", ["jpg", "png"]) is False
    
    def test_case_insensitive(self):
        assert validate_file_extension("photo.JPG", ["jpg", "png"]) is True
    
    def test_empty_allowed_list(self):
        assert validate_file_extension("photo.jpg", []) is False


class TestValidateMimeType:
    """Tests for validate_mime_type function."""
    
    def test_valid_jpeg_mime(self):
        assert validate_mime_type("image/jpeg") is True
    
    def test_valid_png_mime(self):
        assert validate_mime_type("image/png") is True
    
    def test_valid_webp_mime(self):
        assert validate_mime_type("image/webp") is True
    
    def test_invalid_gif_mime(self):
        assert validate_mime_type("image/gif") is False
    
    def test_invalid_text_mime(self):
        assert validate_mime_type("text/plain") is False
    
    def test_none_mime(self):
        assert validate_mime_type(None) is False
    
    def test_case_insensitive(self):
        assert validate_mime_type("IMAGE/JPEG") is True


class TestValidateImageFile:
    """Tests for validate_image_file function."""
    
    def create_mock_upload(
        self,
        filename: str = "test.jpg",
        content_type: str = "image/jpeg"
    ) -> UploadFile:
        """Create a mock UploadFile for testing."""
        file = MagicMock(spec=UploadFile)
        file.filename = filename
        file.content_type = content_type
        return file
    
    def create_mock_settings(self, extensions: list = None):
        """Create mock settings."""
        settings = MagicMock()
        settings.allowed_extensions_list = extensions or ["jpg", "jpeg", "png", "webp"]
        settings.max_file_size_bytes = 10 * 1024 * 1024
        settings.max_file_size_mb = 10
        return settings
    
    def test_valid_jpg_file(self):
        file = self.create_mock_upload("photo.jpg", "image/jpeg")
        settings = self.create_mock_settings()
        # Should not raise
        validate_image_file(file, settings)
    
    def test_valid_png_file(self):
        file = self.create_mock_upload("photo.png", "image/png")
        settings = self.create_mock_settings()
        validate_image_file(file, settings)
    
    def test_missing_filename(self):
        file = self.create_mock_upload(None, "image/jpeg")
        settings = self.create_mock_settings()
        with pytest.raises(ValueError, match="Filename is required"):
            validate_image_file(file, settings)
    
    def test_empty_filename(self):
        file = self.create_mock_upload("", "image/jpeg")
        settings = self.create_mock_settings()
        with pytest.raises(ValueError, match="Filename is required"):
            validate_image_file(file, settings)
    
    def test_invalid_extension(self):
        file = self.create_mock_upload("photo.gif", "image/gif")
        settings = self.create_mock_settings()
        with pytest.raises(ValueError, match="File type not allowed"):
            validate_image_file(file, settings)
    
    def test_invalid_mime_type(self):
        file = self.create_mock_upload("photo.jpg", "text/plain")
        settings = self.create_mock_settings()
        with pytest.raises(ValueError, match="Invalid content type"):
            validate_image_file(file, settings)


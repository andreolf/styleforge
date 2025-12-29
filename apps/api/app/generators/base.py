"""Base interface for image generators."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional

from app.models import StylePreset


class ImageGenerator(ABC):
    """
    Abstract base class for image generators.
    
    Implementations must provide the generate() method which takes an input
    image path and style preset, and returns the path to the generated output.
    """
    
    @abstractmethod
    def generate(
        self,
        input_path: Path,
        style: StylePreset,
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Path:
        """
        Generate a styled version of the input image.
        
        Args:
            input_path: Path to the input image file
            style: Style preset to apply
            output_path: Path where the output should be saved
            progress_callback: Optional callback function to report progress (0-100)
            
        Returns:
            Path to the generated output image
            
        Raises:
            GenerationError: If generation fails
        """
        pass
    
    def validate_input(self, input_path: Path) -> None:
        """Validate that the input file exists and is readable."""
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if not input_path.is_file():
            raise ValueError(f"Input path is not a file: {input_path}")
    
    def report_progress(
        self,
        progress: int,
        callback: Optional[Callable[[int], None]]
    ) -> None:
        """Report progress if callback is provided."""
        if callback:
            callback(min(max(progress, 0), 100))


class GenerationError(Exception):
    """Exception raised when image generation fails."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause


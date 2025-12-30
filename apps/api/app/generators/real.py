"""Real AI generator using Replicate API for style transfer with face preservation."""

import base64
import os
from pathlib import Path
from typing import Callable, Optional

import replicate
from PIL import Image

from app.generators.base import GenerationError, ImageGenerator
from app.models import StylePreset


class RealGenerator(ImageGenerator):
    """
    Real image generator using IP-Adapter FaceID SDXL for AI-powered style transfer.
    
    This model extracts face features from the input image and generates
    a new image with the same face but different clothing/style.
    """
    
    # Model: IP-Adapter FaceID SDXL - best for face preservation
    # Using model name only - Replicate will use latest version
    MODEL_ID = "lucataco/ip-adapter-faceid-sdxl"
    
    def __init__(self):
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError(
                "REPLICATE_API_TOKEN environment variable is required. "
                "Get your token at https://replicate.com/account/api-tokens"
            )
    
    def generate(
        self,
        input_path: Path,
        style: StylePreset,
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Path:
        """
        Generate a styled version of the input image using AI with face preservation.
        """
        try:
            self.validate_input(input_path)
            self.report_progress(10, progress_callback)
            
            # Read input image as data URI
            with open(input_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Detect image format
            with Image.open(input_path) as img:
                fmt = img.format.lower() if img.format else 'png'
                if fmt == 'jpeg':
                    fmt = 'jpg'
            
            image_uri = f"data:image/{fmt};base64,{image_data}"
            
            self.report_progress(20, progress_callback)
            
            # Build the prompt for style transfer
            prompt = self._build_prompt(style)
            
            self.report_progress(30, progress_callback)
            
            # Use IP-Adapter FaceID SDXL for face-preserving style transfer
            output = replicate.run(
                self.MODEL_ID,
                input={
                    "image": image_uri,
                    "prompt": prompt,
                    "negative_prompt": (
                        "blurry, bad quality, ugly, deformed, disfigured, "
                        "low quality, pixelated, bad anatomy, bad hands, "
                        "missing fingers, extra fingers, mutated, "
                        "cartoon, anime, illustration, painting, drawing, sketch"
                    ),
                    "num_outputs": 1,
                    "num_inference_steps": 30,
                    "guidance_scale": 6.0,
                    "ip_adapter_scale": 0.8,  # How much to preserve face (0-1)
                    "scheduler": "EulerDiscreteScheduler",
                }
            )
            
            self.report_progress(80, progress_callback)
            
            # Download and save the result
            if output:
                # Handle both old (list of URLs) and new (FileOutput) SDK formats
                if hasattr(output, '__iter__') and not isinstance(output, str):
                    result = list(output)[0] if output else None
                else:
                    result = output
                
                if result is None:
                    raise GenerationError("No output received from AI model")
                
                # Get URL string from FileOutput object or use directly if string
                result_url = str(result) if hasattr(result, 'url') else result
                if hasattr(result, 'url'):
                    result_url = result.url
                
                self._download_image(result_url, output_path)
            else:
                raise GenerationError("No output received from AI model")
            
            self.report_progress(100, progress_callback)
            
            return output_path
            
        except replicate.exceptions.ReplicateError as e:
            raise GenerationError(f"Replicate API error: {str(e)}", cause=e)
        except Exception as e:
            raise GenerationError(f"Generation failed: {str(e)}", cause=e)
    
    def _build_prompt(self, style: StylePreset) -> str:
        """Build the full prompt for generation."""
        base_prompt = (
            "professional portrait photo of a person, "
            "photorealistic, high quality, detailed, studio lighting, "
        )
        return base_prompt + style.prompt
    
    def _download_image(self, url_or_file, output_path: Path) -> None:
        """Download image from URL or FileOutput and save to path."""
        import httpx
        
        # Handle FileOutput object from newer replicate SDK
        if hasattr(url_or_file, 'read'):
            # It's a file-like object
            with open(output_path, 'wb') as f:
                f.write(url_or_file.read())
        else:
            # It's a URL string
            url = str(url_or_file)
            response = httpx.get(url, follow_redirects=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)

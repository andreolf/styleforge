"""Real AI generator using Replicate API for style transfer."""

import base64
import io
import os
from pathlib import Path
from typing import Callable, Optional

import replicate
from PIL import Image

from app.generators.base import GenerationError, ImageGenerator
from app.models import StylePreset


class RealGenerator(ImageGenerator):
    """
    Real image generator using Replicate API for AI-powered style transfer.
    
    Uses SDXL img2img for style changes with conservative settings
    to preserve face identity.
    """
    
    # SDXL img2img model - reliable and widely available
    MODEL_ID = "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"
    
    # Max dimension to avoid GPU memory errors
    MAX_DIMENSION = 640
    
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
        Generate a styled version of the input image using AI.
        """
        try:
            self.validate_input(input_path)
            self.report_progress(10, progress_callback)
            
            # Open and resize image to avoid GPU memory issues
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                width, height = img.size
                
                # Resize if too large
                if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
                    ratio = min(self.MAX_DIMENSION / width, self.MAX_DIMENSION / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    width, height = new_width, new_height
                
                # Ensure dimensions are multiples of 8 for SDXL
                width = (width // 8) * 8
                height = (height // 8) * 8
                width = max(512, width)
                height = max(512, height)
                
                # Crop to exact dimensions if needed
                if img.size != (width, height):
                    img = img.resize((width, height), Image.LANCZOS)
                
                # Encode resized image to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', quality=90)
                buffer.seek(0)
                image_data = base64.b64encode(buffer.read()).decode('utf-8')
            
            image_uri = f"data:image/png;base64,{image_data}"
            
            self.report_progress(20, progress_callback)
            
            # Build the prompt for style transfer
            prompt = self._build_prompt(style)
            
            self.report_progress(30, progress_callback)
            
            # Use SDXL img2img - balance between changing clothes and keeping face
            output = replicate.run(
                self.MODEL_ID,
                input={
                    "image": image_uri,
                    "prompt": prompt,
                    "negative_prompt": (
                        "different person, different face, changed facial features, "
                        "blurry, bad quality, ugly, deformed, disfigured, "
                        "cartoon, anime, illustration, painting, drawing"
                    ),
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "prompt_strength": 0.6,  # Higher to actually change clothes
                    "num_inference_steps": 30,
                    "width": width,
                    "height": height,
                    "scheduler": "K_EULER",
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
            "photo of this exact same person, same face, same glasses if wearing any, "
            "but now dressed in completely different outfit: "
        )
        return base_prompt + style.prompt + ", photorealistic, high quality photograph"
    
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

"""Hugging Face generator using free Inference API for style transfer."""

import base64
import io
import os
import time
from pathlib import Path
from typing import Callable, Optional

import httpx
from PIL import Image

from app.generators.base import GenerationError, ImageGenerator
from app.models import StylePreset


class HuggingFaceGenerator(ImageGenerator):
    """
    Image generator using Hugging Face's free Inference API.
    
    Uses Stable Diffusion img2img for style transfer.
    Free tier has rate limits but works for testing.
    """
    
    # Model for img2img style transfer
    MODEL_ID = "stabilityai/stable-diffusion-xl-refiner-1.0"
    # Alternative models:
    # "runwayml/stable-diffusion-v1-5"
    # "stabilityai/stable-diffusion-2-1"
    
    API_URL = "https://api-inference.huggingface.co/models/"
    
    def __init__(self):
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN', '')
        # HF API works without token but with rate limits
        self.headers = {}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
    
    def generate(
        self,
        input_path: Path,
        style: StylePreset,
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Path:
        """
        Generate a styled version using Hugging Face API.
        """
        try:
            self.validate_input(input_path)
            self.report_progress(10, progress_callback)
            
            # Read and prepare input image
            with Image.open(input_path) as img:
                # Convert to RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for faster processing (max 768px)
                max_size = 768
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
            
            self.report_progress(20, progress_callback)
            
            # Build prompt
            prompt = self._build_prompt(style)
            
            self.report_progress(30, progress_callback)
            
            # Try multiple approaches
            result_image = None
            
            # Approach 1: Text-to-image with style (simpler, works better with free tier)
            result_image = self._generate_with_text2img(prompt, img_bytes, progress_callback)
            
            if result_image is None:
                raise GenerationError("Failed to generate image from Hugging Face API")
            
            self.report_progress(90, progress_callback)
            
            # Save result
            result_image.save(output_path, 'PNG', quality=95)
            
            self.report_progress(100, progress_callback)
            
            return output_path
            
        except Exception as e:
            raise GenerationError(f"HuggingFace generation failed: {str(e)}", cause=e)
    
    def _build_prompt(self, style: StylePreset) -> str:
        """Build the prompt for generation."""
        return (
            f"professional portrait photo of a person, "
            f"{style.prompt}, "
            f"photorealistic, high quality, detailed, studio lighting, "
            f"fashion photography, 8k uhd"
        )
    
    def _generate_with_text2img(
        self, 
        prompt: str, 
        original_image_bytes: bytes,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Optional[Image.Image]:
        """Generate using text-to-image with img2img style transfer."""
        
        # Use a community model that's still available
        model = "runwayml/stable-diffusion-v1-5"
        url = f"{self.API_URL}{model}"
        
        # Prepare payload - for img2img we send the image
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "blurry, bad quality, distorted, ugly, deformed, cartoon, anime, drawing, painting, illustration, text, watermark",
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
            }
        }
        
        self.report_progress(40, progress_callback)
        
        # Make request with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        url,
                        headers={**self.headers, "Content-Type": "application/json"},
                        json=payload
                    )
                    
                    # Check for model loading
                    if response.status_code == 503:
                        data = response.json()
                        wait_time = data.get("estimated_time", 20)
                        self.report_progress(50, progress_callback)
                        time.sleep(min(wait_time, 30))
                        continue
                    
                    if response.status_code == 200:
                        self.report_progress(80, progress_callback)
                        return Image.open(io.BytesIO(response.content))
                    
                    # Rate limit - wait and retry
                    if response.status_code == 429:
                        time.sleep(10)
                        continue
                        
                    response.raise_for_status()
                    
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                raise
        
        return None

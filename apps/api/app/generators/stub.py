"""Stub generator for local testing - applies visual style effects."""

import time
from pathlib import Path
from typing import Callable, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

from app.generators.base import GenerationError, ImageGenerator
from app.models import StylePreset


# Style-specific color overlays and effects
STYLE_EFFECTS = {
    'classic-tuxedo': {
        'overlay_color': (20, 20, 30),
        'overlay_opacity': 0.15,
        'contrast': 1.2,
        'saturation': 0.8,
        'label_color': (255, 215, 0),  # Gold
    },
    'streetwear': {
        'overlay_color': (255, 100, 50),
        'overlay_opacity': 0.1,
        'contrast': 1.15,
        'saturation': 1.3,
        'label_color': (255, 100, 50),  # Orange
    },
    'techwear': {
        'overlay_color': (30, 30, 35),
        'overlay_opacity': 0.2,
        'contrast': 1.3,
        'saturation': 0.7,
        'label_color': (100, 200, 255),  # Cyan
    },
    'old-money': {
        'overlay_color': (180, 150, 100),
        'overlay_opacity': 0.1,
        'contrast': 1.1,
        'saturation': 0.9,
        'label_color': (180, 150, 100),  # Warm brown
    },
    'minimalist': {
        'overlay_color': (200, 200, 200),
        'overlay_opacity': 0.15,
        'contrast': 1.1,
        'saturation': 0.5,
        'label_color': (150, 150, 150),  # Gray
    },
    'cyberpunk': {
        'overlay_color': (255, 0, 150),
        'overlay_opacity': 0.15,
        'contrast': 1.4,
        'saturation': 1.5,
        'label_color': (255, 0, 255),  # Magenta
    },
    'crypto-bro': {
        'overlay_color': (0, 200, 100),
        'overlay_opacity': 0.1,
        'contrast': 1.2,
        'saturation': 1.1,
        'label_color': (0, 255, 100),  # Green
    },
}

DEFAULT_EFFECT = {
    'overlay_color': (128, 0, 255),
    'overlay_opacity': 0.1,
    'contrast': 1.1,
    'saturation': 1.0,
    'label_color': (128, 0, 255),
}


class StubGenerator(ImageGenerator):
    """
    Stub image generator for testing without AI services.
    
    Applies visual effects (color grading, contrast) to simulate style changes
    and adds a label showing the applied style.
    """
    
    def __init__(self, simulate_delay: bool = True, delay_seconds: float = 3.0):
        self.simulate_delay = simulate_delay
        self.delay_seconds = delay_seconds
    
    def generate(
        self,
        input_path: Path,
        style: StylePreset,
        output_path: Path,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Path:
        try:
            self.validate_input(input_path)
            self.report_progress(10, progress_callback)
            
            # Get style effects
            effects = STYLE_EFFECTS.get(style.id, DEFAULT_EFFECT)
            
            # Open and process image
            with Image.open(input_path) as img:
                # Convert to RGB
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                self.report_progress(20, progress_callback)
                
                # Simulate processing time
                if self.simulate_delay:
                    steps = 5
                    step_delay = self.delay_seconds / steps
                    for i in range(steps):
                        time.sleep(step_delay)
                        progress = 20 + int((i + 1) / steps * 50)
                        self.report_progress(progress, progress_callback)
                
                # Apply color grading
                img = self._apply_color_overlay(img, effects['overlay_color'], effects['overlay_opacity'])
                self.report_progress(75, progress_callback)
                
                # Adjust contrast
                if effects['contrast'] != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(effects['contrast'])
                
                # Adjust saturation
                if effects['saturation'] != 1.0:
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(effects['saturation'])
                
                self.report_progress(85, progress_callback)
                
                # Add style label
                img = self._add_style_label(img, style.name, effects['label_color'])
                
                self.report_progress(95, progress_callback)
                
                # Save output
                img.save(output_path, 'PNG', quality=95)
                
                self.report_progress(100, progress_callback)
                
                return output_path
                
        except Exception as e:
            raise GenerationError(f"Stub generation failed: {str(e)}", cause=e)
    
    def _apply_color_overlay(
        self, 
        img: Image.Image, 
        color: Tuple[int, int, int], 
        opacity: float
    ) -> Image.Image:
        """Apply a color overlay to the image."""
        overlay = Image.new('RGB', img.size, color)
        return Image.blend(img, overlay, opacity)
    
    def _add_style_label(
        self, 
        img: Image.Image, 
        style_name: str,
        label_color: Tuple[int, int, int]
    ) -> Image.Image:
        """Add a style label to the image."""
        img = img.convert('RGBA')
        width, height = img.size
        
        # Create overlay for label
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load font
        font_size = max(24, min(48, width // 15))
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except (IOError, OSError):
                font = ImageFont.load_default()
        
        # Label text
        label_text = f"✨ {style_name}"
        
        # Get text size
        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at bottom center
        padding = 15
        x = (width - text_width) // 2
        y = height - text_height - padding - 20
        
        # Draw background pill
        pill_padding = 12
        pill_box = [
            x - pill_padding,
            y - pill_padding // 2,
            x + text_width + pill_padding,
            y + text_height + pill_padding // 2
        ]
        draw.rounded_rectangle(pill_box, radius=20, fill=(0, 0, 0, 200))
        
        # Draw text
        draw.text((x, y), label_text, font=font, fill=(*label_color, 255))
        
        # Composite
        img = Image.alpha_composite(img, overlay)
        return img.convert('RGB')


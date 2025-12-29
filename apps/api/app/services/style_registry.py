"""Style preset registry - central place to define all available styles."""

from functools import lru_cache
from typing import Dict, List, Optional

from app.models import StylePreset


class StyleRegistry:
    """Registry of available style presets."""
    
    def __init__(self):
        self._styles: Dict[str, StylePreset] = {}
        self._register_default_styles()
    
    def _register_default_styles(self) -> None:
        """Register all default style presets."""
        
        # Classic Tuxedo - Elegant spy archetype
        self.register(StylePreset(
            id="classic-tuxedo",
            name="Classic Tuxedo",
            description="Elegant spy archetype in formal evening wear with sophistication",
            prompt="wearing an elegant black tuxedo with white dress shirt and black bow tie, sophisticated spy aesthetic, formal evening wear, sleek and polished appearance",
            thumbnail="/thumbnails/classic-tuxedo.jpg"
        ))
        
        # Modern Streetwear
        self.register(StylePreset(
            id="streetwear",
            name="Modern Streetwear",
            description="Urban fashion with hoodies, sneakers, and contemporary street style",
            prompt="wearing modern streetwear fashion, oversized hoodie, designer sneakers, urban style, contemporary street fashion, casual cool aesthetic",
            thumbnail="/thumbnails/streetwear.jpg"
        ))
        
        # Techwear
        self.register(StylePreset(
            id="techwear",
            name="Techwear",
            description="Functional futuristic clothing with utility and tech aesthetics",
            prompt="wearing techwear fashion, functional futuristic clothing, utility vest, cargo pants with straps, technical fabrics, dark monochrome palette, cyberpunk influenced",
            thumbnail="/thumbnails/techwear.jpg"
        ))
        
        # Old Money
        self.register(StylePreset(
            id="old-money",
            name="Old Money",
            description="Refined preppy aesthetic with timeless elegance",
            prompt="wearing old money style clothing, cashmere sweater draped over shoulders, oxford shirt, tailored chinos, loafers, preppy refined aesthetic, understated luxury",
            thumbnail="/thumbnails/old-money.jpg"
        ))
        
        # Minimalist
        self.register(StylePreset(
            id="minimalist",
            name="Minimalist",
            description="Clean, simple, monochrome looks with focus on quality basics",
            prompt="wearing minimalist fashion, clean simple clothing, monochrome palette, quality basics, neutral tones, scandinavian inspired, understated elegance",
            thumbnail="/thumbnails/minimalist.jpg"
        ))
        
        # Cyberpunk
        self.register(StylePreset(
            id="cyberpunk",
            name="Cyberpunk",
            description="Neon-accented futuristic fashion with bold tech elements",
            prompt="wearing cyberpunk fashion, neon accented clothing, futuristic tech accessories, LED elements, dark base with bright accent colors, dystopian future aesthetic",
            thumbnail="/thumbnails/cyberpunk.jpg"
        ))
        
        # Crypto Bro
        self.register(StylePreset(
            id="crypto-bro",
            name="Crypto Bro",
            description="Tech founder vibes with hoodies, Patagonia vests, and startup energy",
            prompt="wearing tech startup fashion, grey or black hoodie under Patagonia vest, AirPods, casual expensive sneakers, Apple Watch, confident Silicon Valley tech bro aesthetic, venture capital energy",
            thumbnail="/thumbnails/crypto-bro.jpg"
        ))
    
    def register(self, style: StylePreset) -> None:
        """Register a new style preset."""
        self._styles[style.id] = style
    
    def get_style(self, style_id: str) -> Optional[StylePreset]:
        """Get a style preset by ID."""
        return self._styles.get(style_id)
    
    def get_all_styles(self) -> List[StylePreset]:
        """Get all registered style presets."""
        return list(self._styles.values())
    
    def style_exists(self, style_id: str) -> bool:
        """Check if a style ID exists."""
        return style_id in self._styles
    
    def get_style_ids(self) -> List[str]:
        """Get list of all style IDs."""
        return list(self._styles.keys())


@lru_cache
def get_style_registry() -> StyleRegistry:
    """Get cached style registry instance."""
    return StyleRegistry()


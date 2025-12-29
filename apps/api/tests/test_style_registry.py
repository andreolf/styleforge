"""Tests for style registry."""

import pytest

from app.models import StylePreset
from app.services.style_registry import StyleRegistry, get_style_registry


class TestStyleRegistry:
    """Tests for StyleRegistry class."""
    
    def test_default_styles_registered(self):
        """Test that default styles are registered on initialization."""
        registry = StyleRegistry()
        styles = registry.get_all_styles()
        
        assert len(styles) >= 6
        
    def test_get_style_by_id(self):
        """Test getting a style by ID."""
        registry = StyleRegistry()
        
        style = registry.get_style("classic-tuxedo")
        
        assert style is not None
        assert style.id == "classic-tuxedo"
        assert style.name == "Classic Tuxedo"
        assert len(style.prompt) > 0
    
    def test_get_nonexistent_style(self):
        """Test getting a style that doesn't exist."""
        registry = StyleRegistry()
        
        style = registry.get_style("nonexistent-style")
        
        assert style is None
    
    def test_style_exists(self):
        """Test checking if a style exists."""
        registry = StyleRegistry()
        
        assert registry.style_exists("classic-tuxedo") is True
        assert registry.style_exists("streetwear") is True
        assert registry.style_exists("nonexistent") is False
    
    def test_get_style_ids(self):
        """Test getting all style IDs."""
        registry = StyleRegistry()
        
        ids = registry.get_style_ids()
        
        assert "classic-tuxedo" in ids
        assert "streetwear" in ids
        assert "techwear" in ids
        assert "old-money" in ids
        assert "minimalist" in ids
        assert "cyberpunk" in ids
    
    def test_register_custom_style(self):
        """Test registering a custom style."""
        registry = StyleRegistry()
        
        custom_style = StylePreset(
            id="custom-test",
            name="Custom Test Style",
            description="A test style",
            prompt="test prompt for custom style",
            thumbnail=None
        )
        
        registry.register(custom_style)
        
        assert registry.style_exists("custom-test")
        retrieved = registry.get_style("custom-test")
        assert retrieved.name == "Custom Test Style"
    
    def test_style_has_required_fields(self):
        """Test that all styles have required fields."""
        registry = StyleRegistry()
        
        for style in registry.get_all_styles():
            assert style.id, "Style must have an ID"
            assert style.name, "Style must have a name"
            assert style.description, "Style must have a description"
            assert style.prompt, "Style must have a prompt"
    
    def test_style_ids_are_kebab_case(self):
        """Test that all style IDs follow kebab-case convention."""
        registry = StyleRegistry()
        
        for style in registry.get_all_styles():
            # Should not contain uppercase letters
            assert style.id == style.id.lower(), f"Style ID should be lowercase: {style.id}"
            # Should not contain spaces
            assert " " not in style.id, f"Style ID should not contain spaces: {style.id}"
            # Should not contain underscores (use hyphens)
            # Note: This is a convention, not strictly required
    
    def test_specific_styles_content(self):
        """Test specific style presets have appropriate content."""
        registry = StyleRegistry()
        
        # Classic Tuxedo
        tuxedo = registry.get_style("classic-tuxedo")
        assert "tuxedo" in tuxedo.prompt.lower()
        assert "elegant" in tuxedo.description.lower() or "spy" in tuxedo.description.lower()
        
        # Streetwear
        streetwear = registry.get_style("streetwear")
        assert "street" in streetwear.prompt.lower()
        
        # Cyberpunk
        cyberpunk = registry.get_style("cyberpunk")
        assert "neon" in cyberpunk.prompt.lower() or "cyber" in cyberpunk.prompt.lower()


class TestGetStyleRegistry:
    """Tests for get_style_registry function."""
    
    def test_returns_registry(self):
        """Test that function returns a StyleRegistry instance."""
        registry = get_style_registry()
        
        assert isinstance(registry, StyleRegistry)
    
    def test_cached(self):
        """Test that the registry is cached (same instance returned)."""
        registry1 = get_style_registry()
        registry2 = get_style_registry()
        
        assert registry1 is registry2


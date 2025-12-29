"""Style presets API routes."""

from fastapi import APIRouter

from app.models import StyleListResponse
from app.services.style_registry import get_style_registry

router = APIRouter()


@router.get("/styles", response_model=StyleListResponse)
async def list_styles():
    """
    Get all available style presets.
    
    Returns a list of style presets that can be used for image transformation.
    Each style includes an ID, name, description, and optional thumbnail.
    """
    registry = get_style_registry()
    styles = registry.get_all_styles()
    
    return StyleListResponse(
        styles=styles,
        count=len(styles)
    )


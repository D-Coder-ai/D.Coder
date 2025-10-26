"""
LLM Provider Configuration Endpoints
"""

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def list_providers():
    """List configured LLM providers - TODO: Implement"""
    return {
        "providers": [
            {"name": "openai", "enabled": False},
            {"name": "anthropic", "enabled": False},
            {"name": "google", "enabled": False},
            {"name": "groq", "enabled": False}
        ]
    }


@router.put("/{provider}", status_code=status.HTTP_200_OK)
async def configure_provider(provider: str):
    """Configure LLM provider - TODO: Implement"""
    return {"provider": provider, "message": "Configuration - To be implemented"}


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_provider(provider: str):
    """Remove provider configuration - TODO: Implement"""
    return None


@router.post("/{provider}/test", status_code=status.HTTP_200_OK)
async def test_provider(provider: str):
    """Test provider connection - TODO: Implement"""
    return {"provider": provider, "status": "pending", "message": "Test - To be implemented"}
import logging
from typing import Optional
from app.services.ai_generator.base import BaseAIProvider
from app.services.ai_generator.mock_provider import MockAIProvider
from app.services.ai_generator.gemini_provider import GeminiAIProvider
from app.core.config import settings

logger = logging.getLogger("civic_ai.ai_factory")

def get_ai_provider(provider_override: Optional[str] = None) -> BaseAIProvider:
    """
    Factory to retrieve configured AI Provider.
    Supports 'gemini' and 'mock'. Defaults to 'mock' if no Gemini API key.
    """
    selected = provider_override or settings.AI_PROVIDER or "mock"
    selected = selected.lower().strip()

    if selected == "gemini":
        if settings.GEMINI_API_KEY:
            logger.info("Instantiating GeminiAIProvider with configured API key.")
            return GeminiAIProvider()
        else:
            logger.warning("AI_PROVIDER is 'gemini' but GEMINI_API_KEY is empty. Using MockAIProvider.")
            return MockAIProvider()

    return MockAIProvider()

__all__ = ["BaseAIProvider", "MockAIProvider", "GeminiAIProvider", "get_ai_provider"]

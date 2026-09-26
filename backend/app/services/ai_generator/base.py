from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAIProvider(ABC):
    """
    Abstract Base Class for AI Test Generation Providers.
    Supports pluggable LLMs (Gemini, Mock, etc.)
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider, e.g. 'mock', 'gemini'"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier used, e.g. 'gemini-1.5-pro', 'rule-based-mock'"""
        pass

    @abstractmethod
    def generate_test_cases(
        self,
        context: Dict[str, Any],
        categories: List[str],
        tests_per_requirement: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate structured test cases from the provided context.
        Must return list of dictionaries compliant with TestCase definition.
        """
        pass

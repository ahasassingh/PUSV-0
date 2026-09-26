import json
import logging
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error
from app.services.ai_generator.base import BaseAIProvider
from app.services.ai_generator.mock_provider import MockAIProvider
from app.core.config import settings

logger = logging.getLogger("civic_ai.gemini_provider")

SYSTEM_PROMPT = """You are an automotive software verification engineer for the CIVIC-AI platform.
Generate structured test cases from the supplied normalized requirement and controlled vehicle architecture context.

You must strictly obey these engineering principles:
1. Preserve requirement intent.
2. NEVER invent safety-critical thresholds (braking pressure, yaw rate, speed limits, etc.).
3. NEVER invent timing constraints (detection timeouts, diagnostic response times, etc.).
4. NEVER invent ECU relationships or sensor names not provided in context.
5. NEVER invent expected numerical values unless explicitly present in the requirement or architecture.
6. Preserve specification gaps (e.g. MISSING_TIMEOUT, MISSING_THRESHOLD, AMBIGUOUS_BOUNDARY).
7. Reference the source requirement accurately.
8. Produce deterministic JSON matching the supplied schema.
9. Clearly identify assumptions in the assumptions field.
10. NEVER claim that a test has been executed.
11. NEVER report PASS or FAIL execution results (execution is out of scope).
12. If the requirement is incomplete, produce a reviewable test with the relevant specification gap and set validation_status to "REQUIRES_REVIEW" instead of fabricating missing information.

Format output as a valid JSON object with a single key "test_cases" containing an array of test cases:
{
  "test_cases": [
    {
      "test_id": "TC-AI-<REQ_CODE>-<CAT>-001",
      "title": "Clear descriptive title",
      "requirement_ids": ["<REQ_CODE>"],
      "category": "FUNCTIONAL | BOUNDARY | NEGATIVE | FAULT_INJECTION | TIMING | INTEGRATION",
      "priority": "P0 | P1 | P2",
      "ecu_under_test": ["ECU_NAME"],
      "dependencies": [],
      "preconditions": ["..."],
      "input_signals": [],
      "steps": ["Step 1", "Step 2"],
      "expected_results": ["Expected Result 1"],
      "fault_injection": [],
      "recovery_conditions": [],
      "pass_fail_criteria": ["Definitive criteria"],
      "safety_notes": "...",
      "assumptions": [],
      "specification_gaps": [],
      "generation_status": "GENERATED",
      "validation_status": "VALID | REQUIRES_REVIEW",
      "generation_provider": "gemini",
      "traceability": {
        "requirement_id": "<REQ_CODE>",
        "source_document": "...",
        "source_page": 1,
        "source_section": "..."
      }
    }
  ]
}
"""

class GeminiAIProvider(BaseAIProvider):
    """
    Google Gemini AI Provider for generating structured automotive test cases.
    Falls back gracefully to MockAIProvider if GEMINI_API_KEY is not configured.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-1.5-pro"
        self._fallback_provider = MockAIProvider()

    @property
    def provider_name(self) -> str:
        return "gemini" if self.api_key else "mock"

    @property
    def model_name(self) -> str:
        return self.model if self.api_key else self._fallback_provider.model_name

    def generate_test_cases(
        self,
        context: Dict[str, Any],
        categories: List[str],
        tests_per_requirement: int = 3
    ) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.info("GEMINI_API_KEY not set. Falling back to deterministic MockAIProvider.")
            return self._fallback_provider.generate_test_cases(context, categories, tests_per_requirement)

        prompt_payload = {
            "context": context,
            "requested_categories": categories,
            "tests_per_requirement": tests_per_requirement
        }

        user_content = f"Generate automotive test cases for the following context:\n{json.dumps(prompt_payload, indent=2)}"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_content}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(request_body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned no candidates. Falling back to mock provider.")
                return self._fallback_provider.generate_test_cases(context, categories, tests_per_requirement)

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
            parsed = json.loads(raw_text)

            test_cases = parsed.get("test_cases", [])
            for tc in test_cases:
                tc["generation_provider"] = "gemini"
                tc["generation_model"] = self.model

            return test_cases

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}. Falling back to deterministic mock provider.")
            return self._fallback_provider.generate_test_cases(context, categories, tests_per_requirement)

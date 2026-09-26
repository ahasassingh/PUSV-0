import logging
from typing import List, Dict, Any
from app.services.ai_generator.base import BaseAIProvider

logger = logging.getLogger("civic_ai.mock_provider")

class MockAIProvider(BaseAIProvider):
    """
    Deterministic rule-based Mock AI Provider for offline testing and fallback.
    Identifies generated results with provider="mock".
    Strictly complies with the zero-hallucination rule:
    - Never fabricates safety-critical thresholds.
    - Never invents timing constraints (if missing, records null and preserves MISSING_TIMEOUT).
    - Preserves specification gaps and flags REQUIRES_REVIEW.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "rule-based-mock-engine"

    def generate_test_cases(
        self,
        context: Dict[str, Any],
        categories: List[str],
        tests_per_requirement: int = 3
    ) -> List[Dict[str, Any]]:
        req = context.get("requirement", {})
        req_code = req.get("req_code", "UNKNOWN-REQ")
        req_id = req.get("id", req_code)
        system = req.get("system", "General")
        subsystem = req.get("subsystem") or system
        text = req.get("original_text", "")
        timing = req.get("timing_constraint")
        threshold = req.get("threshold")
        spec_gaps = list(req.get("specification_gaps", []))
        arch = context.get("architecture", {})
        ecus = arch.get("ecus", ["BRAKE_ECU" if "BRK" in req_code else "BODY_CONTROL_ECU"])
        if not ecus:
            ecus = ["UNKNOWN_ECU"]
        primary_ecu = ecus[0]

        traceability = req.get("traceability", {
            "requirement_id": req_code,
            "source_document": "seeded_specification",
            "source_page": 1,
            "source_section": system
        })

        # Check for ambiguity in requirement text without threshold or timing
        text_lower = text.lower()
        if "maintain vehicle stability" in text_lower or ("stability" in text_lower and not threshold):
            if "AMBIGUOUS_BOUNDARY" not in spec_gaps:
                spec_gaps.append("AMBIGUOUS_BOUNDARY")

        if ("detect" in text_lower or "sensor failure" in text_lower) and not timing:
            if "MISSING_TIMEOUT" not in spec_gaps:
                spec_gaps.append("MISSING_TIMEOUT")

        # Determine validation status
        validation_status = "REQUIRES_REVIEW" if spec_gaps else "VALID"

        tests = []
        target_categories = [c for c in categories if c in [
            "FUNCTIONAL", "BOUNDARY", "NEGATIVE", "FAULT_INJECTION", "TIMING", "INTEGRATION"
        ]]
        if not target_categories:
            target_categories = ["FUNCTIONAL", "BOUNDARY", "FAULT_INJECTION"]

        seq = 1

        for cat in target_categories:
            if len(tests) >= tests_per_requirement:
                break

            test_id = f"TC-AI-{req_code}-{cat[:3]}-{seq:03d}"
            seq += 1

            preconditions = [
                "Vehicle ignition state is ON",
                f"{primary_ecu} is in operational state",
                "PUSV-01 CAN communication network is active"
            ]

            steps = []
            expected_results = []
            pass_fail_criteria = []
            fault_injection = []
            recovery_conditions = []
            assumptions = []

            if cat == "FUNCTIONAL":
                title = f"Nominal Verification: {req_code} ({system})"
                steps = [
                    f"Set nominal vehicle operating conditions for {subsystem}",
                    f"Trigger requirement condition: {text}",
                    f"Observe response of {primary_ecu} via vehicle bus"
                ]
                if threshold:
                    expected_results = [
                        f"{primary_ecu} maintains behavior within verified threshold: {threshold}"
                    ]
                    pass_fail_criteria = [
                        f"System complies with requirement {req_code} adhering to threshold {threshold}."
                    ]
                else:
                    expected_results = [
                        f"{primary_ecu} activates requested function according to {req_code}"
                    ]
                    pass_fail_criteria = [
                        f"System behavior matches defined specification for {req_code} under nominal conditions."
                    ]

            elif cat == "FAULT_INJECTION":
                title = f"Fault Injection: {req_code} ({system})"
                fault_name = "wheel-speed sensor failure" if "wheel-speed" in text_lower or "sensor" in text_lower else f"{system} sensor disconnect"
                fault_injection = [fault_name]
                steps = [
                    "Establish steady state operating conditions",
                    f"Inject fault: '{fault_name}' via simulation harness",
                    f"Monitor {primary_ecu} diagnostic and mitigation response"
                ]
                if timing:
                    expected_results = [
                        f"{fault_name} is detected by {primary_ecu} within {timing}",
                        "Appropriate diagnostic flag is raised on CAN bus"
                    ]
                    pass_fail_criteria = [
                        f"Diagnostic detection of '{fault_name}' occurs within {timing}."
                    ]
                else:
                    expected_results = [
                        f"{fault_name} is detected by {primary_ecu} according to requirement {req_code}",
                        "Specification gap note: detection timeout is not numerically specified"
                    ]
                    pass_fail_criteria = [
                        f"Detection occurs per requirement {req_code}. Engineering review required to specify exact timeout threshold."
                    ]

            elif cat == "TIMING":
                title = f"Timing Verification: {req_code} ({system})"
                if timing:
                    steps = [
                        f"Initiate stimuli relevant to {req_code}",
                        f"Measure response latency of {primary_ecu} using bus timestamping",
                        f"Verify latency against defined constraint: {timing}"
                    ]
                    expected_results = [
                        f"Total execution/response latency is <= {timing}"
                    ]
                    pass_fail_criteria = [
                        f"System reaction time strictly meets the requirement constraint: {timing}."
                    ]
                else:
                    steps = [
                        f"Initiate stimuli for {req_code}",
                        f"Measure baseline response latency of {primary_ecu}",
                        "Flag unconstrained timing to safety engineering"
                    ]
                    expected_results = [
                        "Latency measured for engineering review. No requirement timeout defined."
                    ]
                    pass_fail_criteria = [
                        "Requirement does not define timing constraint (MISSING_TIMEOUT). Review required."
                    ]

            elif cat == "BOUNDARY":
                title = f"Boundary Analysis: {req_code} ({system})"
                if threshold:
                    steps = [
                        f"Apply input stimuli at threshold boundary: {threshold} - margin",
                        f"Apply input stimuli at exact threshold: {threshold}",
                        f"Apply input stimuli at threshold + margin: {threshold} + margin",
                        f"Verify {primary_ecu} switching behavior at boundary"
                    ]
                    expected_results = [
                        f"Controller switches state accurately around threshold: {threshold}"
                    ]
                    pass_fail_criteria = [
                        f"Boundary transition verified around specified threshold: {threshold}."
                    ]
                else:
                    steps = [
                        f"Evaluate operational range for {req_code}",
                        "Record lack of numerical boundary in requirement specification"
                    ]
                    expected_results = [
                        "Boundary cannot be numerically evaluated because threshold is undefined."
                    ]
                    pass_fail_criteria = [
                        "Requirement boundary is ambiguous (AMBIGUOUS_BOUNDARY / MISSING_THRESHOLD). Engineering review required."
                    ]

            elif cat == "NEGATIVE":
                title = f"Negative Testing: {req_code} ({system})"
                steps = [
                    f"Present invalid or out-of-order input condition to {primary_ecu}",
                    f"Verify system rejects invalid condition without unintended actuation",
                    f"Verify safety state of {subsystem} is maintained"
                ]
                expected_results = [
                    f"{primary_ecu} rejects invalid stimuli and maintains safe default state"
                ]
                pass_fail_criteria = [
                    f"No improper actuation occurs for {req_code} under invalid input states."
                ]

            elif cat == "INTEGRATION":
                other_ecus = [e for e in ecus if e != primary_ecu]
                secondary_ecu = other_ecus[0] if other_ecus else "CENTRAL_GATEWAY_ECU"
                title = f"Inter-ECU Integration: {primary_ecu} <-> {secondary_ecu}"
                steps = [
                    f"Establish communication between {primary_ecu} and {secondary_ecu}",
                    f"Stimulate requirement condition on {primary_ecu}",
                    f"Verify relevant signal propagation to {secondary_ecu} over CAN-FD bus"
                ]
                expected_results = [
                    f"Signal exchange between {primary_ecu} and {secondary_ecu} is consistent and error-free"
                ]
                pass_fail_criteria = [
                    f"Cross-ECU message exchange for {req_code} maintains bus synchronization and payload integrity."
                ]

            tests.append({
                "test_id": test_id,
                "title": title,
                "requirement_ids": [req_code],
                "category": cat,
                "priority": "P0" if req.get("safety_relevance") in ["ASIL-D", "ASIL-C"] else "P1",
                "ecu_under_test": ecus,
                "dependencies": req.get("dependencies", []),
                "preconditions": preconditions,
                "input_signals": [s["name"] for s in arch.get("signals", [])[:3]],
                "steps": steps,
                "expected_results": expected_results,
                "fault_injection": fault_injection,
                "recovery_conditions": recovery_conditions,
                "pass_fail_criteria": pass_fail_criteria,
                "safety_notes": f"Safety relevance: {req.get('safety_relevance', 'QM')}. Vehicle: PUSV-01.",
                "assumptions": assumptions,
                "specification_gaps": spec_gaps,
                "generation_status": "GENERATED",
                "validation_status": validation_status,
                "generation_provider": self.provider_name,
                "generation_model": self.model_name,
                "traceability": traceability
            })

        return tests

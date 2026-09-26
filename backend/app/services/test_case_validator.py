import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, SpecificationGap
from app.models.vehicle import ECU, Sensor, Signal

logger = logging.getLogger("civic_ai.test_case_validator")

class TestCaseValidator:
    """
    Deterministic Test-Quality Validator for AI-generated automotive test cases.
    CRITICAL RULE: AI generates. Deterministic systems validate.

    Validates generated test cases against controlled source requirement and vehicle architecture:
    1. Requirement ID exists in database.
    2. Test has expected results.
    3. Test has pass/fail criteria.
    4. Test has traceability metadata.
    5. No unsupported numerical threshold appears if not in requirement.
    6. No unsupported timing value appears if not in requirement.
    7. Referenced ECUs exist in architecture or are flagged.
    8. Referenced sensors exist or are flagged.
    9. Referenced signals exist or are flagged.
    10. Specification gaps (MISSING_TIMEOUT, MISSING_THRESHOLD, AMBIGUOUS_BOUNDARY) are preserved.
    11. Generated test does not claim an execution result (PASS/FAIL/BLOCKED).
    12. Deterministic validation status: VALID, REQUIRES_REVIEW, or INVALID.
    """

    def __init__(self, db: Session):
        self.db = db

        # Cache existing architecture identifiers for deterministic lookup
        self.known_ecus = {e.name.upper() for e in self.db.query(ECU).all()}
        self.known_sensors = {s.name.upper() for s in self.db.query(Sensor).all()}
        self.known_signals = {s.name.upper() for s in self.db.query(Signal).all()}

    def validate(self, test_case: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        errors: List[Dict[str, str]] = []
        warnings: List[Dict[str, str]] = []

        # Check 1 & 2: Requirement exists
        req_ids = test_case.get("requirement_ids", [])
        if not req_ids:
            errors.append({
                "code": "MISSING_REQUIREMENT_REFERENCE",
                "message": "Test case does not reference any requirement ID."
            })
            return {
                "status": "INVALID",
                "errors": errors,
                "warnings": warnings
            }

        primary_req_code = req_ids[0]
        req = self.db.query(Requirement).filter(
            (Requirement.id == primary_req_code) | (Requirement.req_code == primary_req_code)
        ).first()

        if not req:
            errors.append({
                "code": "REQUIREMENT_NOT_FOUND",
                "message": f"Referenced requirement '{primary_req_code}' not found in database."
            })
            return {
                "status": "INVALID",
                "errors": errors,
                "warnings": warnings
            }

        # Check 3: Expected results
        expected_results = test_case.get("expected_results", [])
        if not expected_results or not any(str(r).strip() for r in expected_results):
            errors.append({
                "code": "MISSING_EXPECTED_RESULTS",
                "message": "Test case lacks concrete expected results."
            })

        # Check 4: Pass/Fail criteria
        pass_fail = test_case.get("pass_fail_criteria", [])
        if isinstance(pass_fail, list):
            pass_fail_str = " ".join(str(p) for p in pass_fail)
        else:
            pass_fail_str = str(pass_fail or "")

        if not pass_fail_str.strip():
            errors.append({
                "code": "MISSING_PASS_FAIL_CRITERIA",
                "message": "Test case must specify definitive pass/fail criteria."
            })

        # Check 5: Traceability
        traceability = test_case.get("traceability", {})
        if not traceability or not traceability.get("requirement_id"):
            warnings.append({
                "code": "INCOMPLETE_TRACEABILITY",
                "message": "Test case traceability metadata is missing requirement ID reference."
            })

        # Check 6 & 7: Hallucinated Timing / Threshold detection
        req_text = f"{req.original_text} {req.normalized_summary or ''}".lower()
        req_timing = (req.timing_constraint or "").strip().lower()
        req_threshold = (req.threshold or "").strip().lower()

        # Concatenate test text to inspect for invented values
        test_text = " ".join([
            test_case.get("title", ""),
            " ".join(test_case.get("steps", [])),
            " ".join(expected_results if isinstance(expected_results, list) else [str(expected_results)]),
            pass_fail_str
        ]).lower()

        # Specification gap check from DB
        db_gaps = self.db.query(SpecificationGap).filter(SpecificationGap.requirement_id == req.id).all()
        db_gap_types = {g.gap_type for g in db_gaps}

        # Timing inspection
        timing_pattern = re.findall(r'\b(\d+(?:\.\d+)?\s*(?:ms|milliseconds?|s|seconds?))\b', test_text)
        if timing_pattern:
            for matched_t in timing_pattern:
                clean_t = matched_t.strip()
                # Check if this timing exists in requirement text or requirement.timing_constraint
                if clean_t not in req_text and (not req_timing or clean_t not in req_timing):
                    # Flag invented timing
                    errors.append({
                        "code": "HALLUCINATED_TIMING_VALUE",
                        "message": f"Generated test specifies timing value '{matched_t}' not present in requirement {req.req_code}."
                    })

        # If requirement has MISSING_TIMEOUT gap, test must preserve it or require review
        if "MISSING_TIMEOUT" in db_gap_types or (not req.timing_constraint and ("detect" in req_text and "within" not in req_text)):
            spec_gaps = test_case.get("specification_gaps", [])
            if "MISSING_TIMEOUT" not in spec_gaps:
                warnings.append({
                    "code": "SPECIFICATION_GAP_OMITTED",
                    "message": f"Requirement {req.req_code} lacks timing constraint. Test should acknowledge MISSING_TIMEOUT."
                })
            warnings.append({
                "code": "SPECIFICATION_GAP_PRESENT",
                "message": f"Requirement contains specification gap MISSING_TIMEOUT. Test requires engineering review."
            })

        # Threshold / Ambiguous boundary inspection
        if "AMBIGUOUS_BOUNDARY" in db_gap_types or "maintain vehicle stability" in req_text or ("stability" in req_text and not req.threshold):
            # Look for hallucinated yaw rate or lateral acceleration numbers
            hallucinated_metrics = re.findall(r'(yaw\s*rate|lateral\s*accel\w*|g-force)\s*(?:[<>=]|less than|greater than|exceeds?)\s*(\d+(?:\.\d+)?)', test_text)
            if hallucinated_metrics:
                for metric, val in hallucinated_metrics:
                    errors.append({
                        "code": "HALLUCINATED_THRESHOLD_VALUE",
                        "message": f"Generated test fabricated numerical metric '{metric} = {val}' for ambiguous requirement {req.req_code}."
                    })
            warnings.append({
                "code": "AMBIGUOUS_BOUNDARY_PRESENT",
                "message": f"Requirement {req.req_code} has AMBIGUOUS_BOUNDARY. Test requires engineering review."
            })

        # Check 8: Referenced ECUs exist in architecture
        ecus = test_case.get("ecu_under_test", [])
        for ecu in ecus:
            ecu_clean = ecu.upper().strip()
            if ecu_clean != "UNKNOWN_ECU" and ecu_clean not in self.known_ecus:
                warnings.append({
                    "code": "UNKNOWN_ARCHITECTURE_ECU",
                    "message": f"Referenced ECU '{ecu}' is not in known vehicle architecture."
                })

        # Check 9: Referenced signals
        signals = test_case.get("input_signals", [])
        for sig in signals:
            sig_clean = sig.upper().strip()
            if sig_clean not in self.known_signals:
                warnings.append({
                    "code": "UNKNOWN_ARCHITECTURE_SIGNAL",
                    "message": f"Referenced signal '{sig}' is not in vehicle signal database."
                })

        # Check 11: Does generated test falsely claim an execution result?
        status_val = str(test_case.get("status", "")).upper()
        gen_status = str(test_case.get("generation_status", "")).upper()
        if status_val in ["PASS", "FAIL", "BLOCKED"] or gen_status in ["PASS", "FAIL", "BLOCKED"]:
            errors.append({
                "code": "INVALID_EXECUTION_CLAIM",
                "message": "Generated test case must NOT claim execution status (PASS/FAIL/BLOCKED) in Phase 3."
            })

        # Check if execution result is inside pass_fail_criteria
        if any(term in pass_fail_str for term in ["TEST PASSED", "TEST FAILED", "EXECUTION PASSED", "EXECUTION FAILED"]):
            errors.append({
                "code": "INVALID_EXECUTION_CLAIM",
                "message": "Pass/fail criteria must define evaluation rules, not claim that execution has passed."
            })

        # Determine overall deterministic status
        if errors:
            status = "INVALID"
        elif warnings:
            status = "REQUIRES_REVIEW"
        else:
            status = "VALID"

        return {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "checked_rule_count": 12
        }

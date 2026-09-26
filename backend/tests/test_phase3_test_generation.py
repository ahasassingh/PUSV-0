import pytest
from app.models.requirement import Requirement, SpecificationGap
from app.models.vehicle import Vehicle, ECU, Sensor, Actuator, Signal
from app.models.test_case import TestCase, TestGenerationRun
from app.services.test_generation_context import TestGenerationContextAssembler
from app.services.ai_generator import MockAIProvider, GeminiAIProvider, get_ai_provider
from app.services.test_case_validator import TestCaseValidator


@pytest.fixture(autouse=True)
def setup_phase3_test_data(db):
    """Seed reference vehicle, ECUs, signals, and test requirements."""
    # Ensure reference vehicle exists
    v = db.query(Vehicle).first()
    if not v:
        v = Vehicle(
            id="veh_pusv01",
            name="PUSV-01",
            full_name="Pune Urban Safety Vehicle Prototype 01",
            vehicle_class="Compact Sedan",
            reference_model="Honda Civic Ref Model",
            sw_version="PUSV-SW-0.1"
        )
        db.add(v)
        db.commit()

    # Ensure Brake ECU exists
    ecu = db.query(ECU).filter(ECU.name == "BRAKE_ECU").first()
    if not ecu:
        ecu = ECU(
            id="ecu_brake",
            vehicle_id=v.id,
            name="BRAKE_ECU",
            subsystem="Braking",
            domain="Chassis",
            bus_type="CAN-FD",
            safety_integrity_level="ASIL-D"
        )
        db.add(ecu)
        db.commit()

    # Ensure Wheel speed sensor exists
    sensor = db.query(Sensor).filter(Sensor.name == "Wheel_Speed_FL").first()
    if not sensor:
        sensor = Sensor(
            id="SENS-WS-FL",
            ecu_id=ecu.id,
            name="Wheel_Speed_FL",
            sensor_type="WHEEL_SPEED",
            sampling_rate_hz=50.0,
            unit="km/h"
        )
        db.add(sensor)
        db.commit()

    # Ensure Signal exists
    sig = db.query(Signal).filter(Signal.name == "Vehicle_Speed").first()
    if not sig:
        sig = Signal(
            id="SIG-VEH-SPD",
            name="Vehicle_Speed",
            source_ecu_id=ecu.id,
            signal_type="FLOAT",
            unit="km/h",
            cycle_time_ms=20
        )
        db.add(sig)
        db.commit()

    # Seed Requirement 1: BRK-REQ-101 (Complete requirement with 100 ms timeout)
    r101 = db.query(Requirement).filter(Requirement.req_code == "BRK-REQ-101").first()
    if not r101:
        r101 = Requirement(
            id="REQ-TEST-101",
            req_code="BRK-REQ-101",
            vehicle_id=v.id,
            ecu_id=ecu.id,
            system="Braking",
            subsystem="Wheel Speed Sensing",
            original_text="The braking controller shall detect wheel-speed sensor failure within 100 ms.",
            normalized_summary="Braking controller detects wheel-speed sensor failure within 100 ms.",
            timing_constraint="100 ms",
            safety_relevance="ASIL-D",
            completeness_status="COMPLETE",
            source_document="vehicle_safety_spec_v1.pdf",
            source_page=1,
            source_section="Braking Safety"
        )
        db.add(r101)
        db.commit()
    else:
        r101.vehicle_id = v.id
        r101.ecu_id = ecu.id
        r101.source_document = "vehicle_safety_spec_v1.pdf"
        r101.timing_constraint = "100 ms"
        r101.completeness_status = "COMPLETE"
        db.commit()

    # Seed Requirement 2: BRK-REQ-102 (Missing timeout requirement)
    r102 = db.query(Requirement).filter(Requirement.req_code == "BRK-REQ-102").first()
    if not r102:
        r102 = Requirement(
            id="REQ-TEST-102",
            req_code="BRK-REQ-102",
            vehicle_id=v.id,
            ecu_id=ecu.id,
            system="Braking",
            subsystem="Wheel Speed Sensing",
            original_text="The braking controller shall detect wheel-speed sensor failure.",
            normalized_summary="Braking controller detects wheel-speed sensor failure.",
            timing_constraint=None,
            safety_relevance="ASIL-D",
            completeness_status="INCOMPLETE",
            source_document="vehicle_safety_spec_v1.pdf",
            source_page=2,
            source_section="Braking Diagnostics"
        )
        db.add(r102)
        db.commit()

        # Seed gap for BRK-REQ-102
        gap102 = SpecificationGap(
            id="GAP-TEST-102",
            requirement_id=r102.id,
            gap_type="MISSING_TIMEOUT",
            severity="HIGH",
            description="Diagnostic failure detection timeout is not specified for wheel-speed sensor.",
            missing_parameter="detection_timeout_ms",
            status="OPEN"
        )
        db.add(gap102)
        db.commit()
    else:
        r102.vehicle_id = v.id
        r102.ecu_id = ecu.id
        db.commit()

    # Seed Requirement 3: BRK-REQ-103 (Ambiguous stability requirement)
    r103 = db.query(Requirement).filter(Requirement.req_code == "BRK-REQ-103").first()
    if not r103:
        r103 = Requirement(
            id="REQ-TEST-103",
            req_code="BRK-REQ-103",
            vehicle_id=v.id,
            ecu_id=ecu.id,
            system="Braking",
            subsystem="Vehicle Stability",
            original_text="The vehicle shall maintain stability during emergency braking.",
            normalized_summary="Vehicle maintains stability during emergency braking without defined metric.",
            threshold=None,
            timing_constraint=None,
            safety_relevance="ASIL-D",
            completeness_status="AMBIGUOUS",
            source_document="vehicle_safety_spec_v1.pdf",
            source_page=3,
            source_section="Stability Control"
        )
        db.add(r103)
        db.commit()

        gap103 = SpecificationGap(
            id="GAP-TEST-103",
            requirement_id=r103.id,
            gap_type="AMBIGUOUS_BOUNDARY",
            severity="HIGH",
            description="Stability is qualitative with no yaw rate or slip angle threshold specified.",
            missing_parameter="yaw_rate_deg_per_sec",
            status="OPEN"
        )
        db.add(gap103)
        db.commit()
    else:
        r103.vehicle_id = v.id
        r103.ecu_id = ecu.id
        db.commit()


# -------------------------------------------------------------
# 1. Context Assembler Tests
# -------------------------------------------------------------
def test_context_assembler_complete_requirement(db):
    assembler = TestGenerationContextAssembler(db)
    ctx = assembler.assemble("BRK-REQ-101")

    assert ctx["requirement"]["req_code"] == "BRK-REQ-101"
    assert ctx["requirement"]["timing_constraint"] == "100 ms"
    assert ctx["vehicle"]["name"] == "PUSV-01"
    assert "BRAKE_ECU" in ctx["architecture"]["ecus"]
    assert ctx["generation_rules"]["no_invented_thresholds"] is True
    assert ctx["requirement"]["traceability"]["source_document"] == "vehicle_safety_spec_v1.pdf"


def test_context_assembler_with_gaps(db):
    assembler = TestGenerationContextAssembler(db)
    ctx = assembler.assemble("BRK-REQ-102")

    assert ctx["requirement"]["req_code"] == "BRK-REQ-102"
    assert ctx["requirement"]["timing_constraint"] is None
    assert "MISSING_TIMEOUT" in ctx["requirement"]["specification_gaps"]


# -------------------------------------------------------------
# 2. AI Provider Abstraction Tests
# -------------------------------------------------------------
def test_mock_provider_deterministic_generation(db):
    assembler = TestGenerationContextAssembler(db)
    ctx = assembler.assemble("BRK-REQ-101")

    provider = MockAIProvider()
    assert provider.provider_name == "mock"

    tests = provider.generate_test_cases(
        ctx,
        categories=["FUNCTIONAL", "FAULT_INJECTION", "TIMING"],
        tests_per_requirement=3
    )

    assert len(tests) == 3
    for t in tests:
        assert t["generation_provider"] == "mock"
        assert "BRK-REQ-101" in t["requirement_ids"]
        assert len(t["steps"]) > 0
        assert len(t["expected_results"]) > 0
        assert t["pass_fail_criteria"] is not None


def test_provider_factory_fallback():
    provider = get_ai_provider("unknown_provider")
    assert provider.provider_name == "mock"


# -------------------------------------------------------------
# 3. Critical Anti-Hallucination Tests (Mandatory Scenarios)
# -------------------------------------------------------------
def test_critical_requirement_brk_101_preserves_100ms(db):
    """
    Scenario A: Complete requirement with 100 ms timing.
    Test should preserve '100 ms' and deterministic validation status must be VALID.
    """
    assembler = TestGenerationContextAssembler(db)
    ctx = assembler.assemble("BRK-REQ-101")

    provider = MockAIProvider()
    tests = provider.generate_test_cases(ctx, categories=["FAULT_INJECTION"], tests_per_requirement=1)
    tc = tests[0]

    # Verify 100 ms is preserved in test criteria/expected results
    combined_text = " ".join(tc["expected_results"] + tc["pass_fail_criteria"])
    assert "100 ms" in combined_text

    # Validate deterministically
    validator = TestCaseValidator(db)
    res = validator.validate(tc, ctx)
    assert res["status"] == "VALID"
    assert len(res["errors"]) == 0


def test_critical_requirement_brk_102_zero_hallucinated_timing(db):
    """
    Scenario B: Requirement without timing.
    Generator MUST NOT invent '100 ms' or any timeout.
    Must preserve MISSING_TIMEOUT and set validation_status = REQUIRES_REVIEW.
    """
    assembler = TestGenerationContextAssembler(db)
    ctx = assembler.assemble("BRK-REQ-102")

    provider = MockAIProvider()
    tests = provider.generate_test_cases(ctx, categories=["FAULT_INJECTION"], tests_per_requirement=1)
    tc = tests[0]

    # Verify NO timing was invented
    combined_text = " ".join(tc["expected_results"] + tc["pass_fail_criteria"])
    assert "100 ms" not in combined_text
    assert "ms" not in combined_text

    # Verify MISSING_TIMEOUT gap is preserved
    assert "MISSING_TIMEOUT" in tc["specification_gaps"]

    # Validate deterministically
    validator = TestCaseValidator(db)
    res = validator.validate(tc, ctx)
    assert res["status"] == "REQUIRES_REVIEW"
    assert any(w["code"] == "SPECIFICATION_GAP_PRESENT" for w in res["warnings"])
    assert len(res["errors"]) == 0


def test_validator_rejects_hallucinated_timing(db):
    """
    Verify that if an AI hallucinates a timing value not in requirement,
    the deterministic validator flags HALLUCINATED_TIMING_VALUE and sets INVALID.
    """
    hallucinated_test = {
        "test_id": "TC-HALLUCINATED-001",
        "title": "Hallucinated Brake Response",
        "requirement_ids": ["BRK-REQ-102"],  # Has NO timing constraint!
        "category": "FAULT_INJECTION",
        "expected_results": ["Sensor failure detected within 50 ms"],  # 50 ms is hallucinated!
        "pass_fail_criteria": ["Detection must occur in less than 50 ms."],
        "ecu_under_test": ["BRAKE_ECU"],
        "steps": ["Trigger sensor disconnect"],
        "traceability": {"requirement_id": "BRK-REQ-102"}
    }

    validator = TestCaseValidator(db)
    res = validator.validate(hallucinated_test)

    assert res["status"] == "INVALID"
    assert any(e["code"] == "HALLUCINATED_TIMING_VALUE" for e in res["errors"])


def test_critical_requirement_brk_103_ambiguous_stability_no_invented_thresholds(db):
    """
    Scenario C: 'maintain vehicle stability' without measurable criterion.
    Generator MUST NOT invent yaw rate or lateral acceleration.
    Must flag AMBIGUOUS_BOUNDARY and set REQUIRES_REVIEW.
    """
    assembler = TestGenerationContextAssembler(db)
    ctx = assembler.assemble("BRK-REQ-103")

    provider = MockAIProvider()
    tests = provider.generate_test_cases(ctx, categories=["BOUNDARY"], tests_per_requirement=1)
    tc = tests[0]

    combined_text = " ".join(tc["expected_results"] + tc["pass_fail_criteria"]).lower()
    assert "yaw rate <" not in combined_text
    assert "lateral accel" not in combined_text
    assert "AMBIGUOUS_BOUNDARY" in tc["specification_gaps"]

    validator = TestCaseValidator(db)
    res = validator.validate(tc, ctx)
    assert res["status"] == "REQUIRES_REVIEW"
    assert any(w["code"] == "AMBIGUOUS_BOUNDARY_PRESENT" for w in res["warnings"])


def test_validator_rejects_hallucinated_execution_result(db):
    """
    Validator must reject test cases that claim execution status (PASS/FAIL/BLOCKED)
    since Phase 3 only validates test definitions, not execution.
    """
    test_with_execution_claim = {
        "test_id": "TC-EXEC-CLAIM-001",
        "title": "Invalid Claim Test",
        "requirement_ids": ["BRK-REQ-101"],
        "category": "FUNCTIONAL",
        "expected_results": ["ECU responds"],
        "pass_fail_criteria": ["Criteria is met"],
        "status": "PASS",  # Claiming PASS!
        "traceability": {"requirement_id": "BRK-REQ-101"}
    }

    validator = TestCaseValidator(db)
    res = validator.validate(test_with_execution_claim)
    assert res["status"] == "INVALID"
    assert any(e["code"] == "INVALID_EXECUTION_CLAIM" for e in res["errors"])


# -------------------------------------------------------------
# 4. API Endpoint Integration Tests
# -------------------------------------------------------------
def test_api_context_preview(client):
    response = client.get("/api/v1/test-generation/context/BRK-REQ-101")
    assert response.status_code == 200
    data = response.json()
    assert data["requirement"]["req_code"] == "BRK-REQ-101"
    assert data["vehicle"]["name"] == "PUSV-01"


def test_api_generate_test_cases(client):
    payload = {
        "requirement_ids": ["BRK-REQ-101", "BRK-REQ-102"],
        "categories": ["FUNCTIONAL", "FAULT_INJECTION"],
        "tests_per_requirement": 2,
        "provider": "mock"
    }

    response = client.post("/api/v1/test-generation/generate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["provider"] == "mock"
    assert data["requested_requirements"] == 2
    assert data["generated_tests_count"] == 4
    assert len(data["test_cases"]) == 4

    # Verify BRK-REQ-101 produced VALID and BRK-REQ-102 produced REQUIRES_REVIEW
    req_101_tests = [t for t in data["test_cases"] if "BRK-REQ-101" in t["requirement_ids"]]
    req_102_tests = [t for t in data["test_cases"] if "BRK-REQ-102" in t["requirement_ids"]]

    assert any(t["validation_status"] == "VALID" for t in req_101_tests)
    assert any(t["validation_status"] == "REQUIRES_REVIEW" for t in req_102_tests)


def test_api_generation_history(client):
    response = client.get("/api/v1/test-generation/history")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0
    latest = history[0]
    assert "provider" in latest
    assert "generated_test_count" in latest

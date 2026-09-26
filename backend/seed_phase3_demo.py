import sqlite3
import uuid
import json
import os

db_path = os.path.join(os.path.dirname(__file__), "civic_ai.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

demo_tests = [
    (
        str(uuid.uuid4()),
        "TC-AI-BRK-101-001",
        "Wheel-Speed Sensor Failure Detection (Nominal 100ms)",
        "FAULT_INJECTION",
        "P0",
        json.dumps(["BRK-REQ-101"]),
        json.dumps(["BRAKE_ECU"]),
        json.dumps(["Vehicle ignition state is ON", "BRAKE_ECU is in operational state"]),
        "Nominal 100ms wheel speed sensor failure verification on PUSV-01",
        json.dumps(["Inject wheel-speed sensor disconnect", "Monitor brake controller CAN-FD diagnostic response"]),
        json.dumps(["Wheel-speed sensor failure detected by BRAKE_ECU within 100 ms"]),
        "Diagnostic detection of wheel-speed sensor failure occurs strictly within 100 ms.",
        "Safety relevance: ASIL-D. PUSV-01 reference braking system.",
        "mock",
        "rule-based-mock-engine",
        "GENERATED",
        "VALID",
        json.dumps([]),
        json.dumps({"requirement_id": "BRK-REQ-101", "source_document": "vehicle_safety_spec_v1.pdf", "source_page": 1}),
        "PROPOSED"
    ),
    (
        str(uuid.uuid4()),
        "TC-AI-BRK-101-002",
        "Nominal Verification: BRK-REQ-101 (Braking)",
        "FUNCTIONAL",
        "P0",
        json.dumps(["BRK-REQ-101"]),
        json.dumps(["BRAKE_ECU"]),
        json.dumps(["Vehicle ignition state is ON", "BRAKE_ECU is in operational state"]),
        "Nominal functional check for BRK-REQ-101",
        json.dumps(["Establish nominal operating conditions", "Verify diagnostic latch"]),
        json.dumps(["Controller diagnostic response is activated within 100 ms"]),
        "Diagnostic alert signal transmitted within 100 ms.",
        "Safety relevance: ASIL-D. PUSV-01 reference vehicle.",
        "mock",
        "rule-based-mock-engine",
        "GENERATED",
        "VALID",
        json.dumps([]),
        json.dumps({"requirement_id": "BRK-REQ-101", "source_document": "vehicle_safety_spec_v1.pdf", "source_page": 1}),
        "PROPOSED"
    ),
    (
        str(uuid.uuid4()),
        "TC-AI-BRK-102-001",
        "Wheel-Speed Sensor Failure Detection (Unconstrained Timing)",
        "FAULT_INJECTION",
        "P0",
        json.dumps(["BRK-REQ-102"]),
        json.dumps(["BRAKE_ECU"]),
        json.dumps(["Vehicle ignition state is ON", "BRAKE_ECU is operational"]),
        "Fault injection verification for requirement missing timeout",
        json.dumps(["Inject sensor disconnect", "Observe diagnostic flag on bus"]),
        json.dumps(["Wheel-speed sensor failure detected. Timing unconstrained by requirement."]),
        "Failure is detected according to BRK-REQ-102. Engineering review required for missing timeout bound.",
        "Requirement contains specification gap MISSING_TIMEOUT.",
        "mock",
        "rule-based-mock-engine",
        "REQUIRES_REVIEW",
        "REQUIRES_REVIEW",
        json.dumps([{"code": "SPECIFICATION_GAP_PRESENT", "message": "Requirement contains specification gap MISSING_TIMEOUT."}]),
        json.dumps({"requirement_id": "BRK-REQ-102", "source_document": "vehicle_safety_spec_v1.pdf", "source_page": 2}),
        "PROPOSED"
    )
]

for t in demo_tests:
    c.execute("SELECT id FROM test_cases WHERE code = ?", (t[1],))
    if not c.fetchone():
        c.execute("""
            INSERT INTO test_cases (
                id, code, title, category, priority, requirement_ids_json, ecu_under_test_json,
                preconditions_json, scenario, steps_json, expected_results_json, pass_fail_criteria,
                safety_notes, generation_provider, generation_model, generation_status, validation_status,
                validation_findings_json, traceability_json, status, is_ai_generated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, t)
        print(f"Inserted demo test case {t[1]}")

conn.commit()
conn.close()
print("Phase 3 demo test cases seeded successfully!")

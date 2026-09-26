import os
import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.models.requirement import Requirement, SpecificationGap, RequirementDocument
from app.services.document_extractor import (
    extract_txt, extract_pdf, extract_docx, extract_document_units, ExtractionError
)
from app.services.requirement_normalizer import (
    parse_requirement_id, determine_system_and_subsystem,
    extract_deterministic_fields, analyze_specification_gaps,
    normalize_units_into_requirements
)
from tests.conftest import TestingSessionLocal, test_client as client

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def test_1_txt_parsing():
    content = b"BRK-REQ-101: The braking controller shall detect wheel-speed sensor failure within 100 ms.\n\nADAS-REQ-101: The ADAS controller shall issue a collision warning when the defined collision condition occurs."
    units = extract_txt(content)
    assert len(units) == 2
    assert "BRK-REQ-101" in units[0].text
    assert "line-1" in units[0].location

def test_2_docx_parsing():
    docx_path = FIXTURES_DIR / "sample_spec.docx"
    with open(docx_path, "rb") as f:
        units = extract_docx(f.read())
    assert len(units) >= 4
    texts = [u.text for u in units]
    assert any("BRK-REQ-101" in t for t in texts)
    assert any("ADAS-REQ-101" in t for t in texts)

def test_3_pdf_parsing():
    pdf_path = FIXTURES_DIR / "sample_spec.pdf"
    with open(pdf_path, "rb") as f:
        units = extract_pdf(f.read())
    assert len(units) >= 1
    assert any("BRK-REQ-101" in u.text for u in units)
    assert units[0].page == 1

def test_4_explicit_requirement_id_extraction():
    req_id, text = parse_requirement_id("REQ-001: The vehicle shall stop within 40 m.")
    assert req_id == "REQ-001"
    assert text == "The vehicle shall stop within 40 m."

def test_5_brk_001_extraction():
    req_id, _ = parse_requirement_id("BRK-001: The brake controller shall detect failure.")
    assert req_id == "BRK-001"

def test_6_brk_req_001_extraction():
    req_id, _ = parse_requirement_id("BRK-REQ-001: Hydraulic pressure modulation active.")
    assert req_id == "BRK-REQ-001"

def test_7_adas_req_001_extraction():
    req_id, _ = parse_requirement_id("ADAS-REQ-001: Perception fusion latency <= 50 ms.")
    assert req_id == "ADAS-REQ-001"

def test_8_srs_001_extraction():
    req_id, _ = parse_requirement_id("SRS-001: Airbag squib continuity check.")
    assert req_id == "SRS-001"

def test_9_temporary_id_generation():
    from app.services.document_extractor import DocumentUnit
    units = [
        DocumentUnit("The braking system shall detect wheel-speed sensor failure within 100 ms.", location="line-1"),
        DocumentUnit("The vehicle shall maintain stability during dynamic maneuvers.", location="line-2")
    ]
    detected = normalize_units_into_requirements(units, "test.txt", set())
    assert len(detected) == 2
    assert detected[0].req_code == "TMP-REQ-001"
    assert detected[1].req_code == "TMP-REQ-002"

def test_10_deterministic_temporary_id_ordering():
    from app.services.document_extractor import DocumentUnit
    units = [
        DocumentUnit("First requirement shall monitor CAN bus.", location="line-1"),
        DocumentUnit("Second requirement shall detect sensor disconnection.", location="line-2"),
        DocumentUnit("Third requirement shall apply friction brake.", location="line-3"),
    ]
    detected_first_run = normalize_units_into_requirements(units, "test.txt", set())
    detected_second_run = normalize_units_into_requirements(units, "test.txt", set())
    assert [d.req_code for d in detected_first_run] == ["TMP-REQ-001", "TMP-REQ-002", "TMP-REQ-003"]
    assert [d.req_code for d in detected_first_run] == [d.req_code for d in detected_second_run]

def test_11_duplicate_ids_within_document():
    from app.services.document_extractor import DocumentUnit
    units = [
        DocumentUnit("BRK-REQ-101: The system shall apply brake pressure within 40 ms.", location="line-1"),
        DocumentUnit("BRK-REQ-101: The system shall detect sensor fault.", location="line-2"),
    ]
    detected = normalize_units_into_requirements(units, "test.txt", set())
    assert len(detected) == 2
    assert detected[0].is_duplicate is False
    assert detected[1].is_duplicate is True
    assert detected[1].completeness_status == "AMBIGUOUS"

def test_12_duplicate_against_existing_seeded_requirement():
    from app.services.document_extractor import DocumentUnit
    existing = {"BRK-REQ-001", "ADAS-REQ-001"}
    units = [
        DocumentUnit("BRK-REQ-001: A newly uploaded requirement that collides with seeded BRK-REQ-001.", location="line-1")
    ]
    detected = normalize_units_into_requirements(units, "test.txt", existing)
    assert len(detected) == 1
    assert detected[0].is_duplicate is True

def test_13_malformed_pdf():
    with pytest.raises(ExtractionError) as exc_info:
        extract_pdf(b"%PDF-1.4 Not a valid PDF stream corrupted content")
    assert exc_info.value.code in ("MALFORMED_PDF", "CORRUPTED_FILE")

def test_14_malformed_docx():
    with pytest.raises(ExtractionError) as exc_info:
        extract_docx(b"PK\x03\x04 fake corrupted zip byte stream")
    assert exc_info.value.code in ("MALFORMED_DOCX", "CORRUPTED_FILE")

def test_15_unsupported_extension():
    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("spec.xlsx", b"some bytes", "application/vnd.ms-excel")}
    )
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]

def test_16_empty_file():
    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("empty.txt", b"", "text/plain")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_17_file_size_rejection(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_REQUIREMENT_UPLOAD_BYTES", 50)
    oversized = b"A" * 100
    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("big.txt", oversized, "text/plain")}
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()

def test_18_source_document_persistence():
    content = b"BRK-REQ-901: The braking controller shall detect wheel-speed sensor failure within 100 ms."
    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("safety_dossier.txt", content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IMPORTED"

    # Query database
    db = TestingSessionLocal()
    req = db.query(Requirement).filter(Requirement.source_document == "safety_dossier.txt").first()
    assert req is not None
    assert req.source_document == "safety_dossier.txt"
    assert req.source_type == "uploaded_document"
    db.close()

def test_19_source_page_persistence():
    pdf_path = FIXTURES_DIR / "sample_spec.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("spec_page_test.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    db = TestingSessionLocal()
    req = db.query(Requirement).filter(Requirement.source_document == "spec_page_test.pdf").first()
    assert req is not None
    assert req.source_page == 1
    db.close()

def test_20_source_location_persistence():
    db = TestingSessionLocal()
    req = db.query(Requirement).filter(Requirement.source_document == "safety_dossier.txt").first()
    assert req is not None
    assert req.source_location is not None
    assert "line-" in req.source_location
    db.close()

def test_21_deterministic_normalization():
    text = "BRK-REQ-101: The braking controller shall detect wheel-speed sensor failure within 100 ms."
    sys_name, sub_name = determine_system_and_subsystem(text)
    inps, outs, conds, thresh, timing = extract_deterministic_fields(text, sys_name, sub_name)
    assert sys_name == "Braking"
    assert "wheel-speed sensor" in inps
    assert timing == "100 ms"

def test_22_missing_threshold_gap():
    text = "TPMS-REQ-105: The system shall detect low tyre pressure and issue visual tell-tale warning within 500 ms."
    sys_name, sub_name = determine_system_and_subsystem(text)
    inps, outs, conds, thresh, timing = extract_deterministic_fields(text, sys_name, sub_name)
    cstat, gaps = analyze_specification_gaps("TPMS-REQ-105", text, sys_name, sub_name, thresh, timing, "ASIL-B")
    assert any(g["gap_type"] == "MISSING_THRESHOLD" for g in gaps)
    assert cstat == "INCOMPLETE"

def test_23_missing_timing_gap():
    text = "BRK-REQ-102: The braking controller shall detect wheel-speed sensor failure."
    sys_name, sub_name = determine_system_and_subsystem(text)
    inps, outs, conds, thresh, timing = extract_deterministic_fields(text, sys_name, sub_name)
    cstat, gaps = analyze_specification_gaps("BRK-REQ-102", text, sys_name, sub_name, thresh, timing, "ASIL-D")
    assert any(g["gap_type"] == "MISSING_TIMEOUT" for g in gaps)
    assert timing is None
    assert cstat == "INCOMPLETE"

def test_24_no_hallucinated_threshold():
    text = "The braking controller shall detect wheel-speed sensor failure."
    sys_name, sub_name = determine_system_and_subsystem(text)
    inps, outs, conds, thresh, timing = extract_deterministic_fields(text, sys_name, sub_name)
    assert thresh is None
    assert timing is None

def test_25_database_persistence():
    db = TestingSessionLocal()
    docs = db.query(RequirementDocument).all()
    assert len(docs) >= 1
    assert docs[0].sanitized_filename is not None
    db.close()

def test_26_api_success_response():
    content = b"ADAS-REQ-901: The ADAS controller shall issue forward collision warning within 50 ms."
    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("fcw_spec.txt", content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IMPORTED"
    assert data["requirements_detected"] >= 1
    assert data["requirements_imported"] >= 1
    assert "document_id" in data

def test_27_api_validation_error():
    # Empty non-requirement prose file
    content = b"The quick brown fox jumps over the lazy dog."
    response = client.post(
        "/api/v1/requirements/upload",
        files={"file": ("prose.txt", content, "text/plain")}
    )
    assert response.status_code == 422
    assert "no engineering requirements detected" in response.json()["detail"].lower()

def test_28_existing_seeded_requirements_remain_intact():
    db = TestingSessionLocal()
    # PUSV-01 has 40 seed requirements seeded in seed_data.py
    seed_reqs = db.query(Requirement).filter(Requirement.source_type == "seed").all()
    assert len(seed_reqs) >= 40
    # Verify core safety requirements are untouched
    brk_001 = db.query(Requirement).filter(Requirement.req_code == "BRK-REQ-001").first()
    assert brk_001 is not None
    assert brk_001.source_type == "seed"
    assert "peak deceleration" in brk_001.original_text
    db.close()

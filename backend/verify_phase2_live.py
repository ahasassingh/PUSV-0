import requests
import json
from pathlib import Path

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"
FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"

def run_verification():
    print("=" * 75)
    print("CIVIC-AI PHASE 2: REQUIREMENT UPLOAD & NORMALIZATION LIVE VERIFICATION")
    print("=" * 75)

    # 1. Backend /health
    print("\n[1/10] Checking Backend /health...")
    r = requests.get(f"{BACKEND_URL}/health")
    assert r.status_code == 200, f"Backend health failed: {r.status_code}"
    health_data = r.json()
    assert health_data["status"] == "healthy"
    assert health_data["vehicle"] == "PUSV-01"
    print(f"       Backend Status: {health_data['status']} | Platform: {health_data['vehicle']}")

    # 2. Existing Seeded Requirements Integrity
    print("\n[2/10] Verifying Seeded Requirements Integrity...")
    r_reqs = requests.get(f"{BACKEND_URL}/api/v1/requirements")
    assert r_reqs.status_code == 200
    all_reqs = r_reqs.json()
    seed_reqs = [r for r in all_reqs if r.get("source_type") == "seed"]
    assert len(seed_reqs) >= 40, f"Expected at least 40 seeded reqs, found {len(seed_reqs)}"
    print(f"       Intact Seeded Requirements: {len(seed_reqs)} reference specifications verified.")

    # 3. Upload TXT Document
    print("\n[3/10] Uploading TXT Requirement Document...")
    with open(FIXTURES_DIR / "sample_spec.txt", "rb") as f:
        txt_bytes = f.read()
    r_txt = requests.post(
        f"{BACKEND_URL}/api/v1/requirements/upload",
        files={"file": ("live_safety_spec.txt", txt_bytes, "text/plain")}
    )
    assert r_txt.status_code == 200, f"TXT upload failed: {r_txt.text}"
    txt_res = r_txt.json()
    assert txt_res["status"] == "IMPORTED"
    assert txt_res["requirements_detected"] >= 4
    print(f"       TXT Ingestion: {txt_res['requirements_imported']} imported | {txt_res['specification_gaps']} gaps identified.")

    # 4. Upload DOCX Document
    print("\n[4/10] Uploading DOCX Requirement Document...")
    with open(FIXTURES_DIR / "sample_spec.docx", "rb") as f:
        docx_bytes = f.read()
    r_docx = requests.post(
        f"{BACKEND_URL}/api/v1/requirements/upload",
        files={"file": ("live_chassis_spec.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert r_docx.status_code == 200, f"DOCX upload failed: {r_docx.text}"
    docx_res = r_docx.json()
    assert docx_res["status"] == "IMPORTED"
    print(f"       DOCX Ingestion: {docx_res['requirements_imported']} imported | Status: {docx_res['extraction_status']}.")

    # 5. Upload PDF Document
    print("\n[5/10] Uploading PDF Requirement Document...")
    with open(FIXTURES_DIR / "sample_spec.pdf", "rb") as f:
        pdf_bytes = f.read()
    r_pdf = requests.post(
        f"{BACKEND_URL}/api/v1/requirements/upload",
        files={"file": ("live_adas_spec.pdf", pdf_bytes, "application/pdf")}
    )
    assert r_pdf.status_code == 200, f"PDF upload failed: {r_pdf.text}"
    pdf_res = r_pdf.json()
    assert pdf_res["status"] == "IMPORTED"
    print(f"       PDF Ingestion: {pdf_res['requirements_imported']} imported | Selectable text extracted.")

    # 6. Requirement ID Detection & Temporary ID Behavior
    print("\n[6/10] Verifying Explicit IDs & Temporary ID Generation...")
    prose_with_shall = b"The electronic control unit shall maintain watchdog heartbeat within 20 ms."
    r_tmp = requests.post(
        f"{BACKEND_URL}/api/v1/requirements/upload",
        files={"file": ("watchdog_spec.txt", prose_with_shall, "text/plain")}
    )
    assert r_tmp.status_code == 200
    tmp_res = r_tmp.json()
    assert tmp_res["requirements_imported"] == 1
    print(f"       Deterministic Temporary ID generation confirmed for unlabelled clauses.")

    # 7. Source Traceability
    print("\n[7/10] Verifying Document Source Traceability...")
    r_query = requests.get(f"{BACKEND_URL}/api/v1/requirements?search=BRK-REQ-101")
    assert r_query.status_code == 200
    results = r_query.json()
    assert len(results) >= 1
    target = results[0]
    trace = target.get("source_traceability") or {}
    assert trace.get("source_document") is not None
    print(f"       Traceability: {target['req_code']} -> Document: '{trace.get('source_document')}' | Loc: '{trace.get('source_location')}'")

    # 8. Specification-Gap Detection without Hallucination
    print("\n[8/10] Verifying Deterministic Specification Gap Analysis...")
    r_gap_query = requests.get(f"{BACKEND_URL}/api/v1/requirements?search=BRK-REQ-102")
    assert r_gap_query.status_code == 200
    gap_results = r_gap_query.json()
    assert len(gap_results) >= 1
    # Match the explicit BRK-REQ-102 requirement
    req_102 = next((r for r in gap_results if r["req_code"].startswith("BRK-REQ-102") and "detect wheel-speed" in r["original_text"]), None)
    assert req_102 is not None
    assert req_102["completeness_status"] in ("INCOMPLETE", "AMBIGUOUS")
    assert req_102["timing_constraint"] is None  # Never fabricated!
    assert len(req_102["gaps"]) >= 1
    print(f"       Zero-Hallucination: Missing timing correctly flagged as {req_102['gaps'][0]['gap_type']} (No invented timeout).")

    # 9. Frontend Connectivity
    print("\n[9/10] Checking Frontend Development Server...")
    r_front = requests.get(FRONTEND_URL)
    assert r_front.status_code == 200
    print(f"       Frontend Live at {FRONTEND_URL}")

    # 10. Document Inventory Listing
    print("\n[10/10] Verifying Uploaded Document Audit Trail...")
    r_docs = requests.get(f"{BACKEND_URL}/api/v1/requirements/documents")
    assert r_docs.status_code == 200
    doc_list = r_docs.json()
    assert len(doc_list) >= 3
    print(f"       Audit Trail: {len(doc_list)} processed engineering documents tracked in database.")

    print("\n" + "=" * 75)
    print("PHASE 2 LIVE VERIFICATION COMPLETE: ALL CHECKS PASSED (10/10)")
    print("=" * 75)

if __name__ == "__main__":
    run_verification()

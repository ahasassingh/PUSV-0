# TODO.md — CIVIC-AI Implementation Checklist
**Context-Aware Intelligent Vehicle Inspection & Compliance AI**
*Granular Phase-by-Phase Task Tracker*

---

## 🏁 Phase 1: Application Shell, Database & PUSV-01 Seed Data *(COMPLETED)*
- [x] Backend Project Structure setup:
  - [x] Virtual environment / Python dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `networkx`, `pytest`, `httpx`).
  - [x] SQLAlchemy Database setup (`app/core/database.py`, `app/core/config.py`).
  - [x] Relational Models for Vehicles, ECUs, Sensors, Actuators, Signals, Requirements, Scenarios, Test Cases, Results, Gaps.
- [x] PUSV-01 Reference Seed Dataset Loader:
  - [x] Vehicle: PUSV-01 (fictional compact sedan, non-proprietary reference).
  - [x] 8 Logical ECUs: `ADAS_ECU`, `BRAKE_ECU`, `VEHICLE_DYNAMICS_ECU`, `TPMS_ECU`, `POWERTRAIN_ECU`, `BODY_ECU`, `GATEWAY_ECU`, `TELEMATICS_ECU`.
  - [x] 15+ Sensors and Actuators (Radar, Camera, Wheel Speed, IMU, TPMS, Modulator, etc.).
  - [x] 25+ CAN/CAN-FD Signals with cycle times and min/max ranges.
  - [x] 40+ Requirements across Braking (15+), ADAS (8+), TPMS (5+), Suspension/Road (5+), Communication (5+), Diagnostics (5+) with intentional gaps.
  - [x] 20 Scenarios across the 6 Pune categories.
  - [x] Seed Test Cases linked to requirements and ECUs.
- [x] Core API Endpoints for Phase 1:
  - [x] `GET /api/v1/health`
  - [x] `GET /api/v1/dashboard/stats`
  - [x] `GET /api/v1/architecture/ecus`
  - [x] `GET /api/v1/architecture/graph`
  - [x] `GET /api/v1/requirements`
  - [x] `GET /api/v1/scenarios`
  - [x] `GET /api/v1/tests`
- [x] Automated Test Suite for Phase 1:
  - [x] Pytest verification for DB schema, seed loader, and all endpoints (13/13 passing).
- [x] Frontend Project Shell setup:
  - [x] Vite + React + TypeScript + Tailwind/Vanilla CSS engineering dark theme.
  - [x] Navigation shell: Dashboard, Requirements, Vehicle Architecture, Scenarios, Generate Tests, Test Cases, Simulation, Coverage, Specification Gaps, Reports.
  - [x] Live end-to-end API communication verified.

---

## 🏁 Phase 2: Requirement Upload, Document Parsing & Deterministic Normalization *(COMPLETED)*
- [x] Document Ingestion service (`app/services/document_extractor.py`) supporting PDF, DOCX, and TXT.
- [x] File upload endpoint: `POST /api/v1/requirements/upload` with extension, MIME, and size validation (`MAX_REQUIREMENT_UPLOAD_MB = 10`).
- [x] Secure file storage & filename sanitization (`app/core/file_security.py`).
- [x] Generalized requirement token detection (`BRK-001`, `BRK-REQ-001`, `ADAS-REQ-001`, `SRS-001`).
- [x] Natural language requirement extractor with deterministic temporary ID assignment (`TMP-REQ-001`).
- [x] Duplicate requirement handling within document and against existing database requirements.
- [x] Deterministic normalization (`app/services/requirement_normalizer.py`): inputs, outputs, conditions, thresholds, timing, safety relevance.
- [x] Zero-hallucination guarantee: missing parameters produce specification gaps (`MISSING_THRESHOLD`, `MISSING_TIMEOUT`, `AMBIGUOUS_BOUNDARY`).
- [x] Source traceability structure: `source_document`, `source_page`, `source_section`, `source_location`.
- [x] Database persistence: `RequirementDocument` and `Requirement` models with `source_type` ("seed" vs "uploaded_document").
- [x] Interactive Requirements UI: drag-and-drop uploader, extraction status, and document traceability display.
- [x] Automated test suite: 28/28 tests passing (`tests/test_phase2_requirements.py`).
- [x] Regression verification: 13/13 Phase 1 tests passing, 63/63 total tests passing.
- [x] Live end-to-end verification passing: 10/10 checks (`verify_phase2_live.py`).

---

## 🏁 Phase 3: AI Test Case Generation & Deterministic Validation *(COMPLETED)*
- [x] AI Provider abstraction layer: `BaseAIProvider`, `MockAIProvider`, `GeminiAIProvider`, `get_ai_provider`.
- [x] Context Assembler: `TestGenerationContextAssembler` for controlled requirement and architecture grounding without invented relations.
- [x] Zero-hallucination deterministic validator: `TestCaseValidator` with 12-point quality checks.
- [x] Strict safety guardrails:
  - [x] Rejection of hallucinated timing bounds (e.g. preserves 100 ms for `BRK-REQ-101`, flags `MISSING_TIMEOUT` / `REQUIRES_REVIEW` for `BRK-REQ-102`).
  - [x] Rejection of hallucinated stability thresholds (e.g. flags `AMBIGUOUS_BOUNDARY` for qualitative stability requirements).
  - [x] Detection of unknown ECUs, sensors, or signals against vehicle architecture.
  - [x] Strict prohibition of execution status claims (`PASS`/`FAIL`) during test generation phase.
- [x] Data Model & Database:
  - [x] Added `generation_provider`, `generation_model`, `generation_status`, `validation_status`, `validation_findings_json`, `traceability_json`, `generation_context_json` to `TestCase`.
  - [x] Created `TestGenerationRun` model and `test_generation_runs` audit table.
- [x] REST API Endpoints:
  - [x] `POST /api/v1/test-generation/generate`
  - [x] `GET /api/v1/test-generation/context/{requirement_id}`
  - [x] `POST /api/v1/test-generation/validate`
  - [x] `GET /api/v1/test-generation/history`
- [x] Frontend Implementation:
  - [x] "Generate Test Cases" button and multi-requirement selection in `RequirementsView`.
  - [x] Test generation configuration modal (categories, tests per requirement, provider).
  - [x] AI Generated badges, Provider indicator, and Deterministic Validation status (`VALID`, `REQUIRES_REVIEW`) in `TestCasesView`.
  - [x] Requirement document traceability card and acknowledged specification gaps in test detail modal.
- [x] Automated test suite: `backend/tests/test_phase3_test_generation.py` (12/12 passing).
- [x] Full regression test run: 75/75 tests passing across Phases 1, 2, and 3.

---

## 📋 Phase 4: Pune / India Scenario Engine
- [ ] Scenario catalog UI for 6 Pune categories.
- [ ] Interactive Compound Scenario Builder.
- [ ] Scenario parameter synthesis (road friction, visibility, traffic density).

---

## 📋 Phase 6: Vehicle Knowledge Graph
- [ ] NetworkX backend graph builder.
- [ ] Interactive UI graph visualizer (nodes for ECUs, sensors, signals, actuators; colored edges).
- [ ] Dependency path inspector (e.g. Front Camera → ADAS_ECU → AEB_Request → BRAKE_ECU).

---

## 📋 Phase 7: Deterministic Simulation Engine
- [ ] Physics & signal models:
  - [ ] Collision / TTC model.
  - [ ] Dynamic TPMS thermal/leak model.
  - [ ] CAN communication watchdog and jitter model.
  - [ ] Road roughness and pothole IMU shock model.
  - [ ] Braking state machine: `NORMAL` → `WARNING` → `BRAKING_REQUEST` → `BRAKING` → `RECOVERY` / `FAULT`.
- [ ] Test status evaluation: `PASS`, `FAIL`, `BLOCKED` (with actionable blocked reasons).

---

## 📋 Phase 8: Coverage & Specification Gap Engine
- [ ] Real multidimensional coverage calculation: Requirement, ECU, Scenario, Fault, Boundary.
- [ ] Specification Gap triage dashboard with severity levels and engineering recommendations.

---

## 📋 Phase 9: Reporting & Export Engine
- [ ] Export to JSON, CSV, and tabular data.
- [ ] Audit traceability matrix generation.

---

## 📋 Phase 10: Polish & Primary Demo Script
- [ ] High-contrast engineering UI polish.
- [ ] End-to-end Pune monsoon urban traffic demo flow execution.

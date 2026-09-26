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

## 📋 Phase 2: Requirement Upload & Document Parsing
- [ ] Parser service supporting PDF, DOCX, and TXT.
- [ ] Token detection for `REQ-001`, `BRK-001`, `SRS-001`.
- [ ] Natural language requirement extractor with automatic ID assignment.
- [ ] File upload API endpoint (`POST /api/v1/requirements/upload`).

---

## 📋 Phase 3: Requirement Normalization & Completeness Engine
- [ ] Structured extraction of inputs, outputs, conditions, thresholds, timing, dependencies.
- [ ] Completeness classification: `COMPLETE`, `INCOMPLETE`, `AMBIGUOUS`, `CONTRADICTORY`.
- [ ] Automatic specification gap generation for missing safety-critical thresholds.

---

## 📋 Phase 4: AI Test Case Generator
- [ ] `AIProvider` interface definition.
- [ ] `GeminiProvider` implementation with Pydantic JSON schema mode.
- [ ] Architecture-aware prompt crafting incorporating ECU dependencies and signal constraints.
- [ ] Fallback deterministic generator for offline and deterministic environments.

---

## 📋 Phase 5: Pune / India Scenario Engine
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

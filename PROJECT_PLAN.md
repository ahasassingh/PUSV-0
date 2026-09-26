# PROJECT_PLAN.md — CIVIC-AI Development Plan
**Context-Aware Intelligent Vehicle Inspection & Compliance AI**
*Lead Architect & Senior Full-Stack Engineering Blueprint*

---

## 1. Executive Summary & Product Positioning

**CIVIC-AI** is a production-grade B2B automotive software validation and test-generation platform engineered to bridge the gap between high-level automotive software requirements and real-world edge-case validation.

### Core Value Proposition
Automotive OEMs and Tier-1 suppliers face immense difficulty translating functional specifications into comprehensive test suites that account for:
1. Complex multi-ECU interactions and CAN network propagation delays.
2. Real-world operating domain hazards (specifically Indian/Pune dense traffic, monsoon conditions, unmapped potholes, and aggressive motorcycle cut-ins).
3. Degradation modes, sensor failure injection, and stale communication recovery.
4. Latent specification gaps (missing timeout values, undefined recovery thresholds, and ambiguous boundary limits).

Rather than treating AI as a simple text summarizer ("Requirement in, generic test out"), CIVIC-AI implements a deterministic, multi-stage engineering pipeline:
```
Requirement (PDF/DOCX/TXT)
  ↓
Requirement Parser & Normalizer
  ↓
PUSV-01 Vehicle Architecture & Knowledge Graph (ECU, Sensor, Signal, Actuator)
  ↓
Pune / Indian Operational Domain Scenario Engine
  ↓
Architecture-Aware Multi-ECU Test Case Generator (Structured Schema)
  ↓
Deterministic Test Validator (No hallucinated thresholds)
  ↓
Lightweight Deterministic Simulation Engine (TTC, TPMS, CAN, Road/IMU, Braking)
  ↓
Traceability, Coverage & Specification Gap Matrix
```

### Reference Vehicle: PUSV-01
- **Platform Name**: Pune Urban Safety Vehicle (PUSV-01)
- **Vehicle Class**: Compact Sedan (fictional reference inspired by publicly documented modern compact sedan capabilities such as the Honda Civic).
- **Compliance Rule**: Absolutely **no claim** of access to Honda proprietary internal ECU code or Honda IP. PUSV-01 is a self-contained, fully documented fictional open engineering reference.

---

## 2. System Architecture Overview

The application is structured as a decoupled full-stack architecture:
- **Backend**: Python 3.14+, FastAPI, SQLAlchemy ORM, Pydantic v2 data contracts, SQLite (PostgreSQL-ready), NetworkX for the vehicle topological dependency graph.
- **Frontend**: React 18/19, TypeScript, Vite, Tailwind CSS, Lucide icons, interactive SVG/Canvas architecture visualizers, and dark-mode engineering styling.
- **AI Core**: Provider-agnostic abstraction layer (`AIProvider`) with concrete `GeminiProvider` implementation, structured JSON generation with strict Pydantic parsing, automatic schema retry loops, and deterministic fallback generation.

---

## 3. Development Sequence (Canonical Phases 1 - 8)

### Phase 1: Architecture, Database & PUSV-01 Seed Foundation *(COMPLETE)*
- FastAPI backend, SQLite database schema via SQLAlchemy, React TypeScript engineering frontend.
- Reference vehicle: PUSV-01 (Pune Urban Safety Vehicle) with 8 Logical ECUs, 15+ sensors/actuators, 25+ CAN signals, 40+ reference requirements, and 20 Pune scenarios.
- 13/13 Phase 1 automated regression tests passing.

### Phase 2: Requirement Upload, Document Parsing & Deterministic Normalization *(COMPLETE)*
- Document upload endpoint: `POST /api/v1/requirements/upload` supporting `.pdf`, `.docx`, and `.txt`.
- Configurable upload size limit (`MAX_REQUIREMENT_UPLOAD_MB = 10`).
- Deterministic text extraction (TXT, DOCX, and selectable PDF). OCR explicitly disabled for scanned/image PDFs (`EXTRACTION_FAILED_SCANNED_PDF`).
- Generalized requirement ID detection (e.g. `BRK-001`, `BRK-REQ-001`, `ADAS-REQ-001`, `SRS-001`) and deterministic temporary ID generation (`TMP-REQ-001`).
- Deterministic field extraction (inputs, outputs, conditions, threshold, timing, safety relevance) using controlled vocabularies without LLM hallucination.
- Specification gap detection: identifies missing thresholds (`MISSING_THRESHOLD`), missing timeouts (`MISSING_TIMEOUT`), and ambiguous boundaries without fabricating values.
- Source traceability: preserves `source_document`, `source_page`, `source_section`, and `source_location`.
- Database persistence: `requirement_documents` audit trail and `requirements` differentiated by `source_type` ("seed" vs "uploaded_document").
- Requirements UI: drag-and-drop document ingestion, status badges, and source traceability matrix.
- 28/28 Phase 2 automated tests passing; 63/63 total tests passing; live verification 10/10 passed.

### Phase 3: AI Test-Case Generation from Normalized Requirements *(COMPLETE)*
- Canonical pipeline: Normalized Requirement -> Context Assembly -> AI Test Generator -> Structured Test Case -> Deterministic Test-Quality Validator -> Persistence.
- Core principle: "AI generates. Deterministic systems validate." Never invent safety-critical engineering values.
- AI Provider abstraction layer (`BaseAIProvider`, `MockAIProvider`, `GeminiAIProvider`, `get_ai_provider`).
- Zero hallucination validator (`TestCaseValidator`): 12-point deterministic check ensuring no invented thresholds, no invented timeouts, and preserving `MISSING_TIMEOUT` / `AMBIGUOUS_BOUNDARY` gaps as `REQUIRES_REVIEW`.
- Test generation APIs:
  - `POST /api/v1/test-generation/generate`
  - `GET /api/v1/test-generation/context/{requirement_id}`
  - `POST /api/v1/test-generation/validate`
  - `GET /api/v1/test-generation/history`
- Frontend UI: Single and bulk requirement test generation modal, configurable categories, provider selector, AI Generated badge, validation status tags (`VALID`, `REQUIRES_REVIEW`), and traceability card.
- 12/12 Phase 3 automated tests passing; 75/75 total project tests passing.

### Phase 4: Pune / India Scenario Engine & Compound Scenarios *(FUTURE)*
- Operational design domain engine across 6 categories (dense traffic, road conditions, monsoon hazards, intersections, tyre conditions, sensor failures).

### Phase 5: Knowledge Graph & Multi-ECU Dependency Engine *(FUTURE)*
- NetworkX topological dependency graph modeling cascading ECU impacts and CAN delay propagation.

### Phase 6: Simulation & Deterministic PASS / FAIL / BLOCKED Validation *(FUTURE)*
- Lightweight automotive physics models (TTC, TPMS dynamic curve, CAN jitter, IMU shock).

### Phase 7: Coverage, Specification Gaps & Exports *(FUTURE)*
- Multi-dimensional test coverage metrics and formal compliance export.

### Phase 8: Hackathon Demo Polish *(FUTURE)*
- Polished end-to-end demo flow.

---

## 4. Verification & Testing Strategy

Each phase must satisfy strict acceptance criteria before advancing:
1. **Backend Unit & Integration Tests**: `pytest` covering API endpoints, data models, and logic.
2. **Type Safety**: TypeScript check (`tsc --noEmit`) and Pydantic validation.
3. **Deterministic Integrity**: Simulation outcomes must be 100% reproducible for identical input vectors.
4. **Safety Disclaimers**: UI prominently labels AI proposals vs engineering-approved tests.

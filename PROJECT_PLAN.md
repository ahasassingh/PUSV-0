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

## 3. Development Phases (Phases 1 - 10)

### Phase 1: Application Shell, Database & PUSV-01 Seed Data *(CURRENT TARGET)*
- Setup FastAPI backend project layout and SQLite database schema via SQLAlchemy.
- Setup React + TypeScript + Vite + Tailwind CSS frontend shell.
- Implement comprehensive seed dataset:
  - Reference vehicle: PUSV-01.
  - 8 Logical ECUs (`ADAS_ECU`, `BRAKE_ECU`, `VEHICLE_DYNAMICS_ECU`, `TPMS_ECU`, `POWERTRAIN_ECU`, `BODY_ECU`, `GATEWAY_ECU`, `TELEMATICS_ECU`).
  - 15+ Sensors and Actuators.
  - 25+ Canonical CAN/CAN-FD signals with min/max/cycle times.
  - 40 Initial automotive software requirements (Braking, ADAS, TPMS, Suspension/Road, Communication, Diagnostics) with intentional specification gaps.
  - 20 Pune/India driving scenarios across 6 categories.
  - 50+ Seed automotive test cases demonstrating multi-ECU dependencies.
- Verify Phase 1 with automated backend test suite and running server.

### Phase 2: Requirement Upload & Document Parsing
- Support PDF, DOCX, and TXT upload with secure file sanitization.
- Regex and semantic heuristics for requirement token detection (`REQ-001`, `BRK-001`, `SRS-001`).
- Natural language requirement extraction with auto-generated temporary IDs.

### Phase 3: Requirement Normalizer & Completeness Engine
- Normalize raw textual requirements into structured Pydantic entities (`id`, `system`, `ecu`, `inputs`, `outputs`, `conditions`, `thresholds`, `timing`, `dependencies`, `safety_relevance`, `completeness_status`).
- Automatic completeness classification: `COMPLETE`, `INCOMPLETE`, `AMBIGUOUS`, `CONTRADICTORY`.

### Phase 4: AI Test Case Generator
- Structured prompt engineering leveraging PUSV-01 vehicle topology and selected operational domain scenarios.
- Strict Pydantic JSON schema output enforcement.
- Fallback & offline-resilient generation engine.

### Phase 5: Pune / India Scenario Engine
- Scenario catalog across 6 categories:
  1. Dense Traffic (stop-and-go, motorcycle filtering, pedestrian Jaywalking)
  2. Road Conditions (speed breakers, smooth, uneven, deep potholes)
  3. Monsoon Hazards (water spray, aquaplaning, degraded camera confidence)
  4. Intersections (uncontrolled junctions, obstructed signals, crossing cows/two-wheelers)
  5. Tyre Conditions (puncture, low pressure, thermal buildup, sensor drop)
  6. Sensor / ECU Failures (stale CAN frame, bus timeout, sensor blindness)
- Compound Scenario Builder: allow combining orthogonal conditions into multi-ECU stress scenarios.

### Phase 6: Vehicle Knowledge Graph
- NetworkX-powered directed multi-graph:
  - Nodes: `Requirement`, `ECU`, `Sensor`, `Signal`, `Actuator`, `Function`, `Scenario`, `TestCase`, `Fault`.
  - Edges: `REQUIRES`, `PRODUCES`, `CONSUMES`, `DEPENDS_ON`, `TESTS`, `AFFECTS`, `FAILS_WITH`, `RECOVERS_FROM`.
- Interactive UI visualization for path tracing (e.g. Front Camera → ADAS_ECU → AEB_REQUEST → BRAKE_ECU → Hydraulic Modulator).

### Phase 7: Deterministic Simulation Engine
- Lightweight deterministic simulation models:
  1. **Time-To-Collision (TTC) & Braking**: $TTC = \frac{d_{rel}}{v_{rel}}$ evaluated against dynamic speed curves.
  2. **TPMS Dynamic Threshold**: Pressure vs temperature compensation and leak rate classification.
  3. **CAN Communication Bus**: Heartbeat monitoring, jitter, stale message detection, timeout fault injection.
  4. **Road Roughness & Pothole**: Vertical acceleration shock profiling from simulated IMU.
  5. **Braking State Machine**: `NORMAL` → `WARNING` → `BRAKING_REQUEST` → `BRAKING` → `RECOVERY` / `FAULT`.
- Execution results: `PASS`, `FAIL`, `BLOCKED` (with actionable blocked reasons).

### Phase 8: Coverage & Specification Gap Engine
- Deterministic calculation of:
  - Requirement Coverage (%)
  - ECU Coverage (%)
  - Scenario Coverage (%)
  - Fault Injection Coverage (%)
  - Boundary Condition Coverage (%)
- Automated Gap Identification: missing thresholds, missing timeouts, undefined degraded modes, ambiguous recovery boundaries.

### Phase 9: Reporting & Export Engine
- Export complete test specifications and execution logs to JSON, CSV, and tabular data.
- Executive summary with requirement traceability matrices.

### Phase 10: Engineering Polish & Demo Showcase
- High-contrast automotive dark theme with technical typography.
- Primary Demo Script: "Pune Monsoon Urban Traffic Emergency Braking with Motorcycle Cut-in and Low Tyre Pressure".

---

## 4. Verification & Testing Strategy

Each phase must satisfy strict acceptance criteria before advancing:
1. **Backend Unit & Integration Tests**: `pytest` covering API endpoints, data models, and logic.
2. **Type Safety**: TypeScript check (`tsc --noEmit`) and Pydantic validation.
3. **Deterministic Integrity**: Simulation outcomes must be 100% reproducible for identical input vectors.
4. **Safety Disclaimers**: UI prominently labels AI proposals vs engineering-approved tests.

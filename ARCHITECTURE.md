# ARCHITECTURE.md — CIVIC-AI Technical Architecture
**Context-Aware Intelligent Vehicle Inspection & Compliance AI**
*System Design & Component Interaction Specification*

---

## 1. High-Level System Architecture

```
                  ┌────────────────────────────────────────┐
                  │    CIVIC-AI Web Application (React)    │
                  │   Tailwind CSS / Lucide / Monospace    │
                  └──────────────────┬─────────────────────┘
                                     │ HTTPS / JSON API
                                     ▼
                  ┌────────────────────────────────────────┐
                  │          FastAPI Backend (v1)          │
                  │   Router / Validation / Auth / CORS    │
                  └─────┬──────────────┬─────────────┬─────┘
                        │              │             │
        ┌───────────────┴────┐         │             └─────────────────┐
        ▼                    ▼         ▼                               ▼
┌──────────────┐     ┌──────────────┐  ┌──────────────────┐    ┌──────────────┐
│ Requirement  │     │ Vehicle      │  │ Deterministic    │    │ AI Provider  │
│ Parser &     │     │ Knowledge    │  │ Simulation       │    │ Interface    │
│ Normalizer   │     │ Graph        │  │ Engine (TTC/CAN/ │    │ (Gemini/     │
│ (PDF/DOCX/   │     │ (NetworkX)   │  │ TPMS/Braking)    │    │ Fallback)    │
│ TXT)         │     └──────────────┘  └──────────────────┘    └──────┬───────┘
└──────────────┘                                                      │
        │                                                             │
        ▼                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SQLite / PostgreSQL Database Layer                     │
│  (Vehicles, ECUs, Signals, Requirements, Scenarios, Test Cases, Results)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Architecture

### 2.1 Directory Structure
```
backend/
├── app/
│   ├── main.py                    # FastAPI entrypoint, middleware, lifespan
│   ├── core/
│   │   ├── config.py              # Pydantic BaseSettings, env vars
│   │   ├── database.py            # SQLAlchemy engine, session maker, Base
│   │   └── security.py            # File sanitization, safety filters
│   ├── models/                    # SQLAlchemy ORM Models
│   │   ├── vehicle.py             # Vehicle, ECU, Sensor, Actuator, Signal
│   │   ├── requirement.py         # Requirement, SpecGap
│   │   ├── scenario.py            # Scenario, CompoundScenario
│   │   ├── test_case.py           # TestCase, TestStep, TestResult
│   │   └── job.py                 # GenerationJob
│   ├── schemas/                   # Pydantic v2 Schemas & Data Contracts
│   │   ├── requirement.py
│   │   ├── test_case.py
│   │   ├── simulation.py
│   │   ├── scenario.py
│   │   └── graph.py
│   ├── services/                  # Core Business & Engineering Logic
│   │   ├── seed_data.py           # PUSV-01 reference dataset loader
│   │   ├── knowledge_graph.py     # NetworkX topology & traversal
│   │   ├── requirement_parser.py  # PDF/DOCX/TXT text extractor
│   │   ├── requirement_normalizer.py # Structured requirement normalizer
│   │   ├── scenario_engine.py     # Pune operational scenario catalog
│   │   ├── ai_provider.py         # AI provider interface + Gemini provider
│   │   ├── test_generator.py      # Architecture-aware test synthesis
│   │   ├── test_validator.py      # Constraint validator & gap detector
│   │   ├── simulation_engine.py   # Deterministic physics/state simulator
│   │   ├── coverage_engine.py     # Multi-dimensional coverage calculator
│   │   └── export_service.py      # JSON, CSV, and tabular exporter
│   └── api/
│       └── v1/
│           ├── endpoints/
│           │   ├── dashboard.py
│           │   ├── architecture.py
│           │   ├── requirements.py
│           │   ├── scenarios.py
│           │   ├── tests.py
│           │   ├── simulation.py
│           │   ├── coverage.py
│           │   ├── gaps.py
│           │   └── export.py
│           └── router.py
├── tests/                         # Pytest automated test suite
├── seed/                          # JSON/YAML reference definitions
├── requirements.txt
└── pyproject.toml
```

---

## 3. Reference Vehicle: PUSV-01 Topology

```
Sensors:
  [Front Radar] ──────────────┐
  [Front Wide Camera] ────────┼──► [ADAS_ECU]
  [Driver Monitor] ───────────┘          │ (CAN-FD AEB_Request, FCW_Alert)
                                         ▼
  [4x Wheel Speed] ───────────┐   [BRAKE_ECU] ◄─── [Brake Pressure Sensor]
  [Chassis IMU (Yaw/Acc)] ────┼──►       │ (Brake Modulator Commands)
                              │          ▼
                              │   [Actuator: Hydraulic Brake Unit]
                              │
  [4x Valve TPMS Sensors] ────┼──► [TPMS_ECU]
                              │          │ (CAN Tyre_Alert_Status)
                              │          ▼
                              └──► [VEHICLE_DYNAMICS_ECU] ◄── [Steering Angle]
                                         │ (ESC / TCS Torque Demands)
                                         ▼
                                   [GATEWAY_ECU] (Central Backbone Bus Router)
                                    ▲        ▲
           ┌────────────────────────┴─┐    ┌─┴────────────────────────┐
           ▼                          ▼    ▼                          ▼
   [POWERTRAIN_ECU]              [BODY_ECU]                     [TELEMATICS_ECU]
   (Inverter/Throttle)       (Lighting/Wipers)                 (4G/GPS/Event Log)
```

---

## 4. Phase 3: AI Test Generation & Deterministic Validation Architecture

### 4.1 Canonical Pipeline
```
Requirement Document
        ↓
Requirement Parser
        ↓
Normalized Requirement
        ↓
Specification Gap Analysis
        ↓
Context Assembly (PUSV-01 Vehicle, ECUs, Sensors, Signals, Existing Gaps)
        ↓
AI Test Generator (Provider Abstraction: Gemini / Deterministic Mock)
        ↓
Structured Test Case
        ↓
Deterministic Test Validator (12 Anti-Hallucination Quality Rules)
        ↓
Engineering Review (VALID / REQUIRES_REVIEW / INVALID)
        ↓
Future Test Execution (Phase 6)
```

> **Critical Distinction**: Phase 3 generates and validates test definitions. It does NOT execute tests. A `validation_status` of `VALID` means the test case is structurally, semantically, and architecturally verified for future execution — not that the physical vehicle passed a test.

### 4.2 AIProvider Interface & Implementations
- `BaseAIProvider`: Abstract base class with `generate_test_cases(context, categories, tests_per_requirement)`.
- `MockAIProvider`: Deterministic, offline, zero-hallucination test generator (`generation_provider = "mock"`).
- `GeminiAIProvider`: Google GenAI / REST integration using structured JSON schemas and strict engineering guardrails. Automatically falls back to `MockAIProvider` when `GEMINI_API_KEY` is not configured.

### 4.3 Deterministic Test Validator (`TestCaseValidator`)
Enforces the core rule: **"AI generates. Deterministic systems validate."**
- Verifies requirement existence and traceability.
- Validates expected results and definitive pass/fail criteria.
- **Zero Hallucination of Thresholds**: Prevents fabricated numerical metrics (e.g. yaw rates, deceleration g-forces) for ambiguous requirements.
- **Zero Hallucination of Timing**: Detects and rejects any timing constraint not stated in the source requirement.
- **Specification Gap Preservation**: If a requirement has `MISSING_TIMEOUT` or `AMBIGUOUS_BOUNDARY`, the validator ensures the gap is acknowledged and flags `REQUIRES_REVIEW`.
- Rejects any test that falsely claims execution outcome (`PASS`/`FAIL`/`BLOCKED`).

---

## 5. Deterministic Simulation Models

### 5.1 Time-To-Collision (TTC) & Emergency Braking
- Model:
  $$v_{rel} = v_{ego} - v_{target}$$
  $$TTC = \frac{d_{object}}{v_{rel}} \quad (\text{if } v_{rel} > 0)$$
- Brake trigger criteria:
  - $TTC \le TTC_{FCW\_threshold} \implies \text{FCW Warning}$
  - $TTC \le TTC_{AEB\_threshold} \text{ and } P_{brake} < P_{threshold} \implies \text{AEB Request Issued}$
- Road condition modifier: In wet road / pothole scenarios, friction coefficient $\mu$ is degraded from $0.85$ (dry) to $0.45$ (monsoon puddle), extending required stopping distance.

### 5.2 Dynamic TPMS Simulation
- Temperature-compensated target pressure:
  $$P_{expected} = P_{cold} \times \frac{T_{current} + 273.15}{T_{ref} + 273.15}$$
- Alerts:
  - $P < 0.80 \times P_{expected} \implies \text{LOW\_PRESSURE\_WARNING}$
  - $P < 0.70 \times P_{expected} \implies \text{CRITICAL\_PRESSURE\_ALARM}$
  - $\Delta P / \Delta t > \text{leak\_rate} \implies \text{RAPID\_PUNCTURE\_EVENT}$

### 5.3 CAN Communication Watchdog
- Heartbeat period $T_{cycle} = 20\,\text{ms}$, Timeout threshold $T_{timeout} = 100\,\text{ms}$.
- Simulation states: `HEALTHY`, `JITTER`, `STALE_DATA` (rolling counter frozen), `BUS_OFF` / `TIMEOUT`.

---

## 6. Frontend Architecture

### 6.1 Design Language
- **Engineering Dark Mode**: Deep slate `#0B0F19`, card panels `#111827`, border `#1F2937`.
- **Status Indicators**:
  - `PASS`: High-contrast Emerald `#10B981`
  - `BLOCKED`: High-contrast Amber `#F59E0B`
  - `FAIL`: High-contrast Rose `#EF4444`
  - `TELEMETRY`: Precision Cyan `#06B6D4`
- **Typography**: Inter / Outfit for display, JetBrains Mono for CAN signals, ECU identifiers, and test IDs.

### 6.2 Key Views & Navigation
1. **Dashboard**: Vehicle KPIs, requirement distribution, generated test count, coverage gauges.
2. **Requirements**: Sortable table with search, system filters, completeness badges, gap indicators, detail modal.
3. **Vehicle Architecture**: Interactive graphical node-link layout of PUSV-01 ECUs, sensors, signals, and actuators.
4. **Scenarios**: 6-category Pune scenario catalog with compound builder (e.g. Wet Road + Pothole + Motorcycle Cut-in).
5. **Generate Tests**: Controlled generation interface connecting chosen requirements and operational scenarios.
6. **Test Cases**: Full engineering specification viewer with preconditions, steps, expected outputs, fault injection, and trace links.
7. **Simulation**: Interactive deterministic runner with telemetry timeline and signal wave viewer.
8. **Coverage**: Real-time computed multidimensional coverage (Requirements, ECUs, Scenarios, Faults, Boundaries).
9. **Specification Gaps**: Centralized gap triage board highlighting missing thresholds and safety ambiguities.
10. **Reports**: Audit export center (JSON / CSV).

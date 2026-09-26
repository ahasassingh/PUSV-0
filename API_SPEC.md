# API_SPEC.md — CIVIC-AI REST API Specification
**Context-Aware Intelligent Vehicle Inspection & Compliance AI**
*FastAPI v1 Endpoint Contract & Data Serialization*

---

## Base URL
`/api/v1`

---

## 1. System & Dashboard Endpoints

### 1.1 `GET /health`
Returns system health, database status, and active reference vehicle.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "vehicle": "PUSV-01",
  "database": "connected"
}
```

### 1.2 `GET /dashboard/stats`
Aggregated metrics for the engineering dashboard overview.
- **Response `200 OK`**:
```json
{
  "vehicle_name": "PUSV-01",
  "vehicle_class": "Compact Sedan",
  "sw_version": "PUSV-SW-0.1",
  "requirements_count": 40,
  "test_cases_count": 64,
  "validated_tests_count": 52,
  "blocked_tests_count": 12,
  "specification_gaps_count": 14,
  "ecus_count": 8,
  "scenario_categories_count": 6,
  "coverage": {
    "requirement_coverage_pct": 92.5,
    "ecu_coverage_pct": 100.0,
    "scenario_coverage_pct": 85.0,
    "fault_coverage_pct": 72.4,
    "boundary_coverage_pct": 68.0
  },
  "recent_jobs": [
    {
      "id": "job_01",
      "requirement_code": "BRK-REQ-014",
      "scenario": "Monsoon Pothole + Motorcycle Cut-In",
      "tests_generated": 5,
      "status": "COMPLETED",
      "timestamp": "2026-09-26T04:30:00Z"
    }
  ]
}
```

---

## 2. Vehicle Architecture & Knowledge Graph

### 2.1 `GET /architecture/graph`
Returns nodes and edges formatted for interactive network visualization.
- **Response `200 OK`**:
```json
{
  "nodes": [
    {"id": "ecu_adas", "label": "ADAS_ECU", "type": "ECU", "domain": "Chassis/Safety"},
    {"id": "sens_front_radar", "label": "Front Radar", "type": "SENSOR", "subsystem": "Perception"},
    {"id": "sig_aeb_req", "label": "AEB_Request", "type": "SIGNAL", "cycle_ms": 20}
  ],
  "edges": [
    {"source": "sens_front_radar", "target": "ecu_adas", "relation": "REQUIRES"},
    {"source": "ecu_adas", "target": "sig_aeb_req", "relation": "PRODUCES"},
    {"source": "sig_aeb_req", "target": "ecu_brake", "relation": "CONSUMES"}
  ]
}
```

### 2.2 `GET /architecture/ecus`
List all logical ECUs with sensor and actuator counts.
- **Response `200 OK`**: Array of ECU entities.

### 2.3 `GET /architecture/ecus/{ecu_id}`
Detailed breakdown of a specific ECU, including inputs, outputs, signals, and associated test cases.

---

## 3. Requirements Management & Parsing

### 3.1 `POST /requirements/upload`
Upload specification documents (`.pdf`, `.docx`, `.txt`).
- **Request**: `multipart/form-data` with `file: UploadFile`.
- **Response `200 OK`**:
```json
{
  "filename": "pusv01_brake_spec.txt",
  "extracted_count": 8,
  "requirements": [
    {
      "id": "req_brk_014",
      "req_code": "BRK-REQ-014",
      "system": "Braking",
      "ecu": "ADAS_ECU",
      "original_text": "If collision risk exceeds threshold and driver braking is insufficient...",
      "completeness_status": "INCOMPLETE",
      "gaps_found": ["Threshold value undefined"]
    }
  ]
}
```

### 3.2 `GET /requirements`
Query and filter requirements by ECU, system, or completeness status.
- **Query Params**: `ecu`, `system`, `completeness_status`, `search`.

### 3.3 `GET /requirements/{id}`
Returns requirement detail, original vs normalized attributes, linked gaps, and generated tests.

---

## 4. Scenario Catalog & Compound Builder

### 4.1 `GET /scenarios`
Returns catalog of Pune/Indian scenarios grouped by category.

### 4.2 `POST /scenarios/compound`
Compose a compound scenario from multiple conditions.
- **Request Body**:
```json
{
  "name": "Pune Monsoon Pothole with Two-Wheeler Cut-in",
  "category_selections": {
    "traffic": "scen_motorcycle_cutin",
    "road": "scen_pothole_uneven",
    "weather": "scen_monsoon_rain",
    "tyre": "scen_low_pressure_front_right",
    "driver": "scen_delayed_braking"
  }
}
```
- **Response `200 OK`**: Compound scenario definition with combined environmental coefficients.

---

## 5. Test Case Generation & Validation

### 5.1 `POST /tests/generate`
Trigger architecture-aware test case generation.
- **Request Body**:
```json
{
  "requirement_id": "req_brk_014",
  "scenario_id": "scen_pune_compound_01",
  "target_test_types": ["Functional", "Boundary", "Fault injection", "Compound scenario"]
}
```
- **Response `200 OK`**: List of validated `TestCase` objects with safety notes and flagged gaps.

### 5.2 `GET /tests`
List all test cases with filtering by ECU, category, priority, and validation status.

### 5.3 `GET /tests/{id}`
Full engineering test specification view with preconditions, step table, signals, and trace matrix.

---

## 6. Simulation & Telemetry

### 6.1 `POST /simulation/run`
Execute deterministic simulation for a specific test case or manual parameter set.
- **Request Body**:
```json
{
  "test_case_id": "tc_brk_027",
  "overrides": {
    "ego_speed_kph": 42.0,
    "target_distance_m": 14.5,
    "relative_speed_kph": 28.0,
    "road_friction_mu": 0.45,
    "tyre_pressure_bar": 1.6
  }
}
```
- **Response `200 OK`**:
```json
{
  "test_case_id": "tc_brk_027",
  "status": "BLOCKED",
  "blocked_reason": "AEB intervention threshold is not specified in source requirement BRK-REQ-014.",
  "duration_ms": 3200,
  "metrics": {
    "time_to_collision_sec": 1.86,
    "stopping_distance_m": 18.2,
    "tyre_alarm_state": "LOW_PRESSURE_WARNING"
  },
  "telemetry_points": [
    {"timestamp_ms": 0, "ego_speed": 42, "brake_pressure_bar": 0, "state": "NORMAL"},
    {"timestamp_ms": 200, "ego_speed": 42, "brake_pressure_bar": 0, "state": "WARNING"},
    {"timestamp_ms": 600, "ego_speed": 40, "brake_pressure_bar": 45, "state": "BRAKING_REQUEST"}
  ]
}
```

### 6.2 `POST /simulation/batch`
Run all executable tests for a requirement or ECU and produce batch pass/fail/blocked summary.

---

## 7. Coverage, Specification Gaps & Export

### 7.1 `GET /coverage`
Calculate and return real computed metrics across requirements, ECUs, scenarios, faults, and boundaries.

### 7.2 `GET /gaps`
List all detected specification gaps with severity, affected ECUs, and recommended actions.

### 7.3 `GET /export/{format}`
Export test specifications and traceability matrices in `json` or `csv`.

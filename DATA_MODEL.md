# DATA_MODEL.md — CIVIC-AI Data Schema & Models
**Context-Aware Intelligent Vehicle Inspection & Compliance AI**
*Entity-Relationship Specification & Pydantic Validation Schemas*

---

## 1. Entity-Relationship Overview

```
┌──────────────┐         1:N         ┌──────────────┐
│   Vehicle    │ ──────────────────► │     ECU      │
│  (PUSV-01)   │                     └──────┬───────┘
└──────┬───────┘                            │ 1:N
       │ 1:N                                ▼
       │                             ┌──────────────┐
       ├───────────────────────────► │    Sensor    │
       │                             └──────────────┘
       │ 1:N                                │ 1:N
       │                                    ▼
       ├───────────────────────────► │    Signal    │
       │                             └──────────────┘
       │ 1:N
       ▼
┌──────────────┐         1:N         ┌───────────────────┐
│ Requirement  │ ──────────────────► │ SpecificationGap  │
└──────┬───────┘                     └───────────────────┘
       │ M:N
       ▼
┌──────────────┐         1:N         ┌───────────────────┐
│  Test Case   │ ──────────────────► │    TestResult     │
└──────▲───────┘                     └───────────────────┘
       │ M:N
┌──────┴───────┐
│   Scenario   │
│  (Pune ODD)  │
└──────────────┘
```

---

## 2. Relational Database Tables (SQLAlchemy)

### 2.1 `vehicles`
- `id` (String, PK) — e.g., `"veh_pusv01"`
- `name` (String, Not Null) — `"PUSV-01"`
- `full_name` (String) — `"Pune Urban Safety Vehicle 01"`
- `vehicle_class` (String) — `"Compact Sedan"`
- `reference_model` (String) — `"Modern C-segment Compact Sedan (Reference Architecture)"`
- `sw_version` (String) — `"PUSV-SW-0.1"`
- `description` (Text)
- `created_at` (DateTime, UTC)

### 2.2 `ecus`
- `id` (String, PK) — e.g., `"ecu_adas"`
- `vehicle_id` (String, FK `vehicles.id`)
- `name` (String, Not Null) — `"ADAS_ECU"`
- `subsystem` (String) — `"Active Safety"`
- `domain` (String) — `"Chassis / Safety"`
- `description` (Text)
- `bus_type` (String) — `"CAN-FD / Ethernet"`
- `safety_integrity_level` (String) — `"ASIL-D"`

### 2.3 `sensors`
- `id` (String, PK) — e.g., `"sens_front_radar"`
- `ecu_id` (String, FK `ecus.id`)
- `name` (String, Not Null) — `"Long Range Front Radar"`
- `sensor_type` (String) — `"RADAR"`
- `sampling_rate_hz` (Float) — `20.0`
- `range_min` (Float) — `0.5`
- `range_max` (Float) — `200.0`
- `failure_modes` (JSON) — `["blindness", "misalignment", "multipath_clutter"]`

### 2.4 `actuators`
- `id` (String, PK) — e.g., `"act_brake_modulator"`
- `ecu_id` (String, FK `ecus.id`)
- `name` (String, Not Null) — `"Electro-Hydraulic Brake Modulator"`
- `actuator_type` (String) — `"BRAKE_PRESSURE_ACTUATOR"`
- `response_time_ms` (Float) — `120.0`
- `max_output` (String) — `"150 bar"`

### 2.5 `signals`
- `id` (String, PK) — e.g., `"sig_aeb_req"`
- `name` (String, Not Null, Unique) — `"AEB_Request"`
- `source_ecu_id` (String, FK `ecus.id`)
- `consumer_ecu_ids` (JSON) — `["ecu_brake", "ecu_telematics"]`
- `signal_type` (String) — `"ENUM / BOOLEAN / FLOAT"`
- `unit` (String) — `""`, `"bar"`, `"km/h"`
- `min_value` (Float)
- `max_value` (Float)
- `cycle_time_ms` (Integer) — `20`
- `default_value` (String)

### 2.6 `requirements`
- `id` (String, PK) — e.g., `"req_brk_014"`
- `req_code` (String, Unique, Indexed) — `"BRK-REQ-014"`
- `vehicle_id` (String, FK `vehicles.id`)
- `ecu_id` (String, FK `ecus.id`)
- `system` (String) — `"Braking"`
- `subsystem` (String) — `"AEB / Deceleration"`
- `original_text` (Text, Not Null)
- `normalized_summary` (Text)
- `inputs` (JSON) — list of input signals/sensors
- `outputs` (JSON) — list of output signals/actuators
- `conditions` (JSON) — operational conditions
- `threshold` (String) — explicit threshold or `null`
- `timing_constraint` (String) — latency/cycle limits or `null`
- `safety_relevance` (String) — `"ASIL-A"`, `"ASIL-B"`, `"ASIL-C"`, `"ASIL-D"`, `"QM"`
- `completeness_status` (String) — `"COMPLETE"`, `"INCOMPLETE"`, `"AMBIGUOUS"`, `"CONTRADICTORY"`
- `created_at` (DateTime)

### 2.7 `specification_gaps`
- `id` (String, PK) — e.g., `"gap_021"`
- `requirement_id` (String, FK `requirements.id`)
- `gap_type` (String) — `"MISSING_THRESHOLD"`, `"MISSING_TIMEOUT"`, `"MISSING_RECOVERY"`, `"AMBIGUOUS_BOUNDARY"`
- `severity` (String) — `"CRITICAL"`, `"HIGH"`, `"MEDIUM"`, `"LOW"`
- `description` (Text, Not Null)
- `missing_parameter` (String)
- `affected_ecu_id` (String, FK `ecus.id`)
- `suggested_action` (Text)
- `status` (String) — `"OPEN"`, `"RESOLVED"`, `"WAIVED"`

### 2.8 `scenarios`
- `id` (String, PK) — e.g., `"scen_monsoon_pothole_cutin"`
- `category` (String) — `"DENSE_TRAFFIC"`, `"ROAD_CONDITIONS"`, `"MONSOON"`, `"INTERSECTIONS"`, `"TYRE_CONDITIONS"`, `"SENSOR_FAILURES"`
- `name` (String, Not Null) — `"Monsoon Urban Surface with Sudden Motorcycle Cut-In"`
- `pune_context` (Text) — `"High-density JM Road / FC Road monsoon evening traffic..."`
- `road_friction` (Float) — `0.45`
- `visibility_reduction_pct` (Float) — `35.0`
- `traffic_density` (String) — `"HIGH"`
- `parameters` (JSON) — specific physical attributes

### 2.9 `test_cases`
- `id` (String, PK) — e.g., `"tc_brk_027"`
- `code` (String, Unique, Indexed) — `"TC-BRK-027"`
- `title` (String, Not Null)
- `category` (String) — `"Functional"`, `"Boundary"`, `"Negative"`, `"Fault injection"`, `"Communication"`, `"Recovery"`, `"Compound scenario"`
- `priority` (String) — `"P0"`, `"P1"`, `"P2"`
- `requirement_ids` (JSON) — `["req_brk_014", "req_adas_004"]`
- `ecu_under_test` (JSON) — `["ADAS_ECU", "BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"]`
- `dependencies` (JSON) — sensors and bus lines
- `preconditions` (JSON) — list of state prerequisites
- `scenario_id` (String, FK `scenarios.id`, Nullable)
- `scenario_description` (Text)
- `input_signals` (JSON) — list of `{signal: string, value: any, unit: string}`
- `steps` (JSON) — array of step descriptions
- `expected_results` (JSON) — expected ECU and vehicle responses
- `fault_injection` (JSON) — injected faults (e.g. sensor disconnect, CAN timeout)
- `recovery_conditions` (JSON) — system stabilization criteria
- `pass_fail_criteria` (Text)
- `safety_notes` (Text)
- `confidence` (Float) — `0.95`
- `assumptions` (JSON) — assumptions made
- `specification_gaps` (JSON) — gaps unmasked by this test
- `is_ai_generated` (Boolean) — `true`
- `status` (String) — `"PROPOSED"`, `"VALIDATED"`, `"BLOCKED"`
- `created_at` (DateTime)

### 2.10 `test_results`
- `id` (String, PK)
- `test_case_id` (String, FK `test_cases.id`)
- `status` (String) — `"PASS"`, `"FAIL"`, `"BLOCKED"`
- `blocked_reason` (Text, Nullable)
- `simulation_duration_ms` (Integer)
- `telemetry_data` (JSON) — time-series points for chart rendering
- `log_trace` (JSON) — step-by-step verification messages
- `executed_at` (DateTime)

---

## 3. Pydantic v2 Core Schemas

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SafetyIntegrityLevel(str, Enum):
    QM = "QM"
    ASIL_A = "ASIL-A"
    ASIL_B = "ASIL-B"
    ASIL_C = "ASIL-C"
    ASIL_D = "ASIL-D"

class CompletenessStatus(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    AMBIGUOUS = "AMBIGUOUS"
    CONTRADICTORY = "CONTRADICTORY"

class TestExecutionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"

class NormalizedRequirementSchema(BaseModel):
    id: str
    req_code: str
    original_text: str
    system: str
    subsystem: str
    ecu: str
    inputs: List[str] = []
    outputs: List[str] = []
    conditions: List[str] = []
    threshold: Optional[str] = None
    timing: Optional[str] = None
    dependencies: List[str] = []
    safety_relevance: SafetyIntegrityLevel = SafetyIntegrityLevel.QM
    completeness_status: CompletenessStatus = CompletenessStatus.COMPLETE

class TestCaseSchema(BaseModel):
    id: str
    code: str
    title: str
    category: str
    priority: str
    requirement_ids: List[str]
    ecu_under_test: List[str]
    dependencies: List[str]
    preconditions: List[str]
    scenario: str
    input_signals: List[Dict[str, Any]]
    steps: List[str]
    expected_results: List[str]
    fault_injection: List[str] = []
    recovery_conditions: List[str] = []
    pass_fail_criteria: str
    safety_notes: str
    confidence: float = Field(ge=0.0, le=1.0)
    assumptions: List[str] = []
    specification_gaps: List[str] = []
```

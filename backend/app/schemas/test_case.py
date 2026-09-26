from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional

class TestResultSchema(BaseModel):
    id: str
    test_case_id: str
    status: str # PASS, FAIL, BLOCKED
    blocked_reason: Optional[str] = None
    simulation_duration_ms: int = 0
    telemetry_data: List[Dict[str, Any]] = []
    log_trace: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class TestCaseSchema(BaseModel):
    id: str
    code: str
    title: str
    category: str
    priority: str = "P1"
    requirement_ids: List[str] = []
    ecu_under_test: List[str] = []
    dependencies: List[str] = []
    preconditions: List[str] = []
    scenario: str
    input_signals: List[Dict[str, Any]] = []
    steps: List[str] = []
    expected_results: List[str] = []
    fault_injection: List[str] = []
    recovery_conditions: List[str] = []
    pass_fail_criteria: str
    safety_notes: Optional[str] = None
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    assumptions: List[str] = []
    specification_gaps: List[str] = []
    is_ai_generated: bool = True
    status: str = "PROPOSED"
    latest_result: Optional[TestResultSchema] = None

    model_config = ConfigDict(from_attributes=True)

class TestGenerationRequest(BaseModel):
    requirement_id: str
    scenario_id: Optional[str] = None
    target_test_types: Optional[List[str]] = None

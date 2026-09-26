from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class SimulationRunRequest(BaseModel):
    test_case_id: str
    overrides: Optional[Dict[str, Any]] = None

class SimulationRunResponse(BaseModel):
    test_case_id: str
    status: str # PASS, FAIL, BLOCKED
    blocked_reason: Optional[str] = None
    duration_ms: int = 0
    metrics: Dict[str, Any] = {}
    telemetry_points: List[Dict[str, Any]] = []
    log_trace: List[str] = []

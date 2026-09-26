from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class SpecificationGapSchema(BaseModel):
    id: str
    requirement_id: str
    gap_type: str
    severity: str
    description: str
    missing_parameter: Optional[str] = None
    affected_ecu_id: Optional[str] = None
    affected_functions: List[str] = []
    suggested_action: Optional[str] = None
    status: str = "OPEN"

    model_config = ConfigDict(from_attributes=True)

class RequirementSchema(BaseModel):
    id: str
    req_code: str
    vehicle_id: str
    ecu_id: Optional[str] = None
    system: str
    subsystem: Optional[str] = None
    original_text: str
    normalized_summary: Optional[str] = None
    inputs: List[str] = []
    outputs: List[str] = []
    conditions: List[str] = []
    threshold: Optional[str] = None
    timing_constraint: Optional[str] = None
    dependencies: List[str] = []
    safety_relevance: str = "QM"
    completeness_status: str = "COMPLETE"
    gaps: List[SpecificationGapSchema] = []
    test_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class RequirementCreateSchema(BaseModel):
    req_code: str
    system: str
    subsystem: Optional[str] = None
    original_text: str
    ecu_id: Optional[str] = None
    safety_relevance: Optional[str] = "QM"

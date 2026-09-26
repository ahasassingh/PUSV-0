from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TraceabilitySchema(BaseModel):
    requirement_id: str
    source_document: Optional[str] = "seeded_specification"
    source_page: Optional[int] = 1
    source_section: Optional[str] = None
    source_location: Optional[str] = None

class TestGenerationRequest(BaseModel):
    requirement_ids: List[str] = Field(..., description="List of requirement IDs or req_codes to generate tests for")
    categories: Optional[List[str]] = Field(
        default=["FUNCTIONAL", "BOUNDARY", "NEGATIVE", "FAULT_INJECTION", "TIMING", "INTEGRATION"],
        description="Target test categories"
    )
    tests_per_requirement: Optional[int] = Field(default=3, ge=1, le=10)
    provider: Optional[str] = Field(default=None, description="Optional override: 'mock' or 'gemini'")

class ValidationFindingSchema(BaseModel):
    code: str
    message: str

class ValidationResultSchema(BaseModel):
    status: str # VALID, REQUIRES_REVIEW, INVALID
    errors: List[ValidationFindingSchema] = []
    warnings: List[ValidationFindingSchema] = []
    checked_rule_count: Optional[int] = 12

class GeneratedTestCaseSchema(BaseModel):
    id: Optional[str] = None
    code: str
    title: str
    requirement_ids: List[str]
    category: str
    priority: str = "P1"
    ecu_under_test: List[str] = []
    dependencies: List[str] = []
    preconditions: List[str] = []
    input_signals: List[str] = []
    steps: List[str] = []
    expected_results: List[str] = []
    fault_injection: List[str] = []
    recovery_conditions: List[str] = []
    pass_fail_criteria: str
    safety_notes: Optional[str] = None
    assumptions: List[str] = []
    specification_gaps: List[str] = []
    generation_status: str = "GENERATED"
    validation_status: str = "VALID" # VALID, REQUIRES_REVIEW, INVALID
    generation_provider: str = "mock"
    generation_model: Optional[str] = None
    traceability: Optional[Dict[str, Any]] = None
    validation_findings: Optional[List[Dict[str, Any]]] = None

class TestGenerationResponse(BaseModel):
    run_id: str
    provider: str
    model: str
    requested_requirements: int
    generated_tests_count: int
    validation_summary: Dict[str, int]
    test_cases: List[GeneratedTestCaseSchema]

class TestGenerationRunHistorySchema(BaseModel):
    id: str
    provider: str
    model: Optional[str]
    timestamp: datetime
    requested_requirement_count: int
    generated_test_count: int
    validation_status: str
    error_message: Optional[str]
    requirement_ids: List[str]
    generated_test_ids: List[str]

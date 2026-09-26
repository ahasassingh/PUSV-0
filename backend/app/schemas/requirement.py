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

class SourceTraceabilitySchema(BaseModel):
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    source_location: Optional[str] = None

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
    source_type: str = "seed"
    document_id: Optional[str] = None
    source_traceability: Optional[SourceTraceabilitySchema] = None
    gaps: List[SpecificationGapSchema] = []
    test_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class RequirementDocumentSchema(BaseModel):
    id: str
    original_filename: str
    sanitized_filename: str
    file_type: str
    file_size_bytes: int
    upload_timestamp: str
    extraction_status: str
    extraction_error: Optional[str] = None
    imported_requirement_count: int = 0
    duplicate_count: int = 0
    specification_gap_count: int = 0
    processing_status: str = "COMPLETED"

    model_config = ConfigDict(from_attributes=True)

class RequirementUploadResponseSchema(BaseModel):
    document_id: str
    filename: str
    status: str
    extraction_status: str
    requirements_detected: int
    requirements_imported: int
    duplicates: int
    specification_gaps: int
    warnings: List[str] = []
    duplicate_details: List[dict] = []

class RequirementCreateSchema(BaseModel):
    req_code: str
    system: str
    subsystem: Optional[str] = None
    original_text: str
    ecu_id: Optional[str] = None
    safety_relevance: Optional[str] = "QM"


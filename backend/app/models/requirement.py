import json
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from app.core.database import Base

class RequirementDocument(Base):
    __tablename__ = "requirement_documents"

    id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    sanitized_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False) # .txt, .pdf, .docx
    file_size_bytes = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    extraction_status = Column(String, default="SUCCESS") # SUCCESS, PARTIAL, FAILED, EXTRACTION_FAILED_SCANNED_PDF
    extraction_error = Column(Text, nullable=True)
    imported_requirement_count = Column(Integer, default=0)
    duplicate_count = Column(Integer, default=0)
    specification_gap_count = Column(Integer, default=0)
    processing_status = Column(String, default="COMPLETED") # PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(String, primary_key=True, index=True)
    req_code = Column(String, unique=True, index=True, nullable=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    ecu_id = Column(String, ForeignKey("ecus.id"), nullable=True)
    system = Column(String, nullable=False, index=True)
    subsystem = Column(String, nullable=True)
    original_text = Column(Text, nullable=False)
    normalized_summary = Column(Text, nullable=True)
    
    inputs_json = Column(Text, default="[]")
    outputs_json = Column(Text, default="[]")
    conditions_json = Column(Text, default="[]")
    dependencies_json = Column(Text, default="[]")
    
    threshold = Column(String, nullable=True)
    timing_constraint = Column(String, nullable=True)
    safety_relevance = Column(String, default="QM")
    completeness_status = Column(String, default="COMPLETE", index=True) # COMPLETE, INCOMPLETE, AMBIGUOUS, CONTRADICTORY
    
    # Document upload & source traceability (Phase 2)
    source_type = Column(String, default="seed", index=True) # seed, uploaded_document
    document_id = Column(String, ForeignKey("requirement_documents.id"), nullable=True, index=True)
    source_document = Column(String, nullable=True)
    source_page = Column(Integer, nullable=True)
    source_section = Column(String, nullable=True)
    source_location = Column(String, nullable=True)
    source_traceability_json = Column(Text, default="{}")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def inputs(self):
        try:
            return json.loads(self.inputs_json or "[]")
        except Exception:
            return []

    @inputs.setter
    def inputs(self, val):
        self.inputs_json = json.dumps(val)

    @property
    def outputs(self):
        try:
            return json.loads(self.outputs_json or "[]")
        except Exception:
            return []

    @outputs.setter
    def outputs(self, val):
        self.outputs_json = json.dumps(val)

    @property
    def conditions(self):
        try:
            return json.loads(self.conditions_json or "[]")
        except Exception:
            return []

    @conditions.setter
    def conditions(self, val):
        self.conditions_json = json.dumps(val)

    @property
    def dependencies(self):
        try:
            return json.loads(self.dependencies_json or "[]")
        except Exception:
            return []

    @dependencies.setter
    def dependencies(self, val):
        self.dependencies_json = json.dumps(val)

    @property
    def source_traceability(self):
        try:
            parsed = json.loads(self.source_traceability_json or "{}")
            if parsed:
                return parsed
        except Exception:
            pass
        return {
            "source_document": self.source_document,
            "source_page": self.source_page,
            "source_section": self.source_section,
            "source_location": self.source_location
        }

    @source_traceability.setter
    def source_traceability(self, val):
        self.source_traceability_json = json.dumps(val or {})
        if isinstance(val, dict):
            self.source_document = val.get("source_document")
            self.source_page = val.get("source_page")
            self.source_section = val.get("source_section")
            self.source_location = val.get("source_location")



class SpecificationGap(Base):
    __tablename__ = "specification_gaps"

    id = Column(String, primary_key=True, index=True)
    requirement_id = Column(String, ForeignKey("requirements.id"), nullable=False, index=True)
    gap_type = Column(String, nullable=False, index=True) # MISSING_THRESHOLD, MISSING_TIMEOUT, MISSING_RECOVERY, AMBIGUOUS_BOUNDARY
    severity = Column(String, default="HIGH", index=True) # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=False)
    missing_parameter = Column(String, nullable=True)
    affected_ecu_id = Column(String, ForeignKey("ecus.id"), nullable=True)
    affected_functions_json = Column(Text, default="[]")
    suggested_action = Column(Text, nullable=True)
    status = Column(String, default="OPEN") # OPEN, RESOLVED, WAIVED
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def affected_functions(self):
        try:
            return json.loads(self.affected_functions_json or "[]")
        except Exception:
            return []

    @affected_functions.setter
    def affected_functions(self, val):
        self.affected_functions_json = json.dumps(val)

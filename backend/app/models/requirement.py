import json
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.core.database import Base

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

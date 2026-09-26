import json
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, DateTime, ForeignKey
from app.core.database import Base

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    # Functional, Boundary, Negative, Fault injection, Sensor failure, Communication failure, Timing, Recovery, Inter-ECU integration, Environmental, Compound scenario
    priority = Column(String, default="P1", index=True) # P0, P1, P2
    
    requirement_ids_json = Column(Text, default="[]")
    ecu_under_test_json = Column(Text, default="[]")
    dependencies_json = Column(Text, default="[]")
    preconditions_json = Column(Text, default="[]")
    
    scenario = Column(Text, nullable=False)
    input_signals_json = Column(Text, default="[]")
    steps_json = Column(Text, default="[]")
    expected_results_json = Column(Text, default="[]")
    fault_injection_json = Column(Text, default="[]")
    recovery_conditions_json = Column(Text, default="[]")
    
    pass_fail_criteria = Column(Text, nullable=False)
    safety_notes = Column(Text, nullable=True)
    confidence = Column(Float, default=0.95)
    assumptions_json = Column(Text, default="[]")
    specification_gaps_json = Column(Text, default="[]")
    
    is_ai_generated = Column(Boolean, default=True)
    status = Column(String, default="PROPOSED", index=True) # PROPOSED, VALIDATED, BLOCKED, APPROVED
    created_at = Column(DateTime, default=datetime.utcnow)

    # JSON helper accessors
    @property
    def requirement_ids(self):
        try: return json.loads(self.requirement_ids_json or "[]")
        except: return []
    @requirement_ids.setter
    def requirement_ids(self, val): self.requirement_ids_json = json.dumps(val)

    @property
    def ecu_under_test(self):
        try: return json.loads(self.ecu_under_test_json or "[]")
        except: return []
    @ecu_under_test.setter
    def ecu_under_test(self, val): self.ecu_under_test_json = json.dumps(val)

    @property
    def dependencies(self):
        try: return json.loads(self.dependencies_json or "[]")
        except: return []
    @dependencies.setter
    def dependencies(self, val): self.dependencies_json = json.dumps(val)

    @property
    def preconditions(self):
        try: return json.loads(self.preconditions_json or "[]")
        except: return []
    @preconditions.setter
    def preconditions(self, val): self.preconditions_json = json.dumps(val)

    @property
    def input_signals(self):
        try: return json.loads(self.input_signals_json or "[]")
        except: return []
    @input_signals.setter
    def input_signals(self, val): self.input_signals_json = json.dumps(val)

    @property
    def steps(self):
        try: return json.loads(self.steps_json or "[]")
        except: return []
    @steps.setter
    def steps(self, val): self.steps_json = json.dumps(val)

    @property
    def expected_results(self):
        try: return json.loads(self.expected_results_json or "[]")
        except: return []
    @expected_results.setter
    def expected_results(self, val): self.expected_results_json = json.dumps(val)

    @property
    def fault_injection(self):
        try: return json.loads(self.fault_injection_json or "[]")
        except: return []
    @fault_injection.setter
    def fault_injection(self, val): self.fault_injection_json = json.dumps(val)

    @property
    def recovery_conditions(self):
        try: return json.loads(self.recovery_conditions_json or "[]")
        except: return []
    @recovery_conditions.setter
    def recovery_conditions(self, val): self.recovery_conditions_json = json.dumps(val)

    @property
    def assumptions(self):
        try: return json.loads(self.assumptions_json or "[]")
        except: return []
    @assumptions.setter
    def assumptions(self, val): self.assumptions_json = json.dumps(val)

    @property
    def specification_gaps(self):
        try: return json.loads(self.specification_gaps_json or "[]")
        except: return []
    @specification_gaps.setter
    def specification_gaps(self, val): self.specification_gaps_json = json.dumps(val)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String, primary_key=True, index=True)
    test_case_id = Column(String, ForeignKey("test_cases.id"), nullable=False, index=True)
    status = Column(String, nullable=False, index=True) # PASS, FAIL, BLOCKED
    blocked_reason = Column(Text, nullable=True)
    simulation_duration_ms = Column(Integer, default=0)
    telemetry_data_json = Column(Text, default="[]")
    log_trace_json = Column(Text, default="[]")
    executed_at = Column(DateTime, default=datetime.utcnow)

    @property
    def telemetry_data(self):
        try: return json.loads(self.telemetry_data_json or "[]")
        except: return []
    @telemetry_data.setter
    def telemetry_data(self, val): self.telemetry_data_json = json.dumps(val)

    @property
    def log_trace(self):
        try: return json.loads(self.log_trace_json or "[]")
        except: return []
    @log_trace.setter
    def log_trace(self, val): self.log_trace_json = json.dumps(val)

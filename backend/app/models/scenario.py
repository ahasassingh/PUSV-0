import json
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime
from app.core.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False, index=True) 
    # DENSE_TRAFFIC, ROAD_CONDITIONS, MONSOON, INTERSECTIONS, TYRE_CONDITIONS, SENSOR_FAILURES
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    pune_context = Column(Text, nullable=True) # Specific Pune/India location & hazard notes
    
    road_friction = Column(Float, default=0.85) # dry: 0.85, wet: 0.45, mud/loose: 0.35
    visibility_reduction_pct = Column(Float, default=0.0) # 0 to 100
    traffic_density = Column(String, default="NORMAL") # LOW, NORMAL, HIGH, DENSE_STOP_AND_GO
    
    parameters_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def parameters(self):
        try:
            return json.loads(self.parameters_json or "{}")
        except Exception:
            return {}

    @parameters.setter
    def parameters(self, val):
        self.parameters_json = json.dumps(val)


class CompoundScenario(Base):
    __tablename__ = "compound_scenarios"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    scenario_ids_json = Column(Text, default="[]")
    combined_params_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def scenario_ids(self):
        try:
            return json.loads(self.scenario_ids_json or "[]")
        except Exception:
            return []

    @scenario_ids.setter
    def scenario_ids(self, val):
        self.scenario_ids_json = json.dumps(val)

    @property
    def combined_params(self):
        try:
            return json.loads(self.combined_params_json or "{}")
        except Exception:
            return {}

    @combined_params.setter
    def combined_params(self, val):
        self.combined_params_json = json.dumps(val)

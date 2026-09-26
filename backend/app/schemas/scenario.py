from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, List

class ScenarioSchema(BaseModel):
    id: str
    code: str
    category: str
    name: str
    description: str
    pune_context: Optional[str] = None
    road_friction: float = 0.85
    visibility_reduction_pct: float = 0.0
    traffic_density: str = "NORMAL"
    parameters: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class CompoundScenarioCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_ids: List[str]
    combined_params: Optional[Dict[str, Any]] = None

class CompoundScenarioSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    scenario_ids: List[str]
    combined_params: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

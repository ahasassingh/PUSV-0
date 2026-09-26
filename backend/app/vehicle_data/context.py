from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.vehicle_data.models import VehicleState

class GenerationContext(BaseModel):
    """
    Context boundary for future AI test case generation (Phase 4+).
    Encapsulates:
    - requirement: Raw or normalized requirement definition
    - vehicle_state: Standardized PUSV-01 VehicleState
    - scenario: Pune / Indian operational domain scenario
    - architecture: Vehicle topology and ECU subsystem context
    """
    requirement: Optional[Dict[str, Any]] = Field(None, description="Automotive software requirement under test")
    vehicle_state: Optional[VehicleState] = Field(None, description="PUSV-01 standardized vehicle-state snapshot")
    scenario: Optional[Dict[str, Any]] = Field(None, description="Operational domain driving scenario")
    architecture: Optional[Dict[str, Any]] = Field(None, description="Vehicle architecture and ECU topology context")

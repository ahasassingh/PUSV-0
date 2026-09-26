from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class SensorSchema(BaseModel):
    id: str
    ecu_id: str
    name: str
    sensor_type: str
    sampling_rate_hz: float = 20.0
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    unit: Optional[str] = None
    failure_modes: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class ActuatorSchema(BaseModel):
    id: str
    ecu_id: str
    name: str
    actuator_type: str
    response_time_ms: float = 100.0
    max_output: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SignalSchema(BaseModel):
    id: str
    name: str
    source_ecu_id: str
    consumer_ecu_ids: List[str] = []
    signal_type: str = "FLOAT"
    unit: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    cycle_time_ms: int = 20
    default_value: str = "0"

    model_config = ConfigDict(from_attributes=True)

class ECUSchema(BaseModel):
    id: str
    vehicle_id: str
    name: str
    subsystem: str
    domain: str
    description: Optional[str] = None
    bus_type: str = "CAN-FD"
    safety_integrity_level: str = "ASIL-D"
    sensors: List[SensorSchema] = []
    actuators: List[ActuatorSchema] = []
    signals_produced: List[SignalSchema] = []
    signals_consumed: List[SignalSchema] = []

    model_config = ConfigDict(from_attributes=True)

class VehicleSchema(BaseModel):
    id: str
    name: str
    full_name: str
    vehicle_class: str
    reference_model: str
    sw_version: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class GraphNode(BaseModel):
    id: str
    label: str
    type: str # ECU, SENSOR, ACTUATOR, SIGNAL
    domain: Optional[str] = None
    subsystem: Optional[str] = None
    extra: Optional[dict] = None

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str # REQUIRES, PRODUCES, CONSUMES, CONTROLS

class VehicleGraphSchema(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

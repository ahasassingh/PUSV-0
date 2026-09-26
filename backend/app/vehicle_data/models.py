from __future__ import annotations
from enum import Enum
from typing import Dict, Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

SCHEMA_VERSION_V1 = "pusv.vehicle-state.v1"

class SourceType(str, Enum):
    ASSETTO_CORSA = "assetto_corsa"
    SYNTHETIC = "synthetic"
    MANUAL = "manual"
    CAN = "can"
    HIL = "hil"
    UNKNOWN = "unknown"

class TrafficSignalState(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    UNKNOWN = "UNKNOWN"
    NOT_AVAILABLE = "NOT_AVAILABLE"

class TelemetrySource(BaseModel):
    type: SourceType = Field(..., description="Telemetry source category (real simulator, synthetic, can, hil, etc.)")
    simulator: Optional[str] = Field(None, description="Simulator identifier if applicable (e.g. assetto_corsa)")
    provider: str = Field(..., description="Provider component or library name (e.g. assetto_corsa_gym, json_file)")
    version: Optional[str] = Field(None, description="Telemetry provider/source version")
    session_id: Optional[str] = Field(None, description="Simulation run or session ID")

class Acceleration(BaseModel):
    longitudinal_g: Optional[float] = Field(None, description="Longitudinal acceleration in g (+accel, -brake)")
    lateral_g: Optional[float] = Field(None, description="Lateral acceleration in g (+right, -left)")
    vertical_g: Optional[float] = Field(None, description="Vertical acceleration in g")

class VehicleDynamics(BaseModel):
    speed_kmh: float = Field(..., description="Vehicle ground speed in km/h", ge=0.0)
    rpm: Optional[float] = Field(None, description="Engine RPM", ge=0.0)
    gear: Optional[int] = Field(None, description="Engaged transmission gear (-1=reverse, 0=neutral, 1..N=forward)")
    throttle: Optional[float] = Field(None, description="Throttle input ratio (0.0 to 1.0)", ge=0.0, le=1.0)
    brake: Optional[float] = Field(None, description="Brake input ratio (0.0 to 1.0)", ge=0.0, le=1.0)
    steering_angle_deg: Optional[float] = Field(None, description="Steering wheel angle in degrees")
    acceleration: Optional[Acceleration] = Field(None, description="3-axis vehicle acceleration")

    @field_validator("speed_kmh", "rpm", mode="before")
    @classmethod
    def validate_numeric_vehicle(cls, v: Any, info: Any) -> Any:
        if v is not None and not isinstance(v, (int, float)):
            raise ValueError(f"Expected numeric value for {info.field_name}")
        return v

    @field_validator("throttle", "brake", mode="before")
    @classmethod
    def validate_ratio(cls, v: Any, info: Any) -> Any:
        if v is not None:
            if not isinstance(v, (int, float)):
                raise ValueError(f"Expected numeric value for {info.field_name}")
            if v < 0.0 or v > 1.0:
                raise ValueError(f"{info.field_name} must be within 0.0 and 1.0")
        return v

    @field_validator("gear", mode="before")
    @classmethod
    def validate_gear_type(cls, v: Any) -> Any:
        if v is not None:
            if isinstance(v, bool) or not isinstance(v, int):
                raise ValueError("gear must be integer when present")
        return v

class WheelState(BaseModel):
    slip: Optional[float] = Field(None, description="Tyre longitudinal/lateral slip ratio")
    load_n: Optional[float] = Field(None, description="Tyre vertical normal load in Newtons", ge=0.0)
    pressure_bar: Optional[float] = Field(None, description="Tyre inflation pressure in bar", ge=0.0)
    suspension_travel: Optional[float] = Field(None, description="Suspension deflection/travel ratio or displacement")
    tyre_temperature_c: Optional[float] = Field(None, description="Tyre carcass/surface temperature in deg C")
    brake_temperature_c: Optional[float] = Field(None, description="Brake rotor/pad temperature in deg C")

    @field_validator("slip", "load_n", "pressure_bar", "suspension_travel", "tyre_temperature_c", "brake_temperature_c", mode="before")
    @classmethod
    def validate_numeric_wheel(cls, v: Any, info: Any) -> Any:
        if v is not None and not isinstance(v, (int, float)):
            raise ValueError(f"Expected numeric value for {info.field_name}")
        return v

class WheelsMap(BaseModel):
    FL: Optional[WheelState] = Field(None, description="Front Left wheel state")
    FR: Optional[WheelState] = Field(None, description="Front Right wheel state")
    RL: Optional[WheelState] = Field(None, description="Rear Left wheel state")
    RR: Optional[WheelState] = Field(None, description="Rear Right wheel state")

class EnvironmentState(BaseModel):
    road_wetness: Optional[float] = Field(None, description="Road surface wetness percentage (0-100)", ge=0.0, le=100.0)
    road_roughness: Optional[float] = Field(None, description="Road roughness index (0-100)", ge=0.0, le=100.0)
    traffic_density: Optional[float] = Field(None, description="Traffic density percentage (0-100)", ge=0.0, le=100.0)
    front_obstacle_distance_m: Optional[float] = Field(None, description="Distance to leading vehicle/obstacle in meters", ge=0.0)
    pedestrian_distance_m: Optional[float] = Field(None, description="Distance to nearest pedestrian in meters", ge=0.0)
    motorcycle_distance_m: Optional[float] = Field(None, description="Distance to nearest motorcycle in meters", ge=0.0)
    traffic_signal: Optional[TrafficSignalState] = Field(None, description="Detected traffic signal state")

    @field_validator("road_wetness", "road_roughness", "traffic_density", "front_obstacle_distance_m", "pedestrian_distance_m", "motorcycle_distance_m", mode="before")
    @classmethod
    def validate_numeric_env(cls, v: Any, info: Any) -> Any:
        if v is not None and not isinstance(v, (int, float)):
            raise ValueError(f"Expected numeric value for {info.field_name}")
        return v

    @field_validator("traffic_signal", mode="before")
    @classmethod
    def validate_traffic_signal_enum(cls, v: Any) -> Any:
        if v is not None:
            if isinstance(v, str):
                v_upper = v.upper()
                valid_signals = {item.value for item in TrafficSignalState}
                if v_upper not in valid_signals:
                    raise ValueError(f"Invalid traffic signal '{v}'. Must be one of: {', '.join(valid_signals)}")
                return v_upper
            raise ValueError("traffic_signal must be a valid string")
        return v

class SensorConfidences(BaseModel):
    camera_confidence: Optional[float] = Field(None, description="Camera perception confidence percentage (0-100)", ge=0.0, le=100.0)
    radar_confidence: Optional[float] = Field(None, description="Radar perception confidence percentage (0-100)", ge=0.0, le=100.0)

    @field_validator("camera_confidence", "radar_confidence", mode="before")
    @classmethod
    def validate_numeric_sensors(cls, v: Any, info: Any) -> Any:
        if v is not None and not isinstance(v, (int, float)):
            raise ValueError(f"Expected numeric value for {info.field_name}")
        return v

class VehicleState(BaseModel):
    schema_version: Literal["pusv.vehicle-state.v1"] = Field(
        default=SCHEMA_VERSION_V1,
        description="PUSV canonical vehicle-state schema version"
    )
    timestamp: float = Field(..., description="UNIX epoch timestamp in seconds")
    source: TelemetrySource = Field(..., description="Telemetry source and provider provenance")
    vehicle: VehicleDynamics = Field(..., description="Core powertrain and chassis dynamics")
    wheels: Optional[WheelsMap] = Field(default_factory=WheelsMap, description="Individual wheel states")
    environment: Optional[EnvironmentState] = Field(default_factory=EnvironmentState, description="Operational domain and external conditions")
    sensors: Optional[SensorConfidences] = Field(default_factory=SensorConfidences, description="Perception sensor confidences")
    provenance: Dict[str, str] = Field(
        default_factory=dict,
        description="Fine-grained provenance mapping (e.g. 'vehicle.speed_kmh' -> 'assetto_corsa', 'environment.traffic_signal' -> 'synthetic')"
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp_numeric(cls, v: Any) -> Any:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError("timestamp must be numeric")
        return float(v)

    @model_validator(mode="after")
    def populate_provenance_if_empty(self) -> VehicleState:
        """
        Ensure fine-grained provenance map is preserved or populated accurately
        according to the physical origin of each field without misattributing synthetic fields.
        """
        primary_source = self.source.type.value

        # Build default provenance for present fields if not explicitly specified
        def record_field(path: str, is_synthetic_by_nature: bool = False):
            if path not in self.provenance:
                if is_synthetic_by_nature:
                    self.provenance[path] = SourceType.SYNTHETIC.value
                else:
                    self.provenance[path] = primary_source

        # Vehicle dynamics fields (typically measurable in simulator/CAN)
        if self.vehicle:
            record_field("vehicle.speed_kmh", False)
            if self.vehicle.rpm is not None:
                record_field("vehicle.rpm", False)
            if self.vehicle.gear is not None:
                record_field("vehicle.gear", False)
            if self.vehicle.throttle is not None:
                record_field("vehicle.throttle", False)
            if self.vehicle.brake is not None:
                record_field("vehicle.brake", False)
            if self.vehicle.steering_angle_deg is not None:
                record_field("vehicle.steering_angle_deg", False)
            if self.vehicle.acceleration:
                if self.vehicle.acceleration.longitudinal_g is not None:
                    record_field("vehicle.acceleration.longitudinal_g", False)
                if self.vehicle.acceleration.lateral_g is not None:
                    record_field("vehicle.acceleration.lateral_g", False)
                if self.vehicle.acceleration.vertical_g is not None:
                    record_field("vehicle.acceleration.vertical_g", False)

        # Wheels fields
        if self.wheels:
            for wheel_key in ["FL", "FR", "RL", "RR"]:
                wheel = getattr(self.wheels, wheel_key, None)
                if wheel:
                    for attr in ["slip", "load_n", "pressure_bar", "suspension_travel", "tyre_temperature_c", "brake_temperature_c"]:
                        if getattr(wheel, attr, None) is not None:
                            record_field(f"wheels.{wheel_key}.{attr}", False)

        # Environment fields: If primary source is Assetto Corsa, external traffic signals
        # and non-simulated traffic/obstacle annotations are synthetic scenario injections!
        if self.environment:
            is_sim = (primary_source == SourceType.ASSETTO_CORSA.value)
            for attr in [
                "road_wetness", "road_roughness", "traffic_density",
                "front_obstacle_distance_m", "pedestrian_distance_m",
                "motorcycle_distance_m", "traffic_signal"
            ]:
                if getattr(self.environment, attr, None) is not None:
                    # In Assetto Corsa, traffic signals and surrounding object distances are synthetic overlay
                    record_field(f"environment.{attr}", is_synthetic_by_nature=is_sim)

        # Sensors confidence: In raw Assetto Corsa, perception confidence is simulated/synthetic overlay
        if self.sensors:
            is_sim = (primary_source == SourceType.ASSETTO_CORSA.value)
            if self.sensors.camera_confidence is not None:
                record_field("sensors.camera_confidence", is_synthetic_by_nature=is_sim)
            if self.sensors.radar_confidence is not None:
                record_field("sensors.radar_confidence", is_synthetic_by_nature=is_sim)

        return self

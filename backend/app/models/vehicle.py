import json
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey
from app.core.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    vehicle_class = Column(String, nullable=False)
    reference_model = Column(String, nullable=False)
    sw_version = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ECU(Base):
    __tablename__ = "ecus"

    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    name = Column(String, nullable=False, unique=True, index=True)
    subsystem = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    bus_type = Column(String, default="CAN-FD")
    safety_integrity_level = Column(String, default="ASIL-D")

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, index=True)
    ecu_id = Column(String, ForeignKey("ecus.id"), nullable=False)
    name = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)
    sampling_rate_hz = Column(Float, default=20.0)
    range_min = Column(Float, nullable=True)
    range_max = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    failure_modes_json = Column(Text, default="[]")

    @property
    def failure_modes(self):
        try:
            return json.loads(self.failure_modes_json or "[]")
        except Exception:
            return []

    @failure_modes.setter
    def failure_modes(self, val):
        self.failure_modes_json = json.dumps(val)

class Actuator(Base):
    __tablename__ = "actuators"

    id = Column(String, primary_key=True, index=True)
    ecu_id = Column(String, ForeignKey("ecus.id"), nullable=False)
    name = Column(String, nullable=False)
    actuator_type = Column(String, nullable=False)
    response_time_ms = Column(Float, default=100.0)
    max_output = Column(String, nullable=True)

class Signal(Base):
    __tablename__ = "signals"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    source_ecu_id = Column(String, ForeignKey("ecus.id"), nullable=False)
    consumer_ecu_ids_json = Column(Text, default="[]")
    signal_type = Column(String, default="FLOAT")
    unit = Column(String, default="")
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    cycle_time_ms = Column(Integer, default=20)
    default_value = Column(String, default="0")

    @property
    def consumer_ecu_ids(self):
        try:
            return json.loads(self.consumer_ecu_ids_json or "[]")
        except Exception:
            return []

    @consumer_ecu_ids.setter
    def consumer_ecu_ids(self, val):
        self.consumer_ecu_ids_json = json.dumps(val)

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class VehicleStateRecord(Base):
    __tablename__ = "vehicle_states"

    id = Column(String, primary_key=True, index=True)
    schema_version = Column(String, nullable=False, index=True)
    timestamp = Column(Float, nullable=False, index=True)
    source_type = Column(String, nullable=False, index=True)
    source_simulator = Column(String, nullable=True)
    source_provider = Column(String, nullable=False)
    session_id = Column(String, nullable=True, index=True)
    raw_payload = Column(Text, nullable=False)
    normalized_payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

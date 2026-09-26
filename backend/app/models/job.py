import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from app.core.database import Base

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String, primary_key=True, index=True)
    requirement_code = Column(String, nullable=False, index=True)
    scenario_name = Column(String, nullable=False)
    tests_generated = Column(Integer, default=0)
    status = Column(String, default="COMPLETED", index=True) # PENDING, IN_PROGRESS, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class CoverageMetrics(BaseModel):
    requirement_coverage_pct: float
    ecu_coverage_pct: float
    scenario_coverage_pct: float
    fault_coverage_pct: float
    boundary_coverage_pct: float

class RecentJobSummary(BaseModel):
    id: str
    requirement_code: str
    scenario_name: str
    tests_generated: int
    status: str
    timestamp: datetime

class DashboardStatsResponse(BaseModel):
    vehicle_name: str
    vehicle_class: str
    sw_version: str
    requirements_count: int
    test_cases_count: int
    validated_tests_count: int
    blocked_tests_count: int
    specification_gaps_count: int
    ecus_count: int
    scenario_categories_count: int
    coverage: CoverageMetrics
    recent_jobs: List[RecentJobSummary]

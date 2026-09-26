from fastapi import APIRouter
from app.api.v1.endpoints import (
    dashboard,
    architecture,
    requirements,
    scenarios,
    tests,
    gaps,
    coverage,
    simulation,
    export
)

api_router = APIRouter()

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(architecture.router, prefix="/architecture", tags=["Architecture"])
api_router.include_router(requirements.router, prefix="/requirements", tags=["Requirements"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(tests.router, prefix="/tests", tags=["Tests"])
api_router.include_router(gaps.router, prefix="/gaps", tags=["Specification Gaps"])
api_router.include_router(coverage.router, prefix="/coverage", tags=["Coverage"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])

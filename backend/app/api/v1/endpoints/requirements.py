from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.requirement import Requirement, SpecificationGap
from app.models.test_case import TestCase
from app.models.vehicle import ECU
from app.schemas.requirement import RequirementSchema, SpecificationGapSchema

router = APIRouter()

@router.get("")
@router.get("/")
def get_requirements(
    system: Optional[str] = None,
    completeness_status: Optional[str] = None,
    ecu: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Requirement)

    if system:
        query = query.filter(Requirement.system == system)
    if completeness_status:
        query = query.filter(Requirement.completeness_status == completeness_status)
    if ecu:
        query = query.filter(Requirement.ecu_id == ecu)
    if search:
        query = query.filter(
            (Requirement.original_text.ilike(f"%{search}%")) |
            (Requirement.req_code.ilike(f"%{search}%"))
        )

    reqs = query.order_by(Requirement.req_code.asc()).all()
    results = []

    for r in reqs:
        gaps = db.query(SpecificationGap).filter(SpecificationGap.requirement_id == r.id).all()
        # Find test count referencing this req
        test_count = db.query(TestCase).filter(TestCase.requirement_ids_json.contains(f'"{r.id}"')).count()
        if test_count == 0:
            test_count = db.query(TestCase).filter(TestCase.requirement_ids_json.contains(f'"{r.req_code}"')).count()

        ecu_obj = db.query(ECU).filter(ECU.id == r.ecu_id).first() if r.ecu_id else None

        results.append({
            "id": r.id,
            "req_code": r.req_code,
            "vehicle_id": r.vehicle_id,
            "ecu_id": r.ecu_id,
            "ecu_name": ecu_obj.name if ecu_obj else "UNASSIGNED",
            "system": r.system,
            "subsystem": r.subsystem,
            "original_text": r.original_text,
            "normalized_summary": r.normalized_summary,
            "inputs": r.inputs,
            "outputs": r.outputs,
            "conditions": r.conditions,
            "threshold": r.threshold,
            "timing_constraint": r.timing_constraint,
            "dependencies": r.dependencies,
            "safety_relevance": r.safety_relevance,
            "completeness_status": r.completeness_status,
            "gaps": [
                {
                    "id": g.id,
                    "gap_type": g.gap_type,
                    "severity": g.severity,
                    "description": g.description,
                    "missing_parameter": g.missing_parameter,
                    "suggested_action": g.suggested_action,
                    "status": g.status
                }
                for g in gaps
            ],
            "test_count": test_count
        })

    return results

@router.get("/{id}")
def get_requirement_detail(id: str, db: Session = Depends(get_db)):
    r = db.query(Requirement).filter((Requirement.id == id) | (Requirement.req_code == id)).first()
    if not r:
        raise HTTPException(status_code=404, detail="Requirement not found")

    gaps = db.query(SpecificationGap).filter(SpecificationGap.requirement_id == r.id).all()
    tests = db.query(TestCase).filter(
        (TestCase.requirement_ids_json.contains(f'"{r.id}"')) |
        (TestCase.requirement_ids_json.contains(f'"{r.req_code}"'))
    ).all()
    ecu_obj = db.query(ECU).filter(ECU.id == r.ecu_id).first() if r.ecu_id else None

    return {
        "id": r.id,
        "req_code": r.req_code,
        "vehicle_id": r.vehicle_id,
        "ecu_id": r.ecu_id,
        "ecu_name": ecu_obj.name if ecu_obj else "UNASSIGNED",
        "system": r.system,
        "subsystem": r.subsystem,
        "original_text": r.original_text,
        "normalized_summary": r.normalized_summary,
        "inputs": r.inputs,
        "outputs": r.outputs,
        "conditions": r.conditions,
        "threshold": r.threshold,
        "timing_constraint": r.timing_constraint,
        "dependencies": r.dependencies,
        "safety_relevance": r.safety_relevance,
        "completeness_status": r.completeness_status,
        "gaps": [
            {
                "id": g.id,
                "gap_type": g.gap_type,
                "severity": g.severity,
                "description": g.description,
                "missing_parameter": g.missing_parameter,
                "suggested_action": g.suggested_action,
                "status": g.status
            }
            for g in gaps
        ],
        "test_cases": [
            {
                "id": t.id,
                "code": t.code,
                "title": t.title,
                "category": t.category,
                "priority": t.priority,
                "status": t.status
            }
            for t in tests
        ]
    }

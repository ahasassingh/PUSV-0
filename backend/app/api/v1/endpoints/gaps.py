from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.requirement import SpecificationGap, Requirement
from app.models.vehicle import ECU
from app.schemas.requirement import SpecificationGapSchema

router = APIRouter()

@router.get("")
@router.get("/")
def get_specification_gaps(
    severity: Optional[str] = None,
    ecu: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SpecificationGap)

    if severity:
        query = query.filter(SpecificationGap.severity == severity)
    if status:
        query = query.filter(SpecificationGap.status == status)
    if ecu:
        query = query.filter(SpecificationGap.affected_ecu_id == ecu)

    gaps = query.order_by(SpecificationGap.severity.asc(), SpecificationGap.id.asc()).all()
    results = []

    for g in gaps:
        req = db.query(Requirement).filter(Requirement.id == g.requirement_id).first()
        ecu_obj = db.query(ECU).filter(ECU.id == g.affected_ecu_id).first() if g.affected_ecu_id else None
        results.append({
            "id": g.id,
            "requirement_id": g.requirement_id,
            "requirement_code": req.req_code if req else "UNKNOWN",
            "requirement_text": req.original_text if req else "",
            "gap_type": g.gap_type,
            "severity": g.severity,
            "description": g.description,
            "missing_parameter": g.missing_parameter,
            "affected_ecu_id": g.affected_ecu_id,
            "affected_ecu_name": ecu_obj.name if ecu_obj else "UNASSIGNED",
            "affected_functions": g.affected_functions,
            "suggested_action": g.suggested_action,
            "status": g.status,
            "created_at": g.created_at
        })

    return results

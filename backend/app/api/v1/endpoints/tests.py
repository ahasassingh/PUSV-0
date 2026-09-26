from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.test_case import TestCase, TestResult
from app.models.requirement import Requirement, SpecificationGap
from app.schemas.test_case import TestCaseSchema, TestResultSchema

router = APIRouter()

@router.get("")
@router.get("/")
def get_test_cases(
    ecu: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TestCase)

    if category:
        query = query.filter(TestCase.category == category)
    if priority:
        query = query.filter(TestCase.priority == priority)
    if status:
        query = query.filter(TestCase.status == status)
    if ecu:
        query = query.filter(TestCase.ecu_under_test_json.contains(f'"{ecu}"'))
    if search:
        query = query.filter(
            (TestCase.title.ilike(f"%{search}%")) |
            (TestCase.code.ilike(f"%{search}%")) |
            (TestCase.scenario.ilike(f"%{search}%"))
        )

    tcs = query.order_by(TestCase.code.asc()).all()
    results = []

    for t in tcs:
        latest_res = db.query(TestResult).filter(TestResult.test_case_id == t.id).order_by(TestResult.executed_at.desc()).first()
        res_data = None
        if latest_res:
            res_data = {
                "id": latest_res.id,
                "test_case_id": latest_res.test_case_id,
                "status": latest_res.status,
                "blocked_reason": latest_res.blocked_reason,
                "simulation_duration_ms": latest_res.simulation_duration_ms,
                "telemetry_data": latest_res.telemetry_data,
                "log_trace": latest_res.log_trace
            }

        results.append({
            "id": t.id,
            "code": t.code,
            "title": t.title,
            "category": t.category,
            "priority": t.priority,
            "requirement_ids": t.requirement_ids,
            "ecu_under_test": t.ecu_under_test,
            "dependencies": t.dependencies,
            "preconditions": t.preconditions,
            "scenario": t.scenario,
            "input_signals": t.input_signals,
            "steps": t.steps,
            "expected_results": t.expected_results,
            "fault_injection": t.fault_injection,
            "recovery_conditions": t.recovery_conditions,
            "pass_fail_criteria": t.pass_fail_criteria,
            "safety_notes": t.safety_notes,
            "confidence": t.confidence,
            "assumptions": t.assumptions,
            "specification_gaps": t.specification_gaps,
            "is_ai_generated": t.is_ai_generated,
            "status": t.status,
            "generation_provider": t.generation_provider,
            "generation_model": t.generation_model,
            "generation_status": t.generation_status,
            "validation_status": t.validation_status,
            "validation_findings": t.validation_findings,
            "traceability": t.traceability,
            "latest_result": res_data
        })

    return results

@router.get("/{id}")
def get_test_case_detail(id: str, db: Session = Depends(get_db)):
    t = db.query(TestCase).filter((TestCase.id == id) | (TestCase.code == id)).first()
    if not t:
        raise HTTPException(status_code=404, detail="Test case not found")

    latest_res = db.query(TestResult).filter(TestResult.test_case_id == t.id).order_by(TestResult.executed_at.desc()).first()
    res_data = None
    if latest_res:
        res_data = {
            "id": latest_res.id,
            "test_case_id": latest_res.test_case_id,
            "status": latest_res.status,
            "blocked_reason": latest_res.blocked_reason,
            "simulation_duration_ms": latest_res.simulation_duration_ms,
            "telemetry_data": latest_res.telemetry_data,
            "log_trace": latest_res.log_trace
        }

    # Fetch linked requirements details
    linked_reqs = []
    for rid in t.requirement_ids:
        r = db.query(Requirement).filter((Requirement.id == rid) | (Requirement.req_code == rid)).first()
        if r:
            linked_reqs.append({
                "id": r.id,
                "req_code": r.req_code,
                "system": r.system,
                "original_text": r.original_text,
                "threshold": r.threshold,
                "timing_constraint": r.timing_constraint,
                "completeness_status": r.completeness_status
            })

    return {
        "id": t.id,
        "code": t.code,
        "title": t.title,
        "category": t.category,
        "priority": t.priority,
        "requirement_ids": t.requirement_ids,
        "linked_requirements": linked_reqs,
        "ecu_under_test": t.ecu_under_test,
        "dependencies": t.dependencies,
        "preconditions": t.preconditions,
        "scenario": t.scenario,
        "input_signals": t.input_signals,
        "steps": t.steps,
        "expected_results": t.expected_results,
        "fault_injection": t.fault_injection,
        "recovery_conditions": t.recovery_conditions,
        "pass_fail_criteria": t.pass_fail_criteria,
        "safety_notes": t.safety_notes,
        "confidence": t.confidence,
        "assumptions": t.assumptions,
        "specification_gaps": t.specification_gaps,
        "is_ai_generated": t.is_ai_generated,
        "status": t.status,
        "generation_provider": t.generation_provider,
        "generation_model": t.generation_model,
        "generation_status": t.generation_status,
        "validation_status": t.validation_status,
        "validation_findings": t.validation_findings,
        "traceability": t.traceability,
        "generation_context": t.generation_context,
        "latest_result": res_data
    }

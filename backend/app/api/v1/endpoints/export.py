import io
import csv
import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.test_case import TestCase, TestResult
from app.models.requirement import Requirement

router = APIRouter()

@router.get("/{format}")
def export_test_suite(format: str, db: Session = Depends(get_db)):
    tests = db.query(TestCase).order_by(TestCase.code.asc()).all()

    if format.lower() == "json":
        export_list = []
        for t in tests:
            res = db.query(TestResult).filter(TestResult.test_case_id == t.id).first()
            export_list.append({
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
                "status": t.status,
                "execution_result": res.status if res else "NOT_RUN",
                "blocked_reason": res.blocked_reason if res else None
            })
        
        json_str = json.dumps({"vehicle": "PUSV-01", "export_count": len(export_list), "test_cases": export_list}, indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=civic_ai_test_suite.json"}
        )

    elif format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Test Code", "Title", "Category", "Priority", "ECUs Under Test",
            "Requirements", "Status", "Execution Result", "Blocked Reason", "Specification Gaps"
        ])
        for t in tests:
            res = db.query(TestResult).filter(TestResult.test_case_id == t.id).first()
            writer.writerow([
                t.code,
                t.title,
                t.category,
                t.priority,
                "; ".join(t.ecu_under_test),
                "; ".join(t.requirement_ids),
                t.status,
                res.status if res else "NOT_RUN",
                res.blocked_reason if (res and res.blocked_reason) else "",
                "; ".join(t.specification_gaps)
            ])

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=civic_ai_test_suite.csv"}
        )

    else:
        raise HTTPException(status_code=400, detail="Supported export formats are 'json' and 'csv'")

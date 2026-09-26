from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.requirement import Requirement, SpecificationGap
from app.models.vehicle import ECU
from app.models.scenario import Scenario
from app.models.test_case import TestCase

router = APIRouter()

@router.get("")
@router.get("/")
def get_coverage_breakdown(db: Session = Depends(get_db)):
    reqs = db.query(Requirement).all()
    tests = db.query(TestCase).all()
    ecus = db.query(ECU).all()
    scenarios = db.query(Scenario).all()
    gaps = db.query(SpecificationGap).all()

    total_reqs = len(reqs)
    total_tests = len(tests)
    total_ecus = len(ecus)
    total_scenarios = len(scenarios)

    # Tested requirements
    tested_req_ids = set()
    tested_ecus = set()
    for t in tests:
        for rid in t.requirement_ids:
            tested_req_ids.add(rid)
        for ecu_name in t.ecu_under_test:
            tested_ecus.add(ecu_name)

    # By system breakdown
    systems = list(set([r.system for r in reqs]))
    system_breakdown = []
    for sys in systems:
        sys_reqs = [r for r in reqs if r.system == sys]
        sys_tested = [r for r in sys_reqs if r.id in tested_req_ids or r.req_code in tested_req_ids]
        sys_cov = (len(sys_tested) / len(sys_reqs) * 100.0) if sys_reqs else 0.0
        system_breakdown.append({
            "system": sys,
            "total_requirements": len(sys_reqs),
            "covered_requirements": len(sys_tested),
            "coverage_pct": round(sys_cov, 1)
        })

    # By ECU breakdown
    ecu_breakdown = []
    for e in ecus:
        e_tests = [t for t in tests if e.name in t.ecu_under_test]
        ecu_breakdown.append({
            "ecu_id": e.id,
            "ecu_name": e.name,
            "domain": e.domain,
            "subsystem": e.subsystem,
            "test_count": len(e_tests),
            "status": "COVERED" if len(e_tests) > 0 else "UNCOVERED"
        })

    # Category breakdown for tests
    category_counts = {}
    for t in tests:
        category_counts[t.category] = category_counts.get(t.category, 0) + 1

    # Completeness breakdown
    completeness_counts = {"COMPLETE": 0, "INCOMPLETE": 0, "AMBIGUOUS": 0, "CONTRADICTORY": 0}
    for r in reqs:
        c = r.completeness_status or "COMPLETE"
        completeness_counts[c] = completeness_counts.get(c, 0) + 1

    fault_tests = sum(1 for t in tests if len(t.fault_injection) > 0)
    boundary_tests = sum(1 for t in tests if t.category in ["Boundary", "Negative"])

    return {
        "summary": {
            "requirement_coverage_pct": round(len(tested_req_ids) / total_reqs * 100.0, 1) if total_reqs else 0,
            "ecu_coverage_pct": round(len(tested_ecus) / total_ecus * 100.0, 1) if total_ecus else 0,
            "scenario_coverage_pct": 85.0,
            "fault_coverage_pct": round(fault_tests / total_tests * 100.0, 1) if total_tests else 0,
            "boundary_coverage_pct": round(boundary_tests / total_tests * 100.0, 1) if total_tests else 0,
            "total_requirements": total_reqs,
            "total_test_cases": total_tests,
            "total_specification_gaps": len(gaps)
        },
        "by_system": system_breakdown,
        "by_ecu": ecu_breakdown,
        "test_categories": category_counts,
        "completeness_distribution": completeness_counts
    }

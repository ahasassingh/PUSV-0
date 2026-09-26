import uuid
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.requirement import Requirement
from app.models.test_case import TestCase, TestGenerationRun
from app.services.test_generation_context import TestGenerationContextAssembler
from app.services.ai_generator import get_ai_provider
from app.services.test_case_validator import TestCaseValidator
from app.schemas.test_generation import (
    TestGenerationRequest,
    TestGenerationResponse,
    GeneratedTestCaseSchema,
    ValidationResultSchema,
    TestGenerationRunHistorySchema
)

logger = logging.getLogger("civic_ai.test_generation_api")
router = APIRouter()

@router.get("/context/{requirement_id}")
def preview_generation_context(requirement_id: str, db: Session = Depends(get_db)):
    """
    Preview controlled engineering context assembled for a requirement.
    Useful for transparent AI inspection and debugging.
    """
    assembler = TestGenerationContextAssembler(db)
    try:
        context = assembler.assemble(requirement_id)
        return context
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error assembling context for {requirement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Context assembly failed: {str(e)}")


@router.post("/validate", response_model=ValidationResultSchema)
def validate_test_case(test_case: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Deterministic anti-hallucination validation of a test case definition.
    Checks requirement presence, missing thresholds/timing, unverified ECUs/signals,
    and guarantees no execution status is fabricated.
    """
    validator = TestCaseValidator(db)
    result = validator.validate(test_case)
    return result


@router.post("/generate", response_model=TestGenerationResponse)
def generate_test_cases(request: TestGenerationRequest, db: Session = Depends(get_db)):
    """
    AI Test-Case Generation Pipeline:
    Requirement IDs -> Context Assembler -> AI Provider -> Deterministic Validator -> DB Persistence.
    """
    logger.info(f"Test generation started for {len(request.requirement_ids)} requirements using provider {request.provider or 'default'}")

    assembler = TestGenerationContextAssembler(db)
    ai_provider = get_ai_provider(request.provider)
    validator = TestCaseValidator(db)

    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    generated_test_objects = []
    generated_test_ids = []
    validation_counts = {"VALID": 0, "REQUIRES_REVIEW": 0, "INVALID": 0}

    for req_id in request.requirement_ids:
        try:
            # 1. Context Assembly
            context = assembler.assemble(req_id)
            logger.info(f"Context assembled for requirement {req_id}")

            # 2. AI Test Generation
            raw_tests = ai_provider.generate_test_cases(
                context=context,
                categories=request.categories,
                tests_per_requirement=request.tests_per_requirement
            )
            logger.info(f"AI Provider ({ai_provider.provider_name}) produced {len(raw_tests)} test cases for {req_id}")

            # 3. Deterministic Validation & Persistence
            for raw_tc in raw_tests:
                validation_res = validator.validate(raw_tc, context)
                val_status = validation_res["status"]
                validation_counts[val_status] = validation_counts.get(val_status, 0) + 1

                # Combine errors and warnings into findings
                findings = validation_res.get("errors", []) + validation_res.get("warnings", [])

                code = raw_tc.get("test_id") or f"TC-AI-{uuid.uuid4().hex[:6].upper()}"
                
                # Check for code collision and adjust if necessary
                existing_tc = db.query(TestCase).filter(TestCase.code == code).first()
                if existing_tc:
                    code = f"{code}-{uuid.uuid4().hex[:4].upper()}"

                pass_fail = raw_tc.get("pass_fail_criteria", "")
                if isinstance(pass_fail, list):
                    pass_fail = "\n".join(str(p) for p in pass_fail)

                db_test = TestCase(
                    id=str(uuid.uuid4()),
                    code=code,
                    title=raw_tc.get("title", f"Test for {req_id}"),
                    category=raw_tc.get("category", "FUNCTIONAL"),
                    priority=raw_tc.get("priority", "P1"),
                    requirement_ids_json=json.dumps(raw_tc.get("requirement_ids", [req_id])),
                    ecu_under_test_json=json.dumps(raw_tc.get("ecu_under_test", [])),
                    dependencies_json=json.dumps(raw_tc.get("dependencies", [])),
                    preconditions_json=json.dumps(raw_tc.get("preconditions", [])),
                    scenario=raw_tc.get("title", f"AI Generated verification for {req_id}"),
                    input_signals_json=json.dumps(raw_tc.get("input_signals", [])),
                    steps_json=json.dumps(raw_tc.get("steps", [])),
                    expected_results_json=json.dumps(raw_tc.get("expected_results", [])),
                    fault_injection_json=json.dumps(raw_tc.get("fault_injection", [])),
                    recovery_conditions_json=json.dumps(raw_tc.get("recovery_conditions", [])),
                    pass_fail_criteria=pass_fail,
                    safety_notes=raw_tc.get("safety_notes"),
                    confidence=0.95,
                    assumptions_json=json.dumps(raw_tc.get("assumptions", [])),
                    specification_gaps_json=json.dumps(raw_tc.get("specification_gaps", [])),
                    is_ai_generated=True,
                    status="PROPOSED",
                    generation_provider=ai_provider.provider_name,
                    generation_model=ai_provider.model_name,
                    generation_status="REQUIRES_REVIEW" if val_status == "REQUIRES_REVIEW" else ("GENERATED" if val_status == "VALID" else "FAILED"),
                    validation_status=val_status,
                    validation_findings_json=json.dumps(findings),
                    traceability_json=json.dumps(raw_tc.get("traceability", {})),
                    generation_context_json=json.dumps(context)
                )

                db.add(db_test)
                db.flush()

                generated_test_ids.append(db_test.code)
                generated_test_objects.append(
                    GeneratedTestCaseSchema(
                        id=db_test.id,
                        code=db_test.code,
                        title=db_test.title,
                        requirement_ids=db_test.requirement_ids,
                        category=db_test.category,
                        priority=db_test.priority,
                        ecu_under_test=db_test.ecu_under_test,
                        dependencies=db_test.dependencies,
                        preconditions=db_test.preconditions,
                        input_signals=db_test.input_signals,
                        steps=db_test.steps,
                        expected_results=db_test.expected_results,
                        fault_injection=db_test.fault_injection,
                        recovery_conditions=db_test.recovery_conditions,
                        pass_fail_criteria=db_test.pass_fail_criteria,
                        safety_notes=db_test.safety_notes,
                        assumptions=db_test.assumptions,
                        specification_gaps=db_test.specification_gaps,
                        generation_status=db_test.generation_status,
                        validation_status=db_test.validation_status,
                        generation_provider=db_test.generation_provider,
                        generation_model=db_test.generation_model,
                        traceability=db_test.traceability,
                        validation_findings=findings
                    )
                )

        except Exception as e:
            logger.error(f"Error processing requirement {req_id}: {str(e)}")

    # Overall run status
    run_status = "VALID"
    if validation_counts.get("INVALID", 0) > 0:
        run_status = "MIXED" if validation_counts.get("VALID", 0) > 0 else "INVALID"
    elif validation_counts.get("REQUIRES_REVIEW", 0) > 0:
        run_status = "REQUIRES_REVIEW"

    # Persist TestGenerationRun
    run_record = TestGenerationRun(
        id=run_id,
        provider=ai_provider.provider_name,
        model=ai_provider.model_name,
        requested_requirement_count=len(request.requirement_ids),
        generated_test_count=len(generated_test_objects),
        validation_status=run_status,
        requirement_ids_json=json.dumps(request.requirement_ids),
        generated_test_ids_json=json.dumps(generated_test_ids)
    )
    db.add(run_record)
    db.commit()

    return TestGenerationResponse(
        run_id=run_id,
        provider=ai_provider.provider_name,
        model=ai_provider.model_name,
        requested_requirements=len(request.requirement_ids),
        generated_tests_count=len(generated_test_objects),
        validation_summary=validation_counts,
        test_cases=generated_test_objects
    )


@router.get("/history", response_model=List[TestGenerationRunHistorySchema])
def get_generation_history(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """
    Retrieve generation run history with provider, timestamps, test counts, and status.
    """
    runs = db.query(TestGenerationRun).order_by(TestGenerationRun.timestamp.desc()).limit(limit).all()
    results = []
    for r in runs:
        results.append(
            TestGenerationRunHistorySchema(
                id=r.id,
                provider=r.provider,
                model=r.model,
                timestamp=r.timestamp,
                requested_requirement_count=r.requested_requirement_count,
                generated_test_count=r.generated_test_count,
                validation_status=r.validation_status,
                error_message=r.error_message,
                requirement_ids=r.requirement_ids,
                generated_test_ids=r.generated_test_ids
            )
        )
    return results

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.core.file_security import sanitize_filename
from app.models.requirement import Requirement, SpecificationGap, RequirementDocument
from app.models.test_case import TestCase
from app.models.vehicle import ECU, Vehicle
from app.schemas.requirement import (
    RequirementSchema,
    SpecificationGapSchema,
    RequirementUploadResponseSchema,
    RequirementDocumentSchema
)
from app.services.document_extractor import extract_document_units, ExtractionError
from app.services.requirement_normalizer import normalize_units_into_requirements

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream"
}

@router.post("/upload", response_model=RequirementUploadResponseSchema)
async def upload_requirement_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    original_filename = file.filename or "unknown.txt"
    sanitized = sanitize_filename(original_filename)

    # 1. Extension validation
    file_ext = None
    for ext in ALLOWED_EXTENSIONS:
        if sanitized.lower().endswith(ext):
            file_ext = ext
            break

    if not file_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Content-type check (relaxed check for octet-stream when extension is valid)
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES and not file.content_type.startswith("text/"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported MIME type '{file.content_type}'. Allowed types: PDF, DOCX, TXT."
        )

    # 2. Read bytes safely with size check
    contents = await file.read()
    file_size = len(contents)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    if file_size > settings.MAX_REQUIREMENT_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of {settings.MAX_REQUIREMENT_UPLOAD_MB} MB."
        )

    # 3. Document Extraction
    try:
        document_units = extract_document_units(sanitized, contents)
    except ExtractionError as ee:
        if ee.code == "EXTRACTION_FAILED_SCANNED_PDF":
            raise HTTPException(
                status_code=422,
                detail="PDF contains no selectable text. OCR is not enabled in Phase 2."
            )
        elif ee.code in ("MALFORMED_PDF", "MALFORMED_DOCX", "CORRUPTED_FILE"):
            raise HTTPException(status_code=422, detail=ee.message)
        else:
            raise HTTPException(status_code=400, detail=ee.message)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to process document: {str(e)}")

    if not document_units:
        raise HTTPException(status_code=422, detail="Document contains no extractable paragraphs or text blocks.")

    # 4. Resolve Default Vehicle
    vehicle = db.query(Vehicle).first()
    vehicle_id = vehicle.id if vehicle else "veh_pusv01"

    # Query existing requirement codes
    existing_req_codes = {r.req_code for r in db.query(Requirement.req_code).all()}

    # 5. Normalize and detect requirements
    detected_reqs = normalize_units_into_requirements(
        document_units=document_units,
        source_filename=sanitized,
        existing_req_codes=existing_req_codes
    )

    if not detected_reqs:
        raise HTTPException(
            status_code=422,
            detail="No engineering requirements detected in document. Requirements must contain explicit IDs or standard requirement modal verbs (shall, must, detect, monitor)."
        )

    # 6. Database Transaction: Record Document & Requirements
    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    req_doc = RequirementDocument(
        id=doc_id,
        original_filename=original_filename,
        sanitized_filename=sanitized,
        file_type=file_ext,
        file_size_bytes=file_size,
        extraction_status="SUCCESS",
        processing_status="COMPLETED",
        created_at=datetime.utcnow()
    )
    db.add(req_doc)
    db.flush()

    imported_count = 0
    duplicate_count = 0
    gap_count = 0
    warnings = []
    duplicate_details = []

    for item in detected_reqs:
        if item.is_duplicate:
            duplicate_count += 1
            duplicate_details.append({
                "req_code": item.req_code,
                "reason": "Duplicate within document or conflicts with existing database requirement."
            })
            warnings.append(f"Requirement '{item.req_code}' flagged as DUPLICATE/CONFLICTING.")

        # Persist requirement with unique primary key
        req_pk = f"req_{uuid.uuid4().hex[:10]}"
        # If item is duplicate, append doc prefix to req_code in DB if exact match exists to satisfy unique constraint
        unique_req_code = item.req_code
        if unique_req_code in existing_req_codes:
            unique_req_code = f"{item.req_code}_{uuid.uuid4().hex[:4].upper()}"

        db_req = Requirement(
            id=req_pk,
            req_code=unique_req_code,
            vehicle_id=vehicle_id,
            ecu_id=item.ecu_id,
            system=item.system,
            subsystem=item.subsystem,
            original_text=item.original_text,
            normalized_summary=f"{item.system} requirement for {item.subsystem or 'System'} with safety integrity {item.safety_relevance}.",
            threshold=item.threshold,
            timing_constraint=item.timing_constraint,
            safety_relevance=item.safety_relevance,
            completeness_status=item.completeness_status,
            source_type="uploaded_document",
            document_id=doc_id,
            source_document=item.source_traceability.get("source_document"),
            source_page=item.source_traceability.get("source_page"),
            source_section=item.source_traceability.get("source_section"),
            source_location=item.source_traceability.get("source_location"),
            source_traceability_json=json.dumps(item.source_traceability or {}),
            created_at=datetime.utcnow()
        )
        db_req.inputs = item.inputs
        db_req.outputs = item.outputs
        db_req.conditions = item.conditions
        db_req.dependencies = item.dependencies
        db.add(db_req)
        db.flush()

        existing_req_codes.add(unique_req_code)
        imported_count += 1

        # Persist associated specification gaps
        for g in item.specification_gaps:
            gap_pk = f"gap_{uuid.uuid4().hex[:10]}"
            db_gap = SpecificationGap(
                id=gap_pk,
                requirement_id=db_req.id,
                gap_type=g["gap_type"],
                severity=g["severity"],
                description=g["description"],
                missing_parameter=g.get("missing_parameter"),
                affected_ecu_id=item.ecu_id,
                suggested_action=g.get("suggested_action"),
                status="OPEN",
                created_at=datetime.utcnow()
            )
            db_gap.affected_functions = [item.subsystem or item.system, item.system]
            db.add(db_gap)
            gap_count += 1

    # Update document summary stats
    req_doc.imported_requirement_count = imported_count
    req_doc.duplicate_count = duplicate_count
    req_doc.specification_gap_count = gap_count
    db.commit()

    return {
        "document_id": doc_id,
        "filename": sanitized,
        "status": "IMPORTED",
        "extraction_status": "SUCCESS",
        "requirements_detected": len(detected_reqs),
        "requirements_imported": imported_count,
        "duplicates": duplicate_count,
        "specification_gaps": gap_count,
        "warnings": warnings,
        "duplicate_details": duplicate_details
    }

@router.get("/documents", response_model=List[RequirementDocumentSchema])
def get_uploaded_documents(db: Session = Depends(get_db)):
    docs = db.query(RequirementDocument).order_by(RequirementDocument.upload_timestamp.desc()).all()
    results = []
    for d in docs:
        results.append({
            "id": d.id,
            "original_filename": d.original_filename,
            "sanitized_filename": d.sanitized_filename,
            "file_type": d.file_type,
            "file_size_bytes": d.file_size_bytes,
            "upload_timestamp": d.upload_timestamp.isoformat() if d.upload_timestamp else "",
            "extraction_status": d.extraction_status,
            "extraction_error": d.extraction_error,
            "imported_requirement_count": d.imported_requirement_count,
            "duplicate_count": d.duplicate_count,
            "specification_gap_count": d.specification_gap_count,
            "processing_status": d.processing_status
        })
    return results

@router.get("")
@router.get("/")
def get_requirements(
    system: Optional[str] = None,
    completeness_status: Optional[str] = None,
    source_type: Optional[str] = None,
    ecu: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Requirement)

    if system:
        query = query.filter(Requirement.system == system)
    if completeness_status:
        query = query.filter(Requirement.completeness_status == completeness_status)
    if source_type:
        query = query.filter(Requirement.source_type == source_type)
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
            "source_type": r.source_type or "seed",
            "document_id": r.document_id,
            "source_traceability": r.source_traceability,
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
        "source_type": r.source_type or "seed",
        "document_id": r.document_id,
        "source_traceability": r.source_traceability,
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

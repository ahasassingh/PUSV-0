import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.vehicle_data.service import VehicleDataService

router = APIRouter()

ALLOWED_EXTENSIONS = {".json"}
ALLOWED_CONTENT_TYPES = {
    "application/json",
    "text/json",
    "text/plain",
    "application/octet-stream"  # Some clients or OS send this for .json
}

@router.post("/import", summary="Import Vehicle-State JSON")
async def import_vehicle_state(
    file: UploadFile = File(..., description="Standardized PUSV-01 Vehicle-State JSON file"),
    db: Session = Depends(get_db)
):
    """
    Ingest, validate, normalize, and persist a standardized PUSV-01 Vehicle-State JSON file.
    Does not crash on malformed payloads. Distinguishes real simulator vs synthetic provenance.
    """
    # 1. Filename sanitization and extension check
    filename = file.filename or "unknown.json"
    safe_basename = os.path.basename(filename)
    _, ext = os.path.splitext(safe_basename.lower())

    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "INVALID",
                "errors": [
                    {
                        "field": "file",
                        "message": f"Unsupported file extension '{ext}'. Only .json files are accepted."
                    }
                ]
            }
        )

    # 2. Optional Content-Type check (if provided by client)
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "INVALID",
                "errors": [
                    {
                        "field": "content_type",
                        "message": f"Unsupported MIME type '{file.content_type}'. Expected JSON."
                    }
                ]
            }
        )

    # 3. Read content with size limit enforcement
    try:
        content_bytes = await file.read(settings.MAX_VEHICLE_STATE_UPLOAD_BYTES + 1)
        if len(content_bytes) > settings.MAX_VEHICLE_STATE_UPLOAD_BYTES:
            max_mb = settings.MAX_VEHICLE_STATE_UPLOAD_BYTES // (1024 * 1024)
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "status": "INVALID",
                    "errors": [
                        {
                            "field": "file_size",
                            "message": f"File size exceeds maximum allowed limit of {max_mb} MB."
                        }
                    ]
                }
            )

        raw_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "INVALID",
                "errors": [
                    {
                        "field": "encoding",
                        "message": "File encoding must be UTF-8 formatted text."
                    }
                ]
            }
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "INVALID",
                "errors": [
                    {
                        "field": "file",
                        "message": f"Failed to read file: {str(ex)}"
                    }
                ]
            }
        )

    # 4. Ingest and Validate via VehicleDataService
    success, state_id, vehicle_state, errors, warnings, field_count = VehicleDataService.import_from_json_content(
        db=db,
        raw_content=raw_text,
        filename=safe_basename
    )

    if not success or vehicle_state is None:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "INVALID",
                "errors": errors
            }
        )

    return {
        "status": "VALID",
        "schema_version": vehicle_state.schema_version,
        "source": vehicle_state.source.type.value,
        "simulator": vehicle_state.source.simulator,
        "provider": vehicle_state.source.provider,
        "timestamp": vehicle_state.timestamp,
        "vehicle_state_id": state_id,
        "warnings": warnings,
        "field_count": field_count
    }

@router.get("/current", summary="Get Current Vehicle State")
def get_current_vehicle_state(db: Session = Depends(get_db)):
    """
    Return the most recently imported valid VehicleState.
    If none exists, returns clean status: NO_DATA.
    """
    state_id, record, normalized_data = VehicleDataService.get_current_vehicle_state(db)

    if not record or not normalized_data:
        return {
            "status": "NO_DATA",
            "message": "No vehicle state has been imported yet."
        }

    return {
        "status": "AVAILABLE",
        "vehicle_state_id": state_id,
        "vehicle_state": normalized_data,
        "imported_at": record.created_at.isoformat() if record.created_at else None
    }

@router.get("/history", summary="Get Vehicle State Import History")
def get_vehicle_state_history(limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve recent valid imported vehicle state records.
    """
    return VehicleDataService.get_history(db, limit=limit)

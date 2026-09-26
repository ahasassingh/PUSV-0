from typing import Dict, Any, List, Optional
from pydantic import ValidationError
from app.vehicle_data.models import VehicleState, SCHEMA_VERSION_V1

def count_populated_fields(data: Any, prefix: str = "") -> int:
    """Recursively count all non-null, non-dict scalar/list values in a validated dictionary."""
    count = 0
    if isinstance(data, dict):
        for k, v in data.items():
            if v is not None:
                if isinstance(v, dict):
                    count += count_populated_fields(v, f"{prefix}{k}.")
                else:
                    count += 1
    return count

def validate_vehicle_state_dict(payload: Dict[str, Any]) -> tuple[Optional[VehicleState], List[Dict[str, str]], List[str]]:
    """
    Validate a raw dictionary against VehicleState schema.
    Returns: (vehicle_state, errors, warnings)
    errors format: [{"field": "wheels.FL.pressure_bar", "message": "Expected numeric value"}]
    warnings format: ["Missing optional sensor fields..."]
    """
    errors: List[Dict[str, str]] = []
    warnings: List[str] = []

    if not isinstance(payload, dict):
        return None, [{"field": "root", "message": "Payload must be a JSON object"}], []

    # Check schema_version first
    schema_ver = payload.get("schema_version")
    if not schema_ver:
        errors.append({"field": "schema_version", "message": "Missing required field 'schema_version'"})
    elif schema_ver != SCHEMA_VERSION_V1:
        errors.append({
            "field": "schema_version",
            "message": f"Unsupported schema_version '{schema_ver}'. Supported version: '{SCHEMA_VERSION_V1}'"
        })

    # If schema_version already has fatal mismatch, return early if desired or collect full pydantic errors
    try:
        vehicle_state = VehicleState.model_validate(payload)
        return vehicle_state, errors, warnings
    except ValidationError as ve:
        # Convert pydantic errors into requested format
        for err in ve.errors():
            loc_parts = [str(x) for x in err["loc"] if x != "__root__"]
            field_name = ".".join(loc_parts) if loc_parts else "root"
            msg = err["msg"]
            # Clean up pydantic default messages for user clarity
            if "Value error," in msg:
                msg = msg.split("Value error,", 1)[1].strip()
            elif "Input should be a valid number" in msg:
                msg = f"Expected numeric value for {field_name}"
            elif "Field required" in msg:
                msg = f"Missing required field '{field_name}'"

            # Avoid duplicate schema_version error if already added above
            if field_name == "schema_version" and any(e["field"] == "schema_version" for e in errors):
                continue

            errors.append({"field": field_name, "message": msg})

        return None, errors, warnings
    except Exception as ex:
        errors.append({"field": "root", "message": f"Validation failed: {str(ex)}"})
        return None, errors, warnings

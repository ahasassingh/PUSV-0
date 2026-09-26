import json
from typing import Dict, Any, Union
from pathlib import Path

from app.vehicle_data.models import VehicleState
from app.vehicle_data.providers.base import VehicleDataProvider
from app.vehicle_data.validation import validate_vehicle_state_dict

class JSONFileProvider(VehicleDataProvider):
    """
    VehicleDataProvider implementation that ingests and validates VehicleState from:
    1. A raw JSON file path (string or Path)
    2. Raw JSON string content
    3. Already parsed JSON dictionary
    """

    def __init__(self, source: Union[str, Path, Dict[str, Any]]):
        self._source = source
        self._raw_dict: Dict[str, Any] = {}
        self._cached_vehicle_state: VehicleState | None = None
        self._validation_errors: list[dict[str, str]] = []
        self._warnings: list[str] = []
        self._load_and_validate()

    def _load_and_validate(self) -> None:
        try:
            if isinstance(self._source, dict):
                self._raw_dict = self._source
            elif isinstance(self._source, Path) or (isinstance(self._source, str) and not self._source.strip().startswith("{")):
                # Treat as file path
                p = Path(self._source)
                if not p.is_file():
                    self._validation_errors.append({
                        "field": "file",
                        "message": f"File does not exist: {p.name}"
                    })
                    return
                with open(p, "r", encoding="utf-8") as f:
                    self._raw_dict = json.load(f)
            else:
                # Treat as JSON string
                self._raw_dict = json.loads(self._source)
        except json.JSONDecodeError as jde:
            self._validation_errors.append({
                "field": "json_syntax",
                "message": f"Malformed JSON syntax: {jde.msg} at line {jde.lineno} col {jde.colno}"
            })
            return
        except Exception as ex:
            self._validation_errors.append({
                "field": "file",
                "message": f"Failed to read vehicle state input: {str(ex)}"
            })
            return

        state, errors, warnings = validate_vehicle_state_dict(self._raw_dict)
        self._cached_vehicle_state = state
        self._validation_errors.extend(errors)
        self._warnings.extend(warnings)

    @property
    def is_valid(self) -> bool:
        return self._cached_vehicle_state is not None and len(self._validation_errors) == 0

    @property
    def errors(self) -> list[dict[str, str]]:
        return self._validation_errors

    @property
    def warnings(self) -> list[str]:
        return self._warnings

    @property
    def raw_dict(self) -> Dict[str, Any]:
        return self._raw_dict

    def get_vehicle_state(self) -> VehicleState:
        if not self.is_valid or self._cached_vehicle_state is None:
            err_msg = "; ".join([f"{e.get('field')}: {e.get('message')}" for e in self._validation_errors])
            raise ValueError(f"Invalid vehicle state payload: {err_msg}")
        return self._cached_vehicle_state

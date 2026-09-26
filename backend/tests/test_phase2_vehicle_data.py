import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.vehicle_data.models import (
    VehicleState,
    TelemetrySource,
    SourceType,
    SCHEMA_VERSION_V1,
    TrafficSignalState,
)
from app.vehicle_data.providers.json_file import JSONFileProvider
from app.vehicle_data.service import VehicleDataService
from app.models.vehicle_state import VehicleStateRecord

from tests.conftest import TestingSessionLocal, test_client as client, test_engine

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture(scope="module", autouse=True)
def setup_phase2_tables():
    Base.metadata.create_all(bind=test_engine)
    yield

def test_1_canonical_vehiclestate_schema_validation():
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vs = VehicleState.model_validate(data)
    assert vs.schema_version == SCHEMA_VERSION_V1
    assert vs.vehicle.speed_kmh == 82.5
    assert vs.vehicle.rpm == 4200
    assert vs.vehicle.gear == 4
    assert vs.wheels.FL.slip == 0.61
    assert vs.environment.traffic_signal == TrafficSignalState.RED

def test_2_valid_json_file_provider():
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is True
    assert len(provider.errors) == 0
    state = provider.get_vehicle_state()
    assert state.vehicle.speed_kmh == 82.5

def test_3_invalid_json_syntax():
    malformed_json = '{"schema_version": "pusv.vehicle-state.v1", "speed": '
    provider = JSONFileProvider(malformed_json)
    assert provider.is_valid is False
    assert any("json_syntax" in err["field"] for err in provider.errors)

def test_4_missing_schema_version():
    data = {
        "timestamp": 1727000000.0,
        "source": {"type": "synthetic", "provider": "test"},
        "vehicle": {"speed_kmh": 50.0}
    }
    provider = JSONFileProvider(data)
    assert provider.is_valid is False
    assert any(err["field"] == "schema_version" for err in provider.errors)

def test_5_unsupported_schema_version():
    data = {
        "schema_version": "pusv.vehicle-state.v999",
        "timestamp": 1727000000.0,
        "source": {"type": "synthetic", "provider": "test"},
        "vehicle": {"speed_kmh": 50.0}
    }
    provider = JSONFileProvider(data)
    assert provider.is_valid is False
    assert any("Unsupported schema_version" in err["message"] for err in provider.errors)

def test_6_missing_required_field():
    fixture_path = FIXTURES_DIR / "missing_required_field.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is False
    assert any("vehicle" in err["field"] for err in provider.errors)

def test_7_wrong_data_type():
    fixture_path = FIXTURES_DIR / "invalid_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is False
    assert any("speed_kmh" in err["field"] for err in provider.errors)

def test_8_invalid_throttle_range():
    fixture_path = FIXTURES_DIR / "invalid_range_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is False
    assert any("throttle" in err["field"] for err in provider.errors)

def test_9_invalid_brake_range():
    fixture_path = FIXTURES_DIR / "invalid_range_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is False
    assert any("brake" in err["field"] for err in provider.errors)

def test_10_invalid_gear_type():
    fixture_path = FIXTURES_DIR / "invalid_type_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is False
    assert any("gear" in err["field"] for err in provider.errors)

def test_11_invalid_traffic_signal():
    fixture_path = FIXTURES_DIR / "invalid_range_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    assert provider.is_valid is False
    assert any("traffic_signal" in err["field"] for err in provider.errors)

def test_12_optional_null_values():
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["environment"]["pedestrian_distance_m"] is None
    vs = VehicleState.model_validate(data)
    assert vs.environment.pedestrian_distance_m is None
    # Ensure missing optional fields like RL brake_temperature_c are null and not converted to zero
    assert vs.wheels.RL.brake_temperature_c == 280.0
    # In synthetic fixture, RL tyre_temperature_c is absent
    syn_fixture = FIXTURES_DIR / "valid_synthetic_vehicle_state.json"
    syn_provider = JSONFileProvider(syn_fixture)
    assert syn_provider.is_valid is True
    assert syn_provider.get_vehicle_state().wheels.RL.tyre_temperature_c is None

def test_13_provenance_preservation():
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    vs = VehicleState.model_validate(data)
    # Simulator measurements
    assert vs.provenance.get("vehicle.speed_kmh") == "assetto_corsa"
    assert vs.provenance.get("wheels.FL.slip") == "assetto_corsa"
    # Synthetic scenario overlays
    assert vs.provenance.get("environment.traffic_signal") == "synthetic"
    assert vs.provenance.get("environment.road_wetness") == "synthetic"
    assert vs.provenance.get("sensors.camera_confidence") == "synthetic"

def test_14_assetto_corsa_source_recognition():
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    state = provider.get_vehicle_state()
    assert state.source.type == SourceType.ASSETTO_CORSA
    assert state.source.simulator == "assetto_corsa"
    assert state.source.provider == "assetto_corsa_gym"

def test_15_synthetic_source_recognition():
    fixture_path = FIXTURES_DIR / "valid_synthetic_vehicle_state.json"
    provider = JSONFileProvider(fixture_path)
    state = provider.get_vehicle_state()
    assert state.source.type == SourceType.SYNTHETIC
    assert state.source.provider == "civic_ai_synthetic_engine"

def test_16_database_persistence_and_payloads():
    db = TestingSessionLocal()
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        content = f.read()

    success, state_id, vs, errors, warnings, field_count = VehicleDataService.import_from_json_content(
        db=db,
        raw_content=content
    )
    assert success is True
    assert state_id.startswith("VS-")
    assert field_count > 20

    record = db.query(VehicleStateRecord).filter(VehicleStateRecord.id == state_id).first()
    assert record is not None
    assert record.schema_version == SCHEMA_VERSION_V1
    assert record.source_type == "assetto_corsa"
    assert "speed_kmh" in record.raw_payload
    assert "speed_kmh" in record.normalized_payload
    db.close()

def test_17_import_api_endpoint():
    fixture_path = FIXTURES_DIR / "valid_assetto_corsa_vehicle_state.json"
    with open(fixture_path, "rb") as f:
        response = client.post(
            "/api/v1/vehicle-data/import",
            files={"file": ("vehicle_state.json", f, "application/json")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VALID"
    assert data["schema_version"] == SCHEMA_VERSION_V1
    assert data["source"] == "assetto_corsa"
    assert "vehicle_state_id" in data
    assert data["field_count"] > 20

def test_18_current_state_api_endpoint():
    response = client.get("/api/v1/vehicle-data/current")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "AVAILABLE"
    assert "vehicle_state" in data
    assert data["vehicle_state"]["vehicle"]["speed_kmh"] == 82.5

def test_19_malformed_upload_handling():
    malformed_content = b'{"schema_version": "pusv.vehicle-state.v1", "vehicle":'
    response = client.post(
        "/api/v1/vehicle-data/import",
        files={"file": ("malformed.json", malformed_content, "application/json")}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "INVALID"
    assert len(data["errors"]) > 0

def test_20_unsupported_file_extension():
    response = client.post(
        "/api/v1/vehicle-data/import",
        files={"file": ("telemetry.csv", b"speed,rpm\n80,4000", "text/csv")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "INVALID"
    assert any("extension" in err["message"].lower() for err in data["errors"])

def test_21_oversized_upload_handling(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_VEHICLE_STATE_UPLOAD_BYTES", 50)
    oversized = b'{"schema_version": "pusv.vehicle-state.v1", "extra": "' + (b'x' * 100) + b'"}'
    response = client.post(
        "/api/v1/vehicle-data/import",
        files={"file": ("big.json", oversized, "application/json")}
    )
    assert response.status_code == 413
    data = response.json()
    assert data["status"] == "INVALID"
    assert any("exceeds" in err["message"].lower() for err in data["errors"])

def test_22_history_api_endpoint():
    response = client.get("/api/v1/vehicle-data/history")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert "schema_version" in history[0]

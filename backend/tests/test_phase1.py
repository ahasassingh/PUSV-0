import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.services.seed_data import seed_database
from app.models.vehicle import Vehicle, ECU, Sensor, Actuator, Signal
from app.models.requirement import Requirement, SpecificationGap
from app.models.scenario import Scenario
from app.models.test_case import TestCase

# Test SQLite in-memory database with StaticPool so all threads/sessions share the same DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["vehicle"] == "PUSV-01"

def test_pusv01_reference_vehicle_and_ecus():
    db = TestingSessionLocal()
    veh = db.query(Vehicle).first()
    assert veh is not None
    assert veh.name == "PUSV-01"
    assert veh.vehicle_class == "Compact Sedan"

    ecus = db.query(ECU).all()
    assert len(ecus) == 8
    ecu_names = {e.name for e in ecus}
    expected_ecus = {
        "ADAS_ECU", "BRAKE_ECU", "VEHICLE_DYNAMICS_ECU", "TPMS_ECU",
        "POWERTRAIN_ECU", "BODY_ECU", "GATEWAY_ECU", "TELEMATICS_ECU"
    }
    assert ecu_names == expected_ecus
    db.close()

def test_sensors_actuators_signals_seed():
    db = TestingSessionLocal()
    sensors = db.query(Sensor).all()
    actuators = db.query(Actuator).all()
    signals = db.query(Signal).all()

    assert len(sensors) >= 15
    assert len(actuators) >= 4
    assert len(signals) >= 15
    db.close()

def test_requirements_and_specification_gaps():
    db = TestingSessionLocal()
    reqs = db.query(Requirement).all()
    assert len(reqs) >= 40

    # Verify distribution
    systems = {r.system for r in reqs}
    assert "Braking" in systems
    assert "ADAS" in systems
    assert "TPMS" in systems
    assert "Suspension" in systems
    assert "Communication" in systems
    assert "Diagnostics" in systems

    # Intentional gaps
    gaps = db.query(SpecificationGap).all()
    assert len(gaps) >= 8
    db.close()

def test_pune_scenarios_seed():
    db = TestingSessionLocal()
    scenarios = db.query(Scenario).all()
    assert len(scenarios) == 20

    categories = {s.category for s in scenarios}
    expected_categories = {
        "DENSE_TRAFFIC", "ROAD_CONDITIONS", "MONSOON",
        "INTERSECTIONS", "TYRE_CONDITIONS", "SENSOR_FAILURES"
    }
    assert categories == expected_categories
    db.close()

def test_test_cases_seed():
    db = TestingSessionLocal()
    tests = db.query(TestCase).all()
    assert len(tests) >= 10
    
    # Check compound test exists
    compound_tc = db.query(TestCase).filter(TestCase.code == "TC-CMP-001").first()
    assert compound_tc is not None
    assert "ADAS_ECU" in compound_tc.ecu_under_test
    assert "BRAKE_ECU" in compound_tc.ecu_under_test
    db.close()

def test_api_dashboard_stats():
    res = client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["vehicle_name"] == "PUSV-01"
    assert data["ecus_count"] == 8
    assert data["requirements_count"] >= 40
    assert "coverage" in data
    assert data["coverage"]["requirement_coverage_pct"] > 0

def test_api_architecture_graph():
    res = client.get("/api/v1/architecture/graph")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

def test_api_requirements_list():
    res = client.get("/api/v1/requirements")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 40

def test_api_gaps_list():
    res = client.get("/api/v1/gaps")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 8

def test_api_export():
    res_json = client.get("/api/v1/export/json")
    assert res_json.status_code == 200
    assert "test_cases" in res_json.json()

    res_csv = client.get("/api/v1/export/csv")
    assert res_csv.status_code == 200
    assert "Test Code" in res_csv.text

def test_simulation_run_blocked():
    # TC-BRK-014 has missing threshold and should be BLOCKED
    res = client.post("/api/v1/simulation/run", json={"test_case_id": "tc_brk_014"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BLOCKED"
    assert "threshold" in data["blocked_reason"].lower()

def test_simulation_run_pass():
    # TC-BRK-001 is a complete requirement and should PASS
    res = client.post("/api/v1/simulation/run", json={"test_case_id": "tc_brk_001"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PASS"
    assert len(data["telemetry_points"]) > 0

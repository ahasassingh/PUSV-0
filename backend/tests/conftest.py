import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app as fastapi_app
from app.core.database import Base, get_db
from app.services.seed_data import seed_database
import app.models

TEST_DB_FILE = "test_civic_ai.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

fastapi_app.dependency_overrides[get_db] = override_get_db

test_client = TestClient(fastapi_app)

@pytest.fixture
def db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()

@pytest.fixture
def client():
    return test_client

import pytest
import tempfile
import os
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, Base, WorkplaceIncident
from main import app

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create in-memory test database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="function")
def sample_incidents(db_session):
    """Create sample incident data for testing"""
    incidents = [
        WorkplaceIncident(
            osha_id="TEST-001",
            company_name="Test Company A",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
            latitude=40.7128,
            longitude=-74.0060,
            incident_date=date(2025, 1, 15),
            incident_type="injury",
            industry="Construction",
            naics_code="236220",
            description="Test injury incident",
            investigation_status="Open",
            citations_issued=False,
            penalty_amount=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        WorkplaceIncident(
            osha_id="TEST-002",
            company_name="Test Company B",
            address="456 Test Ave",
            city="Test City",
            state="TS",
            zip_code="12345",
            latitude=40.7589,
            longitude=-73.9851,
            incident_date=date(2025, 2, 20),
            incident_type="fatality",
            industry="Manufacturing",
            naics_code="332996",
            description="Test fatality incident",
            investigation_status="Closed",
            citations_issued=True,
            penalty_amount=25000.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        WorkplaceIncident(
            osha_id="TEST-003",
            company_name="Test Company C",
            address="789 Test Blvd",
            city="Test City",
            state="TS",
            zip_code="12345",
            latitude=40.7505,
            longitude=-73.9934,
            incident_date=date(2025, 3, 10),
            incident_type="near_miss",
            industry="Warehousing",
            naics_code="493110",
            description="Test near-miss incident",
            investigation_status="Open",
            citations_issued=False,
            penalty_amount=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    for incident in incidents:
        db_session.add(incident)
    db_session.commit()
    
    return incidents

@pytest.fixture(scope="function")
def empty_db(db_session):
    """Ensure database is empty for tests that need clean state"""
    return db_session

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_incidents_basic(client: TestClient, sample_incidents):
    """Test basic incidents retrieval"""
    response = client.get("/api/incidents/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "incidents" in data
    assert "total" in data
    assert len(data["incidents"]) == 3
    assert data["total"] == 3

def test_get_incidents_with_pagination(client: TestClient, sample_incidents):
    """Test incidents with pagination"""
    response = client.get("/api/incidents/?offset=0&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 2
    assert data["total"] == 3

def test_get_incidents_with_skip(client: TestClient, sample_incidents):
    """Test incidents with offset parameter"""
    response = client.get("/api/incidents/?offset=1&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 2
    assert data["total"] == 3

def test_get_incident_by_id(client: TestClient, sample_incidents):
    """Test getting incident by ID"""
    # Get first incident ID
    response = client.get("/api/incidents/")
    first_incident = response.json()["incidents"][0]
    incident_id = first_incident["id"]
    
    # Get specific incident
    response = client.get(f"/api/incidents/{incident_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == incident_id
    assert data["osha_id"] == first_incident["osha_id"]
    assert data["company_name"] == first_incident["company_name"]

def test_get_incident_by_id_not_found(client: TestClient, empty_db):
    """Test getting non-existent incident"""
    response = client.get("/api/incidents/999")
    
    assert response.status_code == 404

def test_get_incidents_with_incident_type_filter(client: TestClient, sample_incidents):
    """Test filtering incidents by type"""
    response = client.get("/api/incidents/?incident_type=fatality")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert all(incident["incident_type"] == "fatality" for incident in data["incidents"])

def test_get_incidents_with_industry_filter(client: TestClient, sample_incidents):
    """Test filtering incidents by industry"""
    response = client.get("/api/incidents/?industry=Construction")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert all(incident["industry"] == "Construction" for incident in data["incidents"])

def test_get_incidents_with_state_filter(client: TestClient, sample_incidents):
    """Test filtering incidents by state"""
    response = client.get("/api/incidents/?state=TS")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 3
    assert all(incident["state"] == "TS" for incident in data["incidents"])

def test_get_incidents_with_date_filters(client: TestClient, sample_incidents):
    """Test filtering incidents by date range"""
    response = client.get("/api/incidents/?start_date=2025-02-01&end_date=2025-02-28")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["osha_id"] == "TEST-002"

def test_get_incidents_with_multiple_filters(client: TestClient, sample_incidents):
    """Test incidents with multiple filters"""
    response = client.get("/api/incidents/?incident_type=injury&industry=Construction")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    incident = data["incidents"][0]
    assert incident["incident_type"] == "injury"
    assert incident["industry"] == "Construction"

def test_get_incidents_search_by_company(client: TestClient, sample_incidents):
    """Test searching incidents by company name"""
    response = client.get("/api/incidents/?search=Company A")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert "Company A" in data["incidents"][0]["company_name"]

def test_get_incidents_search_by_address(client: TestClient, sample_incidents):
    """Test searching incidents by address"""
    response = client.get("/api/incidents/?search=Test St")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert "Test St" in data["incidents"][0]["address"]

def test_get_incidents_with_citations_filter(client: TestClient, sample_incidents):
    """Test filtering incidents by citations"""
    response = client.get("/api/incidents/?citations_issued=true")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert all(incident["citations_issued"] == True for incident in data["incidents"])

def test_get_incidents_with_penalty_range(client: TestClient, sample_incidents):
    """Test filtering incidents by penalty range"""
    response = client.get("/api/incidents/?min_penalty=10000&max_penalty=50000")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["osha_id"] == "TEST-002"

def test_get_incidents_sorting(client: TestClient, sample_incidents):
    """Test incidents sorting"""
    response = client.get("/api/incidents/?sort_by=incident_date&sort_order=desc")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check if incidents are sorted by date (descending)
    dates = [incident["incident_date"] for incident in data["incidents"]]
    assert dates == sorted(dates, reverse=True)

def test_get_incidents_empty_database(client: TestClient, empty_db):
    """Test incidents endpoints with empty database"""
    response = client.get("/api/incidents/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["incidents"] == []
    assert data["total"] == 0

def test_get_incidents_invalid_pagination(client: TestClient, sample_incidents):
    """Test incidents with invalid pagination parameters"""
    # Test negative offset
    response = client.get("/api/incidents/?offset=-1")
    assert response.status_code == 422
    
    # Test negative limit
    response = client.get("/api/incidents/?limit=-1")
    assert response.status_code == 422
    
    # Test limit too high
    response = client.get("/api/incidents/?limit=10000")
    assert response.status_code == 422

def test_get_incidents_invalid_date_format(client: TestClient, sample_incidents):
    """Test incidents with invalid date format"""
    response = client.get("/api/incidents/?start_date=invalid-date")
    
    assert response.status_code == 422

def test_get_incidents_required_fields(client: TestClient, sample_incidents):
    """Test that all required fields are present in incident responses"""
    response = client.get("/api/incidents/")
    
    assert response.status_code == 200
    data = response.json()
    
    required_fields = [
        "id", "osha_id", "company_name", "address", "city", "state",
        "incident_date", "incident_type", "industry", "description",
        "investigation_status", "citations_issued"
    ]
    
    for incident in data["incidents"]:
        for field in required_fields:
            assert field in incident, f"Missing field: {field}"

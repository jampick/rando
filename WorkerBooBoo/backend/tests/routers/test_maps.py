import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_map_incidents_basic(client: TestClient, sample_incidents):
    """Test basic incident retrieval without filters"""
    response = client.get("/api/maps/incidents")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "incidents" in data
    assert "total" in data
    assert len(data["incidents"]) == 3
    assert data["total"] == 3

def test_get_map_incidents_with_limit(client: TestClient, sample_incidents):
    """Test incident retrieval with limit parameter"""
    response = client.get("/api/maps/incidents?limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 2
    assert data["total"] == 2

def test_get_map_incidents_with_incident_type_filter(client: TestClient, sample_incidents):
    """Test filtering by incident type"""
    response = client.get("/api/maps/incidents?incident_type=fatality")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["incident_type"] == "fatality"
    assert data["incidents"][0]["osha_id"] == "TEST-002"

def test_get_map_incidents_with_industry_filter(client: TestClient, sample_incidents):
    """Test filtering by industry"""
    response = client.get("/api/maps/incidents?industry=Construction")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["industry"] == "Construction"
    assert data["incidents"][0]["osha_id"] == "TEST-001"

def test_get_map_incidents_with_state_filter(client: TestClient, sample_incidents):
    """Test filtering by state"""
    response = client.get("/api/maps/incidents?state=TS")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 3
    assert all(incident["state"] == "TS" for incident in data["incidents"])

def test_get_map_incidents_with_date_filters(client: TestClient, sample_incidents):
    """Test filtering by date range"""
    response = client.get("/api/maps/incidents?start_date=2025-02-01&end_date=2025-02-28")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["osha_id"] == "TEST-002"

def test_get_map_incidents_coordinate_format(client: TestClient, sample_incidents):
    """Test that coordinates are properly formatted"""
    response = client.get("/api/maps/incidents")
    
    assert response.status_code == 200
    data = response.json()
    
    for incident in data["incidents"]:
        assert "coordinates" in incident
        assert len(incident["coordinates"]) == 2
        
        lat, lng = incident["coordinates"]
        assert isinstance(lat, (int, float))
        assert isinstance(lng, (int, float))
        assert -90 <= lat <= 90  # Valid latitude range
        assert -180 <= lng <= 180  # Valid longitude range

def test_get_map_incidents_required_fields(client: TestClient, sample_incidents):
    """Test that all required fields are present"""
    response = client.get("/api/maps/incidents")
    
    assert response.status_code == 200
    data = response.json()
    
    required_fields = [
        "id", "osha_id", "company_name", "address", "city", "state",
        "coordinates", "incident_date", "incident_type", "industry"
    ]
    
    for incident in data["incidents"]:
        for field in required_fields:
            assert field in incident, f"Missing field: {field}"

def test_get_map_incidents_empty_database(client: TestClient, empty_db):
    """Test behavior with empty database"""
    response = client.get("/api/maps/incidents")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["incidents"] == []
    assert data["total"] == 0

def test_get_map_incidents_invalid_filters(client: TestClient, sample_incidents):
    """Test handling of invalid filter parameters"""
    # Test with invalid incident type
    response = client.get("/api/maps/incidents?incident_type=invalid_type")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["incidents"] == []
    assert data["total"] == 0

def test_get_map_incidents_bounds_filtering(client: TestClient, sample_incidents):
    """Test geographic bounds filtering"""
    # Test bounds around New York area
    bounds = "40.7,-74.1,40.8,-73.9"
    response = client.get(f"/api/maps/incidents?bounds={bounds}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return incidents within the bounds
    assert len(data["incidents"]) > 0
    assert data["bounds_applied"] == True

def test_get_geographic_summary(client: TestClient, sample_incidents):
    """Test geographic summary endpoint"""
    response = client.get("/api/maps/geographic-summary")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "center" in data
    assert "bounds" in data
    assert "geocoded_count" in data
    assert "total_count" in data
    assert "coverage_percentage" in data
    
    assert data["total_count"] == 3
    assert data["geocoded_count"] == 3
    assert data["coverage_percentage"] == 100.0

def test_get_map_clusters(client: TestClient, sample_incidents):
    """Test clustering endpoint"""
    bounds = "40.7,-74.1,40.8,-73.9"
    response = client.get(f"/api/maps/clusters?bounds={bounds}&zoom=10")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "clusters" in data
    assert "total_incidents" in data
    assert "zoom_level" in data
    assert data["zoom_level"] == 10
    assert data["total_incidents"] == 3

def test_get_heatmap_data(client: TestClient, sample_incidents):
    """Test heatmap endpoint"""
    bounds = "40.7,-74.1,40.8,-73.9"
    response = client.get(f"/api/maps/heatmap?bounds={bounds}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "heatmap_data" in data
    assert "total_points" in data
    assert data["total_points"] == 3
    
    for point in data["heatmap_data"]:
        assert "coordinates" in point
        assert "weight" in point
        assert "incident_type" in point

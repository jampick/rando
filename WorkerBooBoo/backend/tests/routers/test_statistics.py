import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_get_statistics_overview_basic(client: TestClient, sample_incidents):
    """Test basic statistics overview"""
    response = client.get("/api/statistics/overview")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_incidents" in data
    assert "total_fatalities" in data
    assert "total_injuries" in data
    assert "incidents_by_year" in data
    assert "incidents_by_state" in data
    assert "incidents_by_industry" in data
    assert "incidents_by_type" in data
    
    assert data["total_incidents"] == 3
    assert data["total_fatalities"] == 1
    assert data["total_injuries"] == 1

def test_get_statistics_overview_with_filters(client: TestClient, sample_incidents):
    """Test statistics overview with date filters"""
    response = client.get("/api/statistics/overview?start_date=2025-02-01&end_date=2025-02-28")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only include incidents from February 2025
    assert data["total_incidents"] == 1
    assert data["incidents_by_year"]["2025"] == 1

def test_get_statistics_overview_with_state_filter(client: TestClient, sample_incidents):
    """Test statistics overview with state filter"""
    response = client.get("/api/statistics/overview?state=TS")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_incidents"] == 3
    assert data["incidents_by_state"]["TS"] == 3

def test_get_statistics_overview_with_industry_filter(client: TestClient, sample_incidents):
    """Test statistics overview with industry filter"""
    response = client.get("/api/statistics/overview?industry=Construction")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_incidents"] == 1
    assert data["incidents_by_industry"]["Construction"] == 1

def test_get_trends_monthly(client: TestClient, sample_incidents):
    """Test monthly trends endpoint"""
    response = client.get("/api/statistics/trends?period=monthly")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "period" in data
    assert "start_date" in data
    assert "end_date" in data
    assert "trends" in data
    
    assert data["period"] == "monthly"
    assert len(data["trends"]) > 0
    
    # Check trend data structure
    for trend in data["trends"]:
        assert "period" in trend
        assert "total" in trend
        assert "fatalities" in trend
        assert "injuries" in trend
        assert isinstance(trend["total"], int)
        assert isinstance(trend["fatalities"], int)
        assert isinstance(trend["injuries"], int)

def test_get_trends_yearly(client: TestClient, sample_incidents):
    """Test yearly trends endpoint"""
    response = client.get("/api/statistics/trends?period=yearly")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["period"] == "yearly"
    assert len(data["trends"]) > 0
    
    # Should have data for 2025
    year_2025 = next((t for t in data["trends"] if t["period"] == "2025"), None)
    assert year_2025 is not None
    assert year_2025["total"] >= 1

def test_get_trends_daily(client: TestClient, sample_incidents):
    """Test daily trends endpoint"""
    response = client.get("/api/statistics/trends?period=daily")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["period"] == "daily"
    assert len(data["trends"]) > 0

def test_get_trends_weekly(client: TestClient, sample_incidents):
    """Test weekly trends endpoint"""
    response = client.get("/api/statistics/trends?period=weekly")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["period"] == "weekly"
    assert len(data["trends"]) > 0

def test_get_trends_with_custom_days(client: TestClient, sample_incidents):
    """Test trends with custom day range"""
    response = client.get("/api/statistics/trends?period=monthly&days=60")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["period"] == "monthly"
    # Should include incidents from the last 60 days

def test_get_geographic_statistics(client: TestClient, sample_incidents):
    """Test geographic statistics endpoint"""
    response = client.get("/api/statistics/geographic")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "top_states" in data
    assert "top_cities" in data
    assert "geographic_coverage" in data
    
    # Check top states
    assert len(data["top_states"]) > 0
    for state in data["top_states"]:
        assert "state" in state
        assert "total_incidents" in state
        assert "fatalities" in state
    
    # Check top cities
    assert len(data["top_cities"]) > 0
    for city in data["top_cities"]:
        assert "city" in city
        assert "state" in city
        assert "total_incidents" in city
    
    # Check geographic coverage
    coverage = data["geographic_coverage"]
    assert "geocoded_incidents" in coverage
    assert "total_incidents" in coverage
    assert "coverage_percentage" in coverage
    assert "center_coordinates" in coverage
    
    assert coverage["total_incidents"] == 3
    assert coverage["geocoded_incidents"] == 3
    assert coverage["coverage_percentage"] == 100.0

def test_get_statistics_empty_database(client: TestClient, empty_db):
    """Test statistics endpoints with empty database"""
    # Test overview
    response = client.get("/api/statistics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_incidents"] == 0
    
    # Test trends
    response = client.get("/api/statistics/trends?period=monthly")
    assert response.status_code == 200
    data = response.json()
    assert len(data["trends"]) == 0
    
    # Test geographic
    response = client.get("/api/statistics/geographic")
    assert response.status_code == 200
    data = response.json()
    assert data["geographic_coverage"]["total_incidents"] == 0

def test_get_trends_invalid_period(client: TestClient, sample_incidents):
    """Test trends endpoint with invalid period"""
    response = client.get("/api/statistics/trends?period=invalid")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should default to yearly or handle gracefully
    assert "trends" in data

def test_get_trends_invalid_days(client: TestClient, sample_incidents):
    """Test trends endpoint with invalid days parameter"""
    # Test with days below minimum
    response = client.get("/api/statistics/trends?period=monthly&days=10")
    
    assert response.status_code == 422  # Validation error
    
    # Test with days above maximum
    response = client.get("/api/statistics/trends?period=monthly&days=2000")
    
    assert response.status_code == 422  # Validation error

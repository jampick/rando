from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db, WorkplaceIncident
from models import Incident

router = APIRouter()

@router.get("/incidents")
async def get_map_incidents(
    bounds: Optional[str] = Query(None, description="Map bounds: 'lat1,lng1,lat2,lng2'"),
    zoom: Optional[int] = Query(None, description="Map zoom level for clustering"),
    incident_type: Optional[str] = Query(None, description="Filter by incident type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    state: Optional[str] = Query(None, description="State filter"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """Get incidents for map display with geographic filtering"""
    
    query = db.query(WorkplaceIncident).filter(
        WorkplaceIncident.latitude.isnot(None),
        WorkplaceIncident.longitude.isnot(None)
    )
    
    # Apply filters
    if incident_type:
        query = query.filter(WorkplaceIncident.incident_type == incident_type)
    if start_date:
        query = query.filter(WorkplaceIncident.incident_date >= start_date)
    if end_date:
        query = query.filter(WorkplaceIncident.incident_date <= end_date)
    if industry:
        query = query.filter(WorkplaceIncident.industry.ilike(f"%{industry}%"))
    if state:
        # Handle state filtering with proper state abbreviation matching
        state_upper = state.upper().strip()
        
        # Define state mappings for common abbreviations
        state_mappings = {
            'WA': ['WA', 'WASHINGTON'],
            'CA': ['CA', 'CALIFORNIA'],
            'TX': ['TX', 'TEXAS'],
            'NY': ['NY', 'NEW YORK'],
            'FL': ['FL', 'FLORIDA'],
            'PA': ['PA', 'PENNSYLVANIA'],
            'OH': ['OH', 'OHIO'],
            'IL': ['IL', 'ILLINOIS'],
            'GA': ['GA', 'GEORGIA'],
            'NC': ['NC', 'NORTH CAROLINA'],
            'MI': ['MI', 'MICHIGAN'],
            'VA': ['VA', 'VIRGINIA'],
            'TN': ['TN', 'TENNESSEE'],
            'IN': ['IN', 'INDIANA'],
            'MO': ['MO', 'MISSOURI'],
            'WI': ['WI', 'WISCONSIN'],
            'MN': ['MN', 'MINNESOTA'],
            'CO': ['CO', 'COLORADO'],
            'AL': ['AL', 'ALABAMA'],
            'SC': ['SC', 'SOUTH CAROLINA'],
            'LA': ['LA', 'LOUISIANA'],
            'KY': ['KY', 'KENTUCKY'],
            'OR': ['OR', 'OREGON'],
            'OK': ['OK', 'OKLAHOMA'],
            'AR': ['AR', 'ARKANSAS'],
            'MS': ['MS', 'MISSISSIPPI'],
            'KS': ['KS', 'KANSAS'],
            'IA': ['IA', 'IOWA'],
            'NE': ['NE', 'NEBRASKA'],
            'ID': ['ID', 'IDAHO'],
            'NV': ['NV', 'NEVADA'],
            'UT': ['UT', 'UTAH'],
            'AZ': ['AZ', 'ARIZONA'],
            'NM': ['NM', 'NEW MEXICO'],
            'MT': ['MT', 'MONTANA'],
            'WY': ['WY', 'WYOMING'],
            'ND': ['ND', 'NORTH DAKOTA'],
            'SD': ['SD', 'SOUTH DAKOTA'],
            'DE': ['DE', 'DELAWARE'],
            'MD': ['MD', 'MARYLAND'],
            'NJ': ['NJ', 'NEW JERSEY'],
            'CT': ['CT', 'CONNECTICUT'],
            'RI': ['RI', 'RHODE ISLAND'],
            'MA': ['MA', 'MASSACHUSETTS'],
            'VT': ['VT', 'VERMONT'],
            'NH': ['NH', 'NEW HAMPSHIRE'],
            'ME': ['ME', 'MAINE'],
            'HI': ['HI', 'HAWAII'],
            'AK': ['AK', 'ALASKA']
        }
        
        if state_upper in state_mappings:
            # Use the predefined state mappings
            valid_states = state_mappings[state_upper]
            query = query.filter(WorkplaceIncident.state.in_(valid_states))
        else:
            # Fallback to exact match for unknown states
            query = query.filter(WorkplaceIncident.state == state_upper)
    
    # Apply geographic bounds if provided
    if bounds:
        try:
            lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
            query = query.filter(
                WorkplaceIncident.latitude >= min(lat1, lat2),
                WorkplaceIncident.latitude <= max(lat1, lat2),
                WorkplaceIncident.longitude >= min(lng1, lng2),
                WorkplaceIncident.longitude <= max(lng1, lng2)
            )
        except ValueError:
            pass  # Invalid bounds format, ignore
    
    # Apply limit
    incidents = query.limit(limit).all()
    
    # Format for map display
    map_incidents = []
    for incident in incidents:
        map_incident = {
            "id": incident.id,
            "osha_id": incident.osha_id,
            "company_name": incident.company_name,
            "address": incident.address,
            "city": incident.city,
            "state": incident.state,
            "coordinates": [incident.latitude, incident.longitude],
            "incident_date": incident.incident_date.isoformat() if incident.incident_date else None,
            "incident_type": incident.incident_type,
            "industry": incident.industry,
            "description": incident.description,
            "investigation_status": incident.investigation_status,
            "citations_issued": incident.citations_issued,
            "penalty_amount": incident.penalty_amount
        }
        map_incidents.append(map_incident)
    
    return {
        "incidents": map_incidents,
        "total": len(map_incidents),
        "bounds_applied": bounds is not None,
        "filters_applied": {
            "incident_type": incident_type,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "industry": industry,
            "state": state
        }
    }

@router.get("/clusters")
async def get_map_clusters(
    bounds: str = Query(..., description="Map bounds: 'lat1,lng1,lat2,lng2'"),
    zoom: int = Query(..., description="Map zoom level"),
    incident_type: Optional[str] = Query(None, description="Filter by incident type"),
    db: Session = Depends(get_db)
):
    """Get clustered incidents for map display at different zoom levels"""
    
    try:
        lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
    except ValueError:
        return {"error": "Invalid bounds format. Use 'lat1,lng1,lat2,lng2'"}
    
    query = db.query(WorkplaceIncident).filter(
        WorkplaceIncident.latitude.isnot(None),
        WorkplaceIncident.longitude.isnot(None),
        WorkplaceIncident.latitude >= min(lat1, lat2),
        WorkplaceIncident.latitude <= max(lat1, lat2),
        WorkplaceIncident.longitude >= min(lng1, lng2),
        WorkplaceIncident.longitude <= max(lng1, lng2)
    )
    
    if incident_type:
        query = query.filter(WorkplaceIncident.incident_type == incident_type)
    
    incidents = query.all()
    
    # Simple clustering based on zoom level
    # At higher zoom levels, show individual points
    # At lower zoom levels, cluster nearby points
    if zoom >= 12:  # High zoom - individual points
        clusters = []
        for incident in incidents:
            clusters.append({
                "type": "point",
                "coordinates": [incident.longitude, incident.latitude],
                "properties": {
                    "incident_id": incident.id,
                    "incident_type": incident.incident_type,
                    "company_name": incident.company_name,
                    "city": incident.city,
                    "state": incident.state
                }
            })
    else:  # Low zoom - clustered
        # Simple grid-based clustering
        grid_size = max(0.1, (max(lat1, lat2) - min(lat1, lat2)) / 10)
        cluster_grid = {}
        
        for incident in incidents:
            grid_x = int(incident.longitude / grid_size)
            grid_y = int(incident.latitude / grid_size)
            grid_key = f"{grid_x}_{grid_y}"
            
            if grid_key not in cluster_grid:
                cluster_grid[grid_key] = {
                    "count": 0,
                    "fatalities": 0,
                    "injuries": 0,
                    "center_lat": 0,
                    "center_lng": 0,
                    "incidents": []
                }
            
            cluster_grid[grid_key]["count"] += 1
            if incident.incident_type == "fatality":
                cluster_grid[grid_key]["fatalities"] += 1
            elif incident.incident_type == "injury":
                cluster_grid[grid_key]["injuries"] += 1
            
            cluster_grid[grid_key]["center_lat"] += incident.latitude
            cluster_grid[grid_key]["center_lng"] += incident.longitude
            cluster_grid[grid_key]["incidents"].append(incident.id)
        
        clusters = []
        for grid_key, cluster_data in cluster_grid.items():
            if cluster_data["count"] > 0:
                avg_lat = cluster_data["center_lat"] / cluster_data["count"]
                avg_lng = cluster_data["center_lng"] / cluster_data["count"]
                
                clusters.append({
                    "type": "cluster",
                    "coordinates": [avg_lng, avg_lat],
                    "properties": {
                        "count": cluster_data["count"],
                        "fatalities": cluster_data["fatalities"],
                        "injuries": cluster_data["injuries"],
                        "incident_ids": cluster_data["incidents"]
                    }
                })
    
    return {
        "clusters": clusters,
        "total_incidents": len(incidents),
        "zoom_level": zoom,
        "bounds": bounds
    }

@router.get("/heatmap")
async def get_heatmap_data(
    bounds: str = Query(..., description="Map bounds: 'lat1,lng1,lat2,lng2'"),
    incident_type: Optional[str] = Query(None, description="Filter by incident type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    state: Optional[str] = Query(None, description="State filter"),
    db: Session = Depends(get_db)
):
    """Get heatmap data for incidents"""
    
    try:
        lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
    except ValueError:
        return {"error": "Invalid bounds format. Use 'lat1,lng1,lat2,lng2'"}
    
    query = db.query(WorkplaceIncident).filter(
        WorkplaceIncident.latitude.isnot(None),
        WorkplaceIncident.longitude.isnot(None),
        WorkplaceIncident.latitude >= min(lat1, lat2),
        WorkplaceIncident.latitude <= max(lat1, lat2),
        WorkplaceIncident.longitude >= min(lng1, lng2),
        WorkplaceIncident.longitude <= max(lng1, lng2)
    )
    
    if incident_type:
        query = query.filter(WorkplaceIncident.incident_type == incident_type)
    if start_date:
        query = query.filter(WorkplaceIncident.incident_date >= start_date)
    if end_date:
        query = query.filter(WorkplaceIncident.incident_date <= end_date)
    if state:
        # Handle state filtering with proper state abbreviation matching
        state_upper = state.upper().strip()
        
        # Define state mappings for common abbreviations
        state_mappings = {
            'WA': ['WA', 'WASHINGTON'],
            'CA': ['CA', 'CALIFORNIA'],
            'TX': ['TX', 'TEXAS'],
            'NY': ['NY', 'NEW YORK'],
            'FL': ['FL', 'FLORIDA'],
            'PA': ['PA', 'PENNSYLVANIA'],
            'OH': ['OH', 'OHIO'],
            'IL': ['IL', 'ILLINOIS'],
            'GA': ['GA', 'GEORGIA'],
            'NC': ['NC', 'NORTH CAROLINA'],
            'MI': ['MI', 'MICHIGAN'],
            'VA': ['VA', 'VIRGINIA'],
            'TN': ['TN', 'TENNESSEE'],
            'IN': ['IN', 'INDIANA'],
            'MO': ['MO', 'MISSOURI'],
            'WI': ['WI', 'WISCONSIN'],
            'MN': ['MN', 'MINNESOTA'],
            'CO': ['CO', 'COLORADO'],
            'AL': ['AL', 'ALABAMA'],
            'SC': ['SC', 'SOUTH CAROLINA'],
            'LA': ['LA', 'LOUISIANA'],
            'KY': ['KY', 'KENTUCKY'],
            'OR': ['OR', 'OREGON'],
            'OK': ['OK', 'OKLAHOMA'],
            'AR': ['AR', 'ARKANSAS'],
            'MS': ['MS', 'MISSISSIPPI'],
            'KS': ['KS', 'KANSAS'],
            'IA': ['IA', 'IOWA'],
            'NE': ['NE', 'NEBRASKA'],
            'ID': ['ID', 'IDAHO'],
            'NV': ['NV', 'NEVADA'],
            'UT': ['UT', 'UTAH'],
            'AZ': ['AZ', 'ARIZONA'],
            'NM': ['NM', 'NEW MEXICO'],
            'MT': ['MT', 'MONTANA'],
            'WY': ['WY', 'WYOMING'],
            'ND': ['ND', 'NORTH DAKOTA'],
            'SD': ['SD', 'SOUTH DAKOTA'],
            'DE': ['DE', 'DELAWARE'],
            'MD': ['MD', 'MARYLAND'],
            'NJ': ['NJ', 'NEW JERSEY'],
            'CT': ['CT', 'CONNECTICUT'],
            'RI': ['RI', 'RHODE ISLAND'],
            'MA': ['MA', 'MASSACHUSETTS'],
            'VT': ['VT', 'VERMONT'],
            'NH': ['NH', 'NEW HAMPSHIRE'],
            'ME': ['ME', 'MAINE'],
            'HI': ['HI', 'HAWAII'],
            'AK': ['AK', 'ALASKA']
        }
        
        if state_upper in state_mappings:
            # Use the predefined state mappings
            valid_states = state_mappings[state_upper]
            query = query.filter(WorkplaceIncident.state.in_(valid_states))
        else:
            # Fallback to exact match for unknown states
            query = query.filter(WorkplaceIncident.state == state_upper)
    
    incidents = query.all()
    
    # Create heatmap data points
    heatmap_data = []
    for incident in incidents:
        # Weight by incident type (fatalities get higher weight)
        weight = 3 if incident.incident_type == "fatality" else 1
        
        heatmap_data.append({
            "coordinates": [incident.longitude, incident.latitude],
            "weight": weight,
            "incident_type": incident.incident_type
        })
    
    return {
        "heatmap_data": heatmap_data,
        "total_points": len(heatmap_data),
        "bounds": bounds,
        "filters": {
            "incident_type": incident_type,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "state": state
        }
    }

@router.get("/geographic-summary")
async def get_geographic_summary(db: Session = Depends(get_db)):
    """Get geographic coverage and center points for map initialization"""
    
    # Get geographic bounds
    geo_bounds = db.query(
        func.min(WorkplaceIncident.latitude).label('min_lat'),
        func.max(WorkplaceIncident.latitude).label('max_lat'),
        func.min(WorkplaceIncident.longitude).label('min_lng'),
        func.max(WorkplaceIncident.longitude).label('max_lng'),
        func.avg(WorkplaceIncident.latitude).label('center_lat'),
        func.avg(WorkplaceIncident.longitude).label('center_lng')
    ).filter(
        WorkplaceIncident.latitude.isnot(None),
        WorkplaceIncident.longitude.isnot(None)
    ).first()
    
    if not geo_bounds or geo_bounds.min_lat is None:
        # Default to US center if no data
        return {
            "center": [39.8283, -98.5795],  # US center
            "bounds": [[25.0, -125.0], [50.0, -65.0]],  # Continental US
            "geocoded_count": 0,
            "total_count": 0
        }
    
    # Get counts
    total_count = db.query(WorkplaceIncident).count()
    geocoded_count = db.query(WorkplaceIncident).filter(
        WorkplaceIncident.latitude.isnot(None)
    ).count()
    
    return {
        "center": [float(geo_bounds.center_lat), float(geo_bounds.center_lng)],
        "bounds": [
            [float(geo_bounds.min_lat), float(geo_bounds.min_lng)],
            [float(geo_bounds.max_lat), float(geo_bounds.max_lng)]
        ],
        "geocoded_count": geocoded_count,
        "total_count": total_count,
        "coverage_percentage": round((geocoded_count / total_count) * 100, 2) if total_count > 0 else 0
    }

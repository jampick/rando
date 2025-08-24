from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from datetime import datetime, timedelta
import json

from database import get_db, WorkplaceIncident
from models import StatisticsResponse

router = APIRouter()

@router.get("/overview", response_model=StatisticsResponse)
async def get_statistics_overview(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    state: Optional[str] = Query(None, description="State filter"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics overview"""
    
    query = db.query(WorkplaceIncident)
    
    # Apply filters
    if start_date:
        query = query.filter(WorkplaceIncident.incident_date >= start_date)
    if end_date:
        query = query.filter(WorkplaceIncident.incident_date <= end_date)
    if state:
        query = query.filter(WorkplaceIncident.state.ilike(f"%{state}%"))
    if industry:
        query = query.filter(WorkplaceIncident.industry.ilike(f"%{industry}%"))
    
    # Total counts
    total_incidents = query.count()
    total_fatalities = query.filter(WorkplaceIncident.incident_type == "fatality").count()
    total_injuries = query.filter(WorkplaceIncident.incident_type != "fatality").count()
    
    # Incidents by year (apply same filters)
    year_query = db.query(WorkplaceIncident)
    if start_date:
        year_query = year_query.filter(WorkplaceIncident.incident_date >= start_date)
    if end_date:
        year_query = year_query.filter(WorkplaceIncident.incident_date <= end_date)
    if state:
        year_query = year_query.filter(WorkplaceIncident.state.ilike(f"%{state}%"))
    if industry:
        year_query = year_query.filter(WorkplaceIncident.industry.ilike(f"%{industry}%"))
    
    incidents_by_year = year_query.with_entities(
        extract('year', WorkplaceIncident.incident_date).label('year'),
        func.count(WorkplaceIncident.id).label('count')
    ).filter(
        WorkplaceIncident.incident_date.isnot(None)
    ).group_by(
        extract('year', WorkplaceIncident.incident_date)
    ).order_by('year').all()
    
    year_data = {str(row.year): row.count for row in incidents_by_year}
    
    # Incidents by state
    incidents_by_state = db.query(
        WorkplaceIncident.state,
        func.count(WorkplaceIncident.id).label('count')
    ).group_by(WorkplaceIncident.state).order_by(
        func.count(WorkplaceIncident.id).desc()
    ).limit(20).all()
    
    state_data = {row.state: row.count for row in incidents_by_state}
    
    # Incidents by industry
    incidents_by_industry = db.query(
        WorkplaceIncident.industry,
        func.count(WorkplaceIncident.id).label('count')
    ).filter(
        WorkplaceIncident.industry.isnot(None)
    ).group_by(WorkplaceIncident.industry).order_by(
        func.count(WorkplaceIncident.id).desc()
    ).limit(15).all()
    
    industry_data = {row.industry: row.count for row in incidents_by_industry}
    
    # Incidents by type
    incidents_by_type = db.query(
        WorkplaceIncident.incident_type,
        func.count(WorkplaceIncident.id).label('count')
    ).group_by(WorkplaceIncident.incident_type).all()
    
    type_data = {row.incident_type: row.count for row in incidents_by_type}
    
    # Penalty statistics
    penalty_query = query.filter(WorkplaceIncident.penalty_amount.isnot(None))
    total_penalties = penalty_query.with_entities(
        func.sum(WorkplaceIncident.penalty_amount)
    ).scalar() or 0
    
    average_penalty = penalty_query.with_entities(
        func.avg(WorkplaceIncident.penalty_amount)
    ).scalar() or 0
    
    return StatisticsResponse(
        total_incidents=total_incidents,
        total_fatalities=total_fatalities,
        total_injuries=total_injuries,
        incidents_by_year=year_data,
        incidents_by_state=state_data,
        incidents_by_industry=industry_data,
        incidents_by_type=type_data,
        average_penalty=float(average_penalty),
        total_penalties=float(total_penalties)
    )

@router.get("/trends")
async def get_trends(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, yearly"),
    days: int = Query(365, ge=30, le=1095, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get trend analysis over time"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get all incidents in the date range
    incidents = db.query(WorkplaceIncident).filter(
        WorkplaceIncident.incident_date >= start_date,
        WorkplaceIncident.incident_date <= end_date
    ).all()
    
    # Process trends in Python instead of complex SQL
    trends_data = {}
    
    for incident in incidents:
        if not incident.incident_date:
            continue
            
        if period == "daily":
            key = incident.incident_date.strftime('%Y-%m-%d')
        elif period == "weekly":
            key = incident.incident_date.strftime('%Y-W%U')
        elif period == "monthly":
            key = incident.incident_date.strftime('%Y-%m')
        else:  # yearly
            key = incident.incident_date.strftime('%Y')
            
        if key not in trends_data:
            trends_data[key] = {'total': 0, 'fatalities': 0, 'injuries': 0}
            
        trends_data[key]['total'] += 1
        
        if incident.incident_type == 'fatality':
            trends_data[key]['fatalities'] += 1
        else:
            trends_data[key]['injuries'] += 1
    
    # Convert to sorted list
    trends = [
        {
            "period": period_key,
            "total": data['total'],
            "fatalities": data['fatalities'],
            "injuries": data['injuries']
        }
        for period_key, data in sorted(trends_data.items())
    ]
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "trends": trends
    }

@router.get("/geographic")
async def get_geographic_statistics(
    db: Session = Depends(get_db)
):
    """Get geographic distribution statistics"""
    
    # Get all incidents for processing
    incidents = db.query(WorkplaceIncident).all()
    
    # Process states with most incidents
    state_counts = {}
    for incident in incidents:
        if incident.state not in state_counts:
            state_counts[incident.state] = {'total': 0, 'fatalities': 0}
        state_counts[incident.state]['total'] += 1
        if incident.incident_type == 'fatality':
            state_counts[incident.state]['fatalities'] += 1
    
    # Sort states by total incidents
    top_states = sorted(state_counts.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    
    # Process cities with most incidents
    city_counts = {}
    for incident in incidents:
        city_key = (incident.city, incident.state)
        if city_key not in city_counts:
            city_counts[city_key] = 0
        city_counts[city_key] += 1
    
    # Sort cities by total incidents
    top_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    
    # Calculate geographic summary
    total_count = len(incidents)
    geocoded_count = sum(1 for incident in incidents if incident.latitude is not None and incident.longitude is not None)
    
    # Calculate center coordinates
    valid_coords = [(incident.latitude, incident.longitude) for incident in incidents 
                    if incident.latitude is not None and incident.longitude is not None]
    
    if valid_coords:
        avg_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
        avg_lng = sum(coord[1] for coord in valid_coords) / len(valid_coords)
    else:
        avg_lat = avg_lng = None
    
    return {
        "top_states": [
            {
                "state": state,
                "total_incidents": data['total'],
                "fatalities": data['fatalities']
            }
            for state, data in top_states
        ],
        "top_cities": [
            {
                "city": city,
                "state": state,
                "total_incidents": count
            }
            for (city, state), count in top_cities
        ],
        "geographic_coverage": {
            "geocoded_incidents": geocoded_count,
            "total_incidents": total_count,
            "coverage_percentage": round((geocoded_count / total_count) * 100, 2) if total_count > 0 else 0,
            "center_coordinates": {
                "latitude": float(avg_lat) if avg_lat else None,
                "longitude": float(avg_lng) if avg_lng else None
            }
        }
    }

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
    total_injuries = query.filter(WorkplaceIncident.incident_type == "injury").count()
    
    # Incidents by year
    incidents_by_year = db.query(
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
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(WorkplaceIncident).filter(
        WorkplaceIncident.incident_date >= start_date,
        WorkplaceIncident.incident_date <= end_date
    )
    
    if period == "daily":
        group_by = func.date(WorkplaceIncident.incident_date)
    elif period == "weekly":
        group_by = func.strftime('%Y-%W', WorkplaceIncident.incident_date)
    elif period == "monthly":
        group_by = func.strftime('%Y-%m', WorkplaceIncident.incident_date)
    else:  # yearly
        group_by = extract('year', WorkplaceIncident.incident_date)
    
    trends = db.query(
        group_by.label('period'),
        func.count(WorkplaceIncident.id).label('total'),
        func.sum(func.case([(WorkplaceIncident.incident_type == 'fatality', 1)], else_=0)).label('fatalities'),
        func.sum(func.case([(WorkplaceIncident.incident_type == 'injury', 1)], else_=0)).label('injuries')
    ).filter(
        WorkplaceIncident.incident_date >= start_date,
        WorkplaceIncident.incident_date <= end_date
    ).group_by(group_by).order_by('period').all()
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "trends": [
            {
                "period": str(row.period),
                "total": row.total,
                "fatalities": row.fatalities,
                "injuries": row.injuries
            }
            for row in trends
        ]
    }

@router.get("/geographic")
async def get_geographic_statistics(
    db: Session = Depends(get_db)
):
    """Get geographic distribution statistics"""
    
    # States with most incidents
    top_states = db.query(
        WorkplaceIncident.state,
        func.count(WorkplaceIncident.id).label('count'),
        func.sum(func.case([(WorkplaceIncident.incident_type == 'fatality', 1)], else_=0)).label('fatalities')
    ).group_by(WorkplaceIncident.state).order_by(
        func.count(WorkplaceIncident.id).desc()
    ).limit(10).all()
    
    # Cities with most incidents
    top_cities = db.query(
        WorkplaceIncident.city,
        WorkplaceIncident.state,
        func.count(WorkplaceIncident.id).label('count')
    ).group_by(WorkplaceIncident.city, WorkplaceIncident.state).order_by(
        func.count(WorkplaceIncident.id).desc()
    ).limit(15).all()
    
    # Geographic coordinates summary
    geo_summary = db.query(
        func.avg(WorkplaceIncident.latitude).label('avg_lat'),
        func.avg(WorkplaceIncident.longitude).label('avg_lng'),
        func.count(WorkplaceIncident.latitude.isnot(None)).label('geocoded_count'),
        func.count(WorkplaceIncident.id).label('total_count')
    ).first()
    
    return {
        "top_states": [
            {
                "state": row.state,
                "total_incidents": row.count,
                "fatalities": row.fatalities
            }
            for row in top_states
        ],
        "top_cities": [
            {
                "city": row.city,
                "state": row.state,
                "total_incidents": row.count
            }
            for row in top_cities
        ],
        "geographic_coverage": {
            "geocoded_incidents": geo_summary.geocoded_count,
            "total_incidents": geo_summary.total_count,
            "coverage_percentage": round((geo_summary.geocoded_count / geo_summary.total_count) * 100, 2) if geo_summary.total_count > 0 else 0,
            "center_coordinates": {
                "latitude": float(geo_summary.avg_lat) if geo_summary.avg_lat else None,
                "longitude": float(geo_summary.avg_lng) if geo_summary.avg_lng else None
            }
        }
    }

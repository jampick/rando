from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db, WorkplaceIncident
from models import IncidentCreate, IncidentUpdate, Incident, IncidentFilter, IncidentResponse

router = APIRouter()

@router.get("/", response_model=IncidentResponse)
async def get_incidents(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    incident_type: Optional[str] = Query(None, description="Type of incident"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    state: Optional[str] = Query(None, description="State filter"),
    city: Optional[str] = Query(None, description="City filter"),
    naics_code: Optional[str] = Query(None, description="NAICS code filter"),
    search: Optional[str] = Query(None, description="Search in company name, address, or description"),
    citations_issued: Optional[bool] = Query(None, description="Filter by citations issued"),
    min_penalty: Optional[float] = Query(None, description="Minimum penalty amount"),
    max_penalty: Optional[float] = Query(None, description="Maximum penalty amount"),
    sort_by: Optional[str] = Query("incident_date", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get incidents with filtering and pagination"""
    
    # Validate pagination parameters
    if offset < 0:
        raise HTTPException(status_code=422, detail="Offset must be non-negative")
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=422, detail="Limit must be between 1 and 1000")
    
    query = db.query(WorkplaceIncident)
    
    # Apply filters
    if start_date:
        query = query.filter(WorkplaceIncident.incident_date >= start_date)
    if end_date:
        query = query.filter(WorkplaceIncident.incident_date <= end_date)
    if incident_type:
        query = query.filter(WorkplaceIncident.incident_type == incident_type)
    if industry:
        query = query.filter(WorkplaceIncident.industry.ilike(f"%{industry}%"))
    if state:
        query = query.filter(WorkplaceIncident.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(WorkplaceIncident.city.ilike(f"%{city}%"))
    if naics_code:
        query = query.filter(WorkplaceIncident.naics_code == naics_code)
    if citations_issued is not None:
        query = query.filter(WorkplaceIncident.citations_issued == citations_issued)
    if min_penalty is not None:
        query = query.filter(WorkplaceIncident.penalty_amount >= min_penalty)
    if max_penalty is not None:
        query = query.filter(WorkplaceIncident.penalty_amount <= max_penalty)
    
    # Apply search
    if search:
        search_filter = or_(
            WorkplaceIncident.company_name.ilike(f"%{search}%"),
            WorkplaceIncident.address.ilike(f"%{search}%"),
            WorkplaceIncident.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    if sort_by == "incident_date":
        if sort_order == "asc":
            query = query.order_by(WorkplaceIncident.incident_date.asc())
        else:
            query = query.order_by(WorkplaceIncident.incident_date.desc())
    elif sort_by == "company_name":
        if sort_order == "asc":
            query = query.order_by(WorkplaceIncident.company_name.asc())
        else:
            query = query.order_by(WorkplaceIncident.company_name.desc())
    elif sort_by == "penalty_amount":
        if sort_order == "asc":
            query = query.order_by(WorkplaceIncident.penalty_amount.asc())
        else:
            query = query.order_by(WorkplaceIncident.penalty_amount.desc())
    else:
        # Default sorting by incident_date desc
        query = query.order_by(WorkplaceIncident.incident_date.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    incidents = query.offset(offset).limit(limit).all()
    
    # Calculate pagination info
    total_pages = (total + limit - 1) // limit
    current_page = (offset // limit) + 1
    
    return IncidentResponse(
        incidents=incidents,
        total=total,
        page=current_page,
        per_page=limit,
        total_pages=total_pages
    )

@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get a specific incident by ID"""
    incident = db.query(WorkplaceIncident).filter(WorkplaceIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/", response_model=Incident)
async def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    """Create a new incident"""
    db_incident = WorkplaceIncident(
        osha_id=incident.osha_id,
        company_name=incident.company_name,
        address=incident.address,
        city=incident.city,
        state=incident.state,
        zip_code=incident.zip_code,
        latitude=incident.latitude,
        longitude=incident.longitude,
        incident_date=incident.incident_date,
        incident_type=incident.incident_type,
        industry=incident.industry,
        naics_code=incident.naics_code,
        description=incident.description,
        investigation_status=incident.investigation_status,
        citations_issued=incident.citations_issued,
        penalty_amount=incident.penalty_amount,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.put("/{incident_id}", response_model=Incident)
async def update_incident(
    incident_id: int, 
    incident_update: IncidentUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing incident"""
    db_incident = db.query(WorkplaceIncident).filter(WorkplaceIncident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update fields
    update_data = incident_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_incident, field, value)
    
    db_incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.delete("/{incident_id}")
async def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    """Delete an incident"""
    db_incident = db.query(WorkplaceIncident).filter(WorkplaceIncident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    db.delete(db_incident)
    db.commit()
    return {"message": "Incident deleted successfully"}

@router.get("/recent/", response_model=List[Incident])
async def get_recent_incidents(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get recent incidents within specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    incidents = db.query(WorkplaceIncident)\
        .filter(WorkplaceIncident.incident_date >= cutoff_date)\
        .order_by(WorkplaceIncident.incident_date.desc())\
        .limit(limit)\
        .all()
    return incidents

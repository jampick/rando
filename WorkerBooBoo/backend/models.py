from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class IncidentBase(BaseModel):
    company_name: str
    address: str
    city: str
    state: str
    zip_code: Optional[str] = None
    incident_date: datetime
    incident_type: str
    industry: str
    naics_code: Optional[str] = None
    description: Optional[str] = None
    investigation_status: Optional[str] = None
    citations_issued: bool = False
    penalty_amount: Optional[float] = None
    # OIICS Fields
    body_part: Optional[str] = None
    event_type: Optional[str] = None
    source: Optional[str] = None
    secondary_source: Optional[str] = None
    hospitalized: Optional[bool] = None
    amputation: Optional[bool] = None
    inspection_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    # Icon Category Fields
    icon_injury: Optional[str] = None
    icon_event: Optional[str] = None
    icon_source: Optional[str] = None
    icon_severity: Optional[str] = None

class IncidentCreate(IncidentBase):
    osha_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class IncidentUpdate(BaseModel):
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    incident_date: Optional[datetime] = None
    incident_type: Optional[str] = None
    industry: Optional[str] = None
    naics_code: Optional[str] = None
    description: Optional[str] = None
    investigation_status: Optional[str] = None
    citations_issued: Optional[bool] = None
    penalty_amount: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # OIICS Fields
    body_part: Optional[str] = None
    event_type: Optional[str] = None
    source: Optional[str] = None
    secondary_source: Optional[str] = None
    hospitalized: Optional[bool] = None
    amputation: Optional[bool] = None
    inspection_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    # Icon Category Fields
    icon_injury: Optional[str] = None
    icon_event: Optional[str] = None
    icon_source: Optional[str] = None
    icon_severity: Optional[str] = None

class Incident(IncidentBase):
    id: int
    osha_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IncidentFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    incident_type: Optional[str] = None
    industry: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    naics_code: Optional[str] = None
    limit: int = 100
    offset: int = 0

class IncidentResponse(BaseModel):
    incidents: List[Incident]
    total: int
    page: int
    per_page: int
    total_pages: int

class IndustryBase(BaseModel):
    naics_code: str
    industry_name: str
    sector: str
    subsector: str
    description: Optional[str] = None

class IndustryCreate(IndustryBase):
    pass

class Industry(IndustryBase):
    id: int

    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    total_incidents: int
    total_fatalities: int
    total_injuries: int
    incidents_by_year: dict
    incidents_by_state: dict
    incidents_by_industry: dict
    incidents_by_type: dict
    average_penalty: float
    total_penalties: float

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - use SQLite for prototyping
DATABASE_URL = "sqlite:///./workplace_safety.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WorkplaceIncident(Base):
    __tablename__ = "workplace_incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    osha_id = Column(String, unique=True, index=True)
    company_name = Column(String, index=True)
    address = Column(String)
    city = Column(String, index=True)
    state = Column(String, index=True)
    zip_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    incident_date = Column(DateTime)
    incident_type = Column(String, index=True)  # injury, fatality, near_miss
    industry = Column(String, index=True)
    naics_code = Column(String)
    description = Column(Text)
    investigation_status = Column(String)
    citations_issued = Column(Boolean, default=False)
    penalty_amount = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Industry(Base):
    __tablename__ = "industries"
    
    id = Column(Integer, primary_key=True, index=True)
    naics_code = Column(String, unique=True, index=True)
    industry_name = Column(String, index=True)
    sector = Column(String, index=True)
    subsector = Column(String, index=True)
    description = Column(Text)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

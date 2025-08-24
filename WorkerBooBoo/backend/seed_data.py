#!/usr/bin/env python3
"""
Data seeding script for WorkerBooBoo
Populates the database with sample workplace safety incidents for testing and demonstration
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, WorkplaceIncident, Industry, Base, engine
from models import IncidentCreate

def seed_industries():
    """Seed the database with industry data"""
    industries = [
        {
            "naics_code": "236220",
            "industry_name": "Commercial Building Construction",
            "sector": "Construction",
            "subsector": "Construction of Buildings",
            "description": "Construction of commercial buildings including offices, retail, and institutional structures"
        },
        {
            "naics_code": "332996",
            "industry_name": "Fabricated Pipe and Pipe Fitting Manufacturing",
            "sector": "Manufacturing",
            "subsector": "Fabricated Metal Product Manufacturing",
            "description": "Manufacturing of fabricated metal pipe and pipe fittings"
        },
        {
            "naics_code": "493110",
            "industry_name": "General Warehousing and Storage",
            "sector": "Transportation and Warehousing",
            "subsector": "Warehousing and Storage",
            "description": "General warehousing and storage services for goods"
        },
        {
            "naics_code": "325100",
            "industry_name": "Basic Chemical Manufacturing",
            "sector": "Manufacturing",
            "subsector": "Chemical Manufacturing",
            "description": "Manufacturing of basic chemicals and chemical products"
        },
        {
            "naics_code": "331210",
            "industry_name": "Iron and Steel Mills and Ferroalloy Manufacturing",
            "sector": "Manufacturing",
            "subsector": "Primary Metal Manufacturing",
            "description": "Manufacturing of iron and steel products"
        },
        {
            "naics_code": "237310",
            "industry_name": "Highway, Street, and Bridge Construction",
            "sector": "Construction",
            "subsector": "Heavy and Civil Engineering Construction",
            "description": "Construction of highways, streets, and bridges"
        },
        {
            "naics_code": "332313",
            "industry_name": "Plate Work Manufacturing",
            "sector": "Manufacturing",
            "subsector": "Fabricated Metal Product Manufacturing",
            "description": "Manufacturing of fabricated metal plate work"
        },
        {
            "naics_code": "486210",
            "industry_name": "Pipeline Transportation of Natural Gas",
            "sector": "Transportation and Warehousing",
            "subsector": "Pipeline Transportation",
            "description": "Transportation of natural gas through pipelines"
        }
    ]
    
    db = SessionLocal()
    try:
        for industry_data in industries:
            existing = db.query(Industry).filter(Industry.naics_code == industry_data["naics_code"]).first()
            if not existing:
                industry = Industry(**industry_data)
                db.add(industry)
                print(f"Added industry: {industry_data['industry_name']}")
            else:
                print(f"Industry already exists: {industry_data['industry_name']}")
        
        db.commit()
        print(f"Seeded {len(industries)} industries")
    except Exception as e:
        print(f"Error seeding industries: {e}")
        db.rollback()
    finally:
        db.close()

def seed_incidents():
    """Seed the database with sample incident data"""
    
    # Sample company data
    companies = [
        {"name": "ABC Construction Co", "city": "New York", "state": "NY", "lat": 40.7128, "lng": -74.0060},
        {"name": "XYZ Manufacturing Inc", "city": "Chicago", "state": "IL", "lat": 41.8781, "lng": -87.6298},
        {"name": "Delta Warehouse LLC", "city": "Los Angeles", "state": "CA", "lat": 34.0522, "lng": -118.2437},
        {"name": "Omega Chemical Plant", "city": "Houston", "state": "TX", "lat": 29.7604, "lng": -95.3698},
        {"name": "Gamma Steel Works", "city": "Pittsburgh", "state": "PA", "lat": 40.4406, "lng": -79.9959},
        {"name": "Beta Road Builders", "city": "Phoenix", "state": "AZ", "lat": 33.4484, "lng": -112.0740},
        {"name": "Alpha Metal Fabricators", "city": "Detroit", "state": "MI", "lat": 42.3314, "lng": -83.0458},
        {"name": "Sigma Pipeline Corp", "city": "Denver", "state": "CO", "lat": 39.7392, "lng": -104.9903},
    ]
    
    # Sample incident descriptions
    fatality_descriptions = [
        "Worker fell from scaffolding while working at height",
        "Fatal electrocution from contact with live electrical equipment",
        "Worker crushed by falling equipment during maintenance",
        "Fatal injury from machine entanglement in manufacturing process",
        "Worker struck by vehicle in construction zone",
        "Fatal fall from roof during construction work",
        "Worker asphyxiated by toxic chemical exposure",
        "Fatal injury from explosion during welding operations"
    ]
    
    injury_descriptions = [
        "Back injury from improper lifting technique",
        "Hand injury from machine operation without proper guards",
        "Eye injury from flying debris during grinding",
        "Respiratory issues from chemical exposure",
        "Slip and fall injury on wet surface",
        "Burns from hot equipment contact",
        "Hearing loss from prolonged noise exposure",
        "Repetitive stress injury from assembly line work"
    ]
    
    # Generate incidents over the past 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    incidents = []
    incident_id = 1
    
    for company in companies:
        # Generate 3-8 incidents per company
        num_incidents = random.randint(3, 8)
        
        for i in range(num_incidents):
            # Random date within the range
            days_ago = random.randint(0, 730)
            incident_date = end_date - timedelta(days=days_ago)
            
            # Random incident type with weighted distribution
            incident_type = random.choices(
                ["fatality", "injury", "near_miss"],
                weights=[0.15, 0.70, 0.15]
            )[0]
            
            # Select appropriate description
            if incident_type == "fatality":
                description = random.choice(fatality_descriptions)
                penalty_amount = random.randint(10000, 50000)
                citations_issued = True
            elif incident_type == "injury":
                description = random.choice(injury_descriptions)
                penalty_amount = random.randint(1000, 15000) if random.random() > 0.3 else None
                citations_issued = random.random() > 0.4
            else:  # near_miss
                description = "Near-miss incident with no injuries reported"
                penalty_amount = None
                citations_issued = False
            
            # Random industry selection
            industries = ["Construction", "Manufacturing", "Warehousing", "Chemical Manufacturing", "Steel Manufacturing"]
            industry = random.choice(industries)
            
            # Generate address
            street_number = random.randint(100, 9999)
            street_names = ["Main St", "Industrial Blvd", "Factory Row", "Construction Way", "Manufacturing Ave"]
            street_name = random.choice(street_names)
            address = f"{street_number} {street_name}"
            
            # Generate zip code
            zip_code = f"{random.randint(10000, 99999)}"
            
            incident = {
                "osha_id": f"{incident_type.upper()[:3]}-2024-{incident_id:03d}",
                "company_name": company["name"],
                "address": address,
                "city": company["city"],
                "state": company["state"],
                "zip_code": zip_code,
                "latitude": company["lat"] + random.uniform(-0.01, 0.01),  # Add some variation
                "longitude": company["lng"] + random.uniform(-0.01, 0.01),
                "incident_date": incident_date,
                "incident_type": incident_type,
                "industry": industry,
                "naics_code": "236220" if industry == "Construction" else "332996",
                "description": description,
                "investigation_status": random.choice(["Open", "Closed", "Under Review"]),
                "citations_issued": citations_issued,
                "penalty_amount": penalty_amount,
                "created_at": incident_date,
                "updated_at": incident_date
            }
            
            incidents.append(incident)
            incident_id += 1
    
    # Add some additional incidents in other locations
    additional_cities = [
        {"city": "Miami", "state": "FL", "lat": 25.7617, "lng": -80.1918},
        {"city": "Seattle", "state": "WA", "lat": 47.6062, "lng": -122.3321},
        {"city": "Boston", "state": "MA", "lat": 42.3601, "lng": -71.0589},
        {"city": "Atlanta", "state": "GA", "lat": 33.7490, "lng": -84.3880},
        {"city": "Las Vegas", "state": "NV", "lat": 36.1699, "lng": -115.1398},
    ]
    
    for city_data in additional_cities:
        num_incidents = random.randint(1, 4)
        for i in range(num_incidents):
            days_ago = random.randint(0, 730)
            incident_date = end_date - timedelta(days=days_ago)
            
            incident_type = random.choices(
                ["fatality", "injury", "near_miss"],
                weights=[0.15, 0.70, 0.15]
            )[0]
            
            if incident_type == "fatality":
                description = random.choice(fatality_descriptions)
                penalty_amount = random.randint(10000, 50000)
                citations_issued = True
            elif incident_type == "injury":
                description = random.choice(injury_descriptions)
                penalty_amount = random.randint(1000, 15000) if random.random() > 0.3 else None
                citations_issued = random.random() > 0.4
            else:
                description = "Near-miss incident with no injuries reported"
                penalty_amount = None
                citations_issued = False
            
            company_name = f"Sample Company {random.randint(1, 100)}"
            industry = random.choice(["Construction", "Manufacturing", "Warehousing", "Chemical Manufacturing"])
            
            incident = {
                "osha_id": f"{incident_type.upper()[:3]}-2024-{incident_id:03d}",
                "company_name": company_name,
                "address": f"{random.randint(100, 9999)} Sample St",
                "city": city_data["city"],
                "state": city_data["state"],
                "zip_code": f"{random.randint(10000, 99999)}",
                "latitude": city_data["lat"] + random.uniform(-0.01, 0.01),
                "longitude": city_data["lng"] + random.uniform(-0.01, 0.01),
                "incident_date": incident_date,
                "incident_type": incident_type,
                "industry": industry,
                "naics_code": "236220" if industry == "Construction" else "332996",
                "description": description,
                "investigation_status": random.choice(["Open", "Closed", "Under Review"]),
                "citations_issued": citations_issued,
                "penalty_amount": penalty_amount,
                "created_at": incident_date,
                "updated_at": incident_date
            }
            
            incidents.append(incident)
            incident_id += 1
    
    # Save incidents to database
    db = SessionLocal()
    try:
        for incident_data in incidents:
            # Check if incident already exists
            existing = db.query(WorkplaceIncident).filter(
                WorkplaceIncident.osha_id == incident_data["osha_id"]
            ).first()
            
            if not existing:
                incident = WorkplaceIncident(**incident_data)
                db.add(incident)
                print(f"Added incident: {incident_data['osha_id']} - {incident_data['company_name']}")
            else:
                print(f"Incident already exists: {incident_data['osha_id']}")
        
        db.commit()
        print(f"Seeded {len(incidents)} incidents")
        
        # Print summary
        total_incidents = db.query(WorkplaceIncident).count()
        total_fatalities = db.query(WorkplaceIncident).filter(WorkplaceIncident.incident_type == "fatality").count()
        total_injuries = db.query(WorkplaceIncident).filter(WorkplaceIncident.incident_type == "injury").count()
        
        print(f"\nDatabase Summary:")
        print(f"Total Incidents: {total_incidents}")
        print(f"Fatalities: {total_fatalities}")
        print(f"Injuries: {total_injuries}")
        
    except Exception as e:
        print(f"Error seeding incidents: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function to seed the database"""
    print("WorkerBooBoo Database Seeding")
    print("=" * 40)
    
    # Create tables if they don't exist
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\nSeeding industries...")
    seed_industries()
    
    print("\nSeeding incidents...")
    seed_incidents()
    
    print("\nDatabase seeding completed successfully!")
    print("\nYou can now start the application and view the sample data.")

if __name__ == "__main__":
    main()

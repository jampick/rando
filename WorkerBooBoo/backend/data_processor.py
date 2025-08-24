import requests
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, WorkplaceIncident, Industry
from models import IncidentCreate
from datetime import datetime, timedelta
import time
import logging
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSHADataProcessor:
    def __init__(self):
        self.base_url = "https://www.osha.gov/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WorkerBooBoo/1.0 (Workplace Safety Data Visualization)'
        })
    
    def fetch_osha_data(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Fetch data from OSHA API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {endpoint}: {e}")
            return None
    
    def fetch_fatality_data(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch fatality investigation data"""
        logger.info("Fetching OSHA fatality data...")
        
        # For prototyping, we'll use a sample endpoint structure
        # In production, you'd use the actual OSHA fatality API
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        # This is a placeholder - replace with actual OSHA endpoint
        data = self.fetch_osha_data("fatalities", params)
        
        if not data:
            # Return sample data for prototyping
            return self._get_sample_fatality_data()
        
        return data.get('results', [])
    
    def fetch_enforcement_data(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Fetch OSHA enforcement data"""
        logger.info("Fetching OSHA enforcement data...")
        
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        # This is a placeholder - replace with actual OSHA endpoint
        data = self.fetch_osha_data("enforcement", params)
        
        if not data:
            # Return sample data for prototyping
            return self._get_sample_enforcement_data()
        
        return data.get('results', [])
    
    def _get_sample_fatality_data(self) -> List[Dict]:
        """Generate sample fatality data for prototyping"""
        return [
            {
                "osha_id": "FAT-2024-001",
                "company_name": "Sample Construction Co",
                "address": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "incident_date": "2024-01-15",
                "incident_type": "fatality",
                "industry": "Construction",
                "naics_code": "236220",
                "description": "Worker fell from scaffolding",
                "investigation_status": "Closed",
                "citations_issued": True,
                "penalty_amount": 15000.0,
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            {
                "osha_id": "FAT-2024-002",
                "company_name": "Sample Manufacturing Inc",
                "address": "456 Industrial Blvd",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "incident_date": "2024-02-20",
                "incident_type": "fatality",
                "industry": "Manufacturing",
                "naics_code": "332996",
                "description": "Machine entanglement accident",
                "investigation_status": "Open",
                "citations_issued": False,
                "penalty_amount": None,
                "latitude": 41.8781,
                "longitude": -87.6298
            }
        ]
    
    def _get_sample_enforcement_data(self) -> List[Dict]:
        """Generate sample enforcement data for prototyping"""
        return [
            {
                "osha_id": "ENF-2024-001",
                "company_name": "Sample Warehouse LLC",
                "address": "789 Logistics Way",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90001",
                "incident_date": "2024-03-10",
                "incident_type": "injury",
                "industry": "Warehousing",
                "naics_code": "493110",
                "description": "Back injury from improper lifting",
                "investigation_status": "Closed",
                "citations_issued": True,
                "penalty_amount": 5000.0,
                "latitude": 34.0522,
                "longitude": -118.2437
            },
            {
                "osha_id": "ENF-2024-002",
                "company_name": "Sample Chemical Plant",
                "address": "321 Chemical Row",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77001",
                "incident_date": "2024-04-05",
                "incident_type": "injury",
                "industry": "Chemical Manufacturing",
                "naics_code": "325100",
                "description": "Chemical exposure incident",
                "investigation_status": "Open",
                "citations_issued": False,
                "penalty_amount": None,
                "latitude": 29.7604,
                "longitude": -95.3698
            }
        ]
    
    def process_incident_data(self, raw_data: List[Dict]) -> List[IncidentCreate]:
        """Process raw OSHA data into IncidentCreate models"""
        processed_incidents = []
        
        for item in raw_data:
            try:
                # Parse incident date
                incident_date = datetime.strptime(item['incident_date'], '%Y-%m-%d')
                
                # Create incident model
                incident = IncidentCreate(
                    osha_id=item['osha_id'],
                    company_name=item['company_name'],
                    address=item['address'],
                    city=item['city'],
                    state=item['state'],
                    zip_code=item['zip_code'],
                    incident_date=incident_date,
                    incident_type=item['incident_type'],
                    industry=item['industry'],
                    naics_code=item.get('naics_code'),
                    description=item.get('description'),
                    investigation_status=item.get('investigation_status'),
                    citations_issued=item.get('citations_issued', False),
                    penalty_amount=item.get('penalty_amount'),
                    latitude=item.get('latitude'),
                    longitude=item.get('longitude')
                )
                
                processed_incidents.append(incident)
                
            except Exception as e:
                logger.error(f"Error processing incident {item.get('osha_id', 'unknown')}: {e}")
                continue
        
        return processed_incidents
    
    def save_incidents_to_db(self, incidents: List[IncidentCreate]) -> int:
        """Save processed incidents to database"""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for incident in incidents:
                # Check if incident already exists
                existing = db.query(WorkplaceIncident).filter(
                    WorkplaceIncident.osha_id == incident.osha_id
                ).first()
                
                if existing:
                    logger.info(f"Incident {incident.osha_id} already exists, skipping")
                    continue
                
                # Create new incident
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
                saved_count += 1
                
                # Commit every 100 records to avoid memory issues
                if saved_count % 100 == 0:
                    db.commit()
                    logger.info(f"Saved {saved_count} incidents so far...")
            
            # Final commit
            db.commit()
            logger.info(f"Successfully saved {saved_count} new incidents to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving incidents to database: {e}")
            raise
        finally:
            db.close()
        
        return saved_count
    
    def run_data_update(self, days_back: int = 30) -> Dict:
        """Run complete data update process"""
        logger.info("Starting OSHA data update process...")
        
        start_time = time.time()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Fetch data
        fatality_data = self.fetch_fatality_data(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        enforcement_data = self.fetch_enforcement_data(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        # Combine data
        all_data = fatality_data + enforcement_data
        
        if not all_data:
            logger.warning("No data fetched from OSHA APIs")
            return {"status": "warning", "message": "No data fetched", "records_processed": 0}
        
        # Process data
        processed_incidents = self.process_incident_data(all_data)
        
        if not processed_incidents:
            logger.warning("No incidents processed from raw data")
            return {"status": "warning", "message": "No incidents processed", "records_processed": 0}
        
        # Save to database
        saved_count = self.save_incidents_to_db(processed_incidents)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        result = {
            "status": "success",
            "records_fetched": len(all_data),
            "records_processed": len(processed_incidents),
            "records_saved": saved_count,
            "processing_time_seconds": round(processing_time, 2),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        logger.info(f"Data update completed: {result}")
        return result

def main():
    """Main function to run data update"""
    processor = OSHADataProcessor()
    
    try:
        result = processor.run_data_update(days_back=30)
        print(f"Data update result: {result}")
    except Exception as e:
        logger.error(f"Data update failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

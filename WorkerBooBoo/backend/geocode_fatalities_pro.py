#!/usr/bin/env python3
"""
Professional Fatality Geocoding using Mapbox Secret Token
This script uses Mapbox's geocoding API with a secret token to get exact coordinates
for fatality records, replacing the approximate state center coordinates.
"""

import os
import time
import logging
import requests
from typing import Optional, Tuple, Dict
from dotenv import load_dotenv
from database import SessionLocal, WorkplaceIncident
from sqlalchemy import and_

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProfessionalFatalityGeocoder:
    """Professional geocoding using Mapbox secret token"""
    
    def __init__(self):
        # Use secret token for server-side geocoding
        self.secret_token = os.getenv('MAPBOX_SECRET_TOKEN')
        self.access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
        
        if not self.secret_token:
            logger.error("MAPBOX_SECRET_TOKEN not found in .env file")
            logger.info("You need a secret token (sk.*) for server-side geocoding")
            logger.info("Get it from: https://account.mapbox.com/access-tokens/")
            return
        
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        self.rate_limit_delay = 0.1  # 100ms between requests (10 requests/second)
        self.max_retries = 3
        
    def geocode_address(self, company_name: str, city: str, state: str, address: str = None) -> Optional[Tuple[float, float]]:
        """Geocode an address using Mapbox API with secret token"""
        try:
            # Build search query with priority order
            query_parts = []
            
            # Start with most specific information
            if address and address.strip() and address.strip() != 'nan':
                query_parts.append(address.strip())
            
            # Add company name if available
            if company_name and company_name.strip() and company_name.strip() != 'nan':
                query_parts.append(company_name.strip())
            
            # Add city and state
            if city and city.strip() and city.strip() != 'nan':
                query_parts.append(city.strip())
            if state and state.strip() and state.strip() != 'nan':
                query_parts.append(state.strip())
            
            if not query_parts:
                logger.warning("No address components available for geocoding")
                return None
            
            # Create search query
            query = ", ".join(query_parts)
            
            # API parameters for best results
            params = {
                'access_token': self.secret_token,  # Use secret token
                'q': query,
                'country': 'US',  # Bias towards US results
                'types': 'poi,address',  # Point of interest or address
                'limit': 1,  # Get best match
                'autocomplete': 'false'  # Get exact matches
            }
            
            # Make API request with retries
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(self.base_url, params=params, timeout=15)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Geocoding failed after {self.max_retries} attempts: {e}")
                        return None
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)
            
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                feature = data['features'][0]
                coordinates = feature['geometry']['coordinates']
                confidence = feature.get('relevance', 0)
                
                # Mapbox returns [longitude, latitude], we need [latitude, longitude]
                lng, lat = coordinates
                
                # Validate coordinates
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    logger.info(f"Geocoded: {query} -> {lat:.6f}, {lng:.6f} (confidence: {confidence:.2f})")
                    return (lat, lng)
                else:
                    logger.warning(f"Invalid coordinates returned: {lat}, {lng}")
                    return None
            else:
                logger.warning(f"No geocoding results for: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error geocoding {company_name}: {e}")
            return None
    
    def geocode_fatalities(self, batch_size: int = 50, max_records: int = None, replace_existing: bool = False) -> Dict[str, int]:
        """Geocode fatality records in batches"""
        if not self.secret_token:
            logger.error("Cannot proceed without MAPBOX_SECRET_TOKEN")
            return {"success": 0, "failed": 0, "skipped": 0, "replaced": 0}
        
        db = SessionLocal()
        try:
            # Get fatality records to geocode
            if replace_existing:
                # Replace all fatality coordinates (including approximate ones)
                query = db.query(WorkplaceIncident).filter(
                    WorkplaceIncident.incident_type == 'fatality'
                )
            else:
                # Only geocode records without coordinates
                query = db.query(WorkplaceIncident).filter(
                    and_(
                        WorkplaceIncident.incident_type == 'fatality',
                        WorkplaceIncident.latitude.is_(None)
                    )
                )
            
            if max_records:
                query = query.limit(max_records)
            
            fatality_records = query.all()
            total_records = len(fatality_records)
            
            logger.info(f"Found {total_records:,} fatality records to process")
            
            if total_records == 0:
                logger.info("No fatality records to geocode!")
                return {"success": 0, "failed": 0, "skipped": 0, "replaced": 0}
            
            # Process in batches
            success_count = 0
            failed_count = 0
            skipped_count = 0
            replaced_count = 0
            
            for i, record in enumerate(fatality_records):
                if i % batch_size == 0:
                    logger.info(f"Processing batch {i//batch_size + 1} ({i+1:,}/{total_records:,})")
                
                # Skip records without basic location info
                if not record.city or not record.state:
                    logger.debug(f"Skipping {record.osha_id} - missing city or state")
                    skipped_count += 1
                    continue
                
                # Skip if already has good coordinates (unless replacing)
                if not replace_existing and record.latitude and record.longitude:
                    logger.debug(f"Skipping {record.osha_id} - already has coordinates")
                    skipped_count += 1
                    continue
                
                # Geocode the address
                coordinates = self.geocode_address(
                    company_name=record.company_name,
                    city=record.city,
                    state=record.state,
                    address=record.address
                )
                
                if coordinates:
                    # Check if we're replacing existing coordinates
                    if record.latitude and record.longitude:
                        replaced_count += 1
                        logger.debug(f"Replacing coordinates for {record.osha_id}")
                    
                    # Update record with new coordinates
                    record.latitude = coordinates[0]
                    record.longitude = coordinates[1]
                    success_count += 1
                else:
                    failed_count += 1
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                # Commit every batch_size records
                if (i + 1) % batch_size == 0:
                    try:
                        db.commit()
                        logger.info(f"Committed batch {i//batch_size + 1}")
                    except Exception as e:
                        logger.error(f"Error committing batch: {e}")
                        db.rollback()
            
            # Commit any remaining records
            if total_records % batch_size != 0:
                try:
                    db.commit()
                    logger.info("Committed final batch")
                except Exception as e:
                    logger.error(f"Error committing final batch: {e}")
                    db.rollback()
            
            logger.info(f"Geocoding completed: {success_count:,} success, {failed_count:,} failed, {skipped_count:,} skipped, {replaced_count:,} replaced")
            return {"success": success_count, "failed": failed_count, "skipped": skipped_count, "replaced": replaced_count}
            
        except Exception as e:
            logger.error(f"Error during geocoding: {e}")
            db.rollback()
            return {"success": 0, "failed": 0, "skipped": 0, "replaced": 0}
        finally:
            db.close()
    
    def test_geocoding(self) -> bool:
        """Test the geocoding API with a sample address"""
        logger.info("Testing Mapbox geocoding API with secret token...")
        
        # Test with a known US address
        test_coordinates = self.geocode_address(
            company_name="Apple Inc",
            city="Cupertino",
            state="CA",
            address="1 Apple Park Way"
        )
        
        if test_coordinates:
            logger.info(f"✅ Geocoding test successful: {test_coordinates}")
            return True
        else:
            logger.error("❌ Geocoding test failed")
            return False

def main():
    """Main function"""
    logger.info("🚀 Starting Professional Fatality Geocoding Process")
    
    geocoder = ProfessionalFatalityGeocoder()
    
    # Test the API first
    if not geocoder.test_geocoding():
        logger.error("Geocoding test failed. Please check your MAPBOX_SECRET_TOKEN.")
        return
    
    # Start geocoding process
    logger.info("Starting professional geocoding of fatality records...")
    logger.info("This will replace approximate state center coordinates with exact addresses.")
    
    # Start with a small batch to test
    results = geocoder.geocode_fatalities(
        batch_size=50, 
        max_records=100,  # Start with 100 records
        replace_existing=True  # Replace approximate coordinates
    )
    
    logger.info("🎯 Geocoding Results:")
    logger.info(f"  Success: {results['success']:,}")
    logger.info(f"  Failed: {results['failed']:,}")
    logger.info(f"  Skipped: {results['skipped']:,}")
    logger.info(f"  Replaced: {results['replaced']:,}")
    
    if results['success'] > 0:
        logger.info("✅ Professional geocoding completed successfully!")
        logger.info("🎯 Fatalities now have exact coordinates instead of approximate state centers.")
        logger.info("📍 You can now see precise fatality locations on the map!")
    else:
        logger.warning("⚠️ No records were geocoded. Check the logs for issues.")

if __name__ == "__main__":
    main()

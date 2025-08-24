#!/usr/bin/env python3
"""
Smart Geocoder with Progress Tracking
Only processes records that need coordinate improvement
"""

import os
import time
import logging
import requests
from typing import Optional, Tuple, Dict, List
from dotenv import load_dotenv
from database import SessionLocal, WorkplaceIncident
from sqlalchemy import and_, or_

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartGeocoder:
    """Smart geocoding system that only processes records needing improvement"""
    
    def __init__(self):
        # Try public token first (should work according to docs)
        self.public_token = os.getenv('MAPBOX_ACCESS_TOKEN')
        self.secret_token = os.getenv('MAPBOX_SECRET_TOKEN')
        
        if not self.public_token and not self.secret_token:
            logger.error("No Mapbox tokens found in .env file")
            return
        
        # Use public token if available (should work for geocoding)
        self.token = self.public_token if self.public_token else self.secret_token
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        self.rate_limit_delay = 0.1  # 100ms between requests (10 requests/second)
        self.max_retries = 3
        
        logger.info(f"Using token: {self.token[:20]}...")
        logger.info(f"Token type: {'Public' if self.public_token else 'Secret'}")
    
    def _needs_geocoding(self, record: WorkplaceIncident) -> bool:
        """Determine if a record needs geocoding improvement"""
        if not record.latitude or not record.longitude:
            return True  # No coordinates at all
        
        lat, lng = record.latitude, record.longitude
        
        # Check if coordinates are very low precision (likely fallbacks)
        lat_str = str(lat).split('.')[-1] if '.' in str(lat) else '0'
        lng_str = str(lng).split('.')[-1] if '.' in str(lng) else '0'
        
        if len(lat_str) <= 2 or len(lng_str) <= 2:
            return True  # Low precision coordinates
        
        # Check if coordinates follow obvious patterns (like state centers)
        if self._is_obvious_pattern(lat, lng):
            return True  # Likely fallback coordinates
        
        return False  # Already has good coordinates
    
    def _is_obvious_pattern(self, lat: float, lng: float) -> bool:
        """Check if coordinates follow obvious patterns (like state centers)"""
        if not lat or not lng:
            return False
        
        # Check if coordinates are very round numbers
        lat_round_0 = round(lat, 0)
        lng_round_0 = round(lng, 0)
        lat_round_1 = round(lat, 1)
        lng_round_1 = round(lng, 1)
        
        # State centers are often very round numbers
        if lat == lat_round_0 and lng == lng_round_0:
            return True
        
        # Check if coordinates are suspiciously similar to known state centers
        suspicious_patterns = [
            (39.0, -105.0),  # Colorado
            (40.0, -100.0),  # Nebraska
            (35.0, -100.0),  # Oklahoma
            (30.0, -90.0),   # Louisiana
            (45.0, -100.0),  # North Dakota
        ]
        
        for pattern_lat, pattern_lng in suspicious_patterns:
            if abs(lat - pattern_lat) < 0.1 and abs(lng - pattern_lng) < 0.1:
                return True
        
        return False
    
    def geocode_address(self, company_name: str, city: str, state: str, address: str = None) -> Optional[Tuple[float, float]]:
        """Geocode an address using Mapbox Geocoding API with correct format"""
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
                logger.debug("No address components available for geocoding")
                return None
            
            # Create search query
            query = ", ".join(query_parts)
            
            # Use the CORRECT endpoint format from documentation
            geocoding_url = f"{self.base_url}/{requests.utils.quote(query)}.json"
            
            params = {
                'access_token': self.token,
                'country': 'US',  # Bias towards US results
                'types': 'poi,address',  # Point of interest or address
                'limit': 1,  # Get best match
                'autocomplete': 'false'  # Get exact matches
            }
            
            # Make API request with retries
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(geocoding_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('features') and len(data['features']) > 0:
                            feature = data['features'][0]
                            coordinates = feature['geometry']['coordinates']
                            confidence = feature.get('relevance', 0)
                            
                            # Mapbox returns [longitude, latitude], we need [latitude, longitude]
                            lng, lat = coordinates
                            
                            # Validate coordinates
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                return (lat, lng)
                            else:
                                logger.debug(f"Invalid coordinates returned: {lat}, {lng}")
                                return None
                        else:
                            logger.debug(f"No geocoding results for: {query}")
                            return None
                    
                    elif response.status_code == 404:
                        # Try alternative endpoint format
                        return self._try_alternative_endpoint(query)
                    elif response.status_code == 429:
                        logger.warning("429 Rate limited - waiting before retry")
                        time.sleep(2)
                        continue
                    else:
                        if attempt < self.max_retries - 1:
                            time.sleep(1)
                            continue
                        return None
                        
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        logger.debug(f"Geocoding failed after {self.max_retries} attempts: {e}")
                        return None
                    time.sleep(1)
            
            return None
                
        except Exception as e:
            logger.debug(f"Unexpected error geocoding {company_name}: {e}")
            return None
    
    def _try_alternative_endpoint(self, query: str) -> Optional[Tuple[float, float]]:
        """Try alternative endpoint format if the .json format fails"""
        try:
            # Method 2: Try without .json extension (traditional format)
            geocoding_url = self.base_url
            
            params = {
                'access_token': self.token,
                'q': query,
                'country': 'US',
                'types': 'poi,address',
                'limit': 1,
                'autocomplete': 'false'
            }
            
            response = requests.get(geocoding_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('features') and len(data['features']) > 0:
                    feature = data['features'][0]
                    coordinates = feature['geometry']['coordinates']
                    lng, lat = coordinates
                    
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        return (lat, lng)
            
            return None
            
        except Exception as e:
            logger.debug(f"Alternative endpoint failed: {e}")
            return None
    
    def get_records_needing_geocoding(self, incident_type: str = None, limit: int = None) -> List[WorkplaceIncident]:
        """Get records that need geocoding improvement"""
        try:
            db = SessionLocal()
            
            # Build query
            query = db.query(WorkplaceIncident)
            
            # Filter by incident type if specified
            if incident_type:
                query = query.filter(WorkplaceIncident.incident_type == incident_type)
            
            # Get all records
            all_records = query.all()
            
            # Filter records that need geocoding
            needs_geocoding = []
            for record in all_records:
                if self._needs_geocoding(record):
                    needs_geocoding.append(record)
                    if limit and len(needs_geocoding) >= limit:
                        break
            
            db.close()
            return needs_geocoding
            
        except Exception as e:
            logger.error(f"Error getting records needing geocoding: {e}")
            return []
    
    def smart_geocode_records(self, incident_type: str = None, batch_size: int = 50, max_records: int = None) -> Dict[str, int]:
        """Smart geocoding that only processes records needing improvement"""
        try:
            # Get records that need geocoding
            logger.info("🔍 Identifying records that need geocoding improvement...")
            records_to_process = self.get_records_needing_geocoding(incident_type, max_records)
            
            total_records = len(records_to_process)
            logger.info("=" * 60)
            logger.info(f"📋 FOUND: {total_records:,} records needing geocoding improvement")
            logger.info("=" * 60)
            
            if total_records == 0:
                logger.info("✅ No records need geocoding improvement!")
                return {"success": 0, "failed": 0, "skipped": 0, "improved": 0}
            
            # Process in batches
            success_count = 0
            failed_count = 0
            skipped_count = 0
            improved_count = 0
            
            for i, record in enumerate(records_to_process):
                # Show clear progress: "Processing record X of Y"
                current_record = i + 1
                logger.info(f"🔄 Processing record {current_record:,} of {total_records:,} ({current_record/total_records*100:.1f}%)")
                logger.info(f"   📍 Company: {record.company_name}")
                logger.info(f"   🏙️  Location: {record.city}, {record.state}")
                
                # Skip records without basic location info
                if not record.city or not record.state:
                    logger.info(f"   ⚠️  SKIPPED: Missing city or state")
                    skipped_count += 1
                    continue
                
                # Double-check if this record still needs geocoding
                if not self._needs_geocoding(record):
                    logger.info(f"   ⏭️  SKIPPED: Already has good coordinates")
                    skipped_count += 1
                    continue
                
                # Geocode the address
                logger.info(f"   🔍 Geocoding address...")
                coordinates = self.geocode_address(
                    company_name=record.company_name,
                    city=record.city,
                    state=record.state,
                    address=record.address
                )
                
                if coordinates:
                    # Check if we're improving existing coordinates
                    if record.latitude and record.longitude:
                        old_lat, old_lng = record.latitude, record.longitude
                        logger.info(f"   🔄 IMPROVED: Old ({old_lat:.6f}, {old_lng:.6f}) → New ({coordinates[0]:.6f}, {coordinates[1]:.6f})")
                        improved_count += 1
                    else:
                        logger.info(f"   ✅ ADDED: New coordinates ({coordinates[0]:.6f}, {coordinates[1]:.6f})")
                    
                    # Update record with new coordinates
                    record.latitude = coordinates[0]
                    record.longitude = coordinates[1]
                    success_count += 1
                else:
                    failed_count += 1
                    logger.info(f"   ❌ FAILED: Could not geocode address")
                
                # Show running totals
                logger.info(f"   📊 Progress: {success_count:,} success, {failed_count:,} failed, {skipped_count:,} skipped, {improved_count:,} improved")
                logger.info("-" * 50)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                # Commit every batch_size records
                if (i + 1) % batch_size == 0:
                    try:
                        db = SessionLocal()
                        db.merge(record)
                        db.commit()
                        logger.info(f"💾 COMMITTED: Batch {i//batch_size + 1} ({i+1:,} records)")
                        logger.info("=" * 60)
                        db.close()
                    except Exception as e:
                        logger.error(f"❌ Error committing batch: {e}")
                        if db:
                            db.rollback()
                            db.close()
            
            # Commit any remaining records
            if total_records % batch_size != 0:
                try:
                    db = SessionLocal()
                    db.merge(record)
                    db.commit()
                    logger.info(f"💾 COMMITTED: Final batch ({total_records:,} total records)")
                    db.close()
                except Exception as e:
                    logger.error(f"❌ Error committing final batch: {e}")
                    if db:
                        db.rollback()
                        db.close()
            
            # Final summary
            logger.info("=" * 60)
            logger.info("🎯 FINAL SMART GEOCODING RESULTS:")
            logger.info(f"   ✅ Success: {success_count:,}")
            logger.info(f"   ❌ Failed: {failed_count:,}")
            logger.info(f"   ⏭️  Skipped: {skipped_count:,}")
            logger.info(f"   🔄 Improved: {improved_count:,}")
            logger.info(f"   📊 Total Processed: {total_records:,}")
            logger.info("=" * 60)
            
            return {"success": success_count, "failed": failed_count, "skipped": skipped_count, "improved": improved_count}
            
        except Exception as e:
            logger.error(f"❌ Error during smart geocoding: {e}")
            return {"success": 0, "failed": 0, "skipped": 0, "improved": 0}

def main():
    """Main function"""
    logger.info("🚀 Starting Smart Geocoding Process")
    logger.info("Only processes records that need coordinate improvement")
    
    geocoder = SmartGeocoder()
    
    # Check what needs geocoding
    logger.info("\\n🔍 ANALYZING RECORDS...")
    
    # Check fatalities
    fatality_records = geocoder.get_records_needing_geocoding('fatality')
    logger.info(f"Fatalities needing improvement: {len(fatality_records):,}")
    
    # Check injuries (SIR data)
    injury_records = geocoder.get_records_needing_geocoding('injury')
    logger.info(f"Injuries needing improvement: {len(injury_records):,}")
    
    # Check all records
    all_records = geocoder.get_records_needing_geocoding()
    logger.info(f"Total records needing improvement: {len(all_records):,}")
    
    if len(all_records) == 0:
        logger.info("🎉 All records already have good coordinates!")
        return
    
    # Ask user what to process
    logger.info("\\n🎯 WHAT WOULD YOU LIKE TO PROCESS?")
    logger.info("1. Process ALL records needing improvement")
    logger.info("2. Process only FATALITIES needing improvement")
    logger.info("3. Process only INJURIES needing improvement")
    logger.info("4. Process a small sample (100 records)")
    
    # For now, let's process a small sample to test
    logger.info("\\n🚀 Processing small sample (100 records) to test...")
    
    results = geocoder.smart_geocode_records(
        batch_size=50, 
        max_records=100
    )
    
    if results['success'] > 0:
        logger.info("🎉 Smart geocoding completed successfully!")
        logger.info(f"📍 {results['success']:,} records now have better coordinates!")
    else:
        logger.warning("⚠️  No records were improved. Check the logs for issues.")

if __name__ == "__main__":
    main()

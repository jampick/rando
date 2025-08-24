#!/usr/bin/env python3
"""
Corrected Fatality Geocoding using Mapbox Geocoding API
Following the official documentation format
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

class CorrectedMapboxGeocoder:
    """Geocoding using Mapbox Geocoding API with correct endpoint format"""
    
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
                logger.warning("No address components available for geocoding")
                return None
            
            # Create search query
            query = ", ".join(query_parts)
            
            # Use the CORRECT endpoint format from documentation
            # https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json?access_token=YOUR_TOKEN
            
            # Method 1: Try with .json extension (as per documentation)
            geocoding_url = f"{self.base_url}/{requests.utils.quote(query)}.json"
            
            params = {
                'access_token': self.token,
                'country': 'US',  # Bias towards US results
                'types': 'poi,address',  # Point of interest or address
                'limit': 1,  # Get best match
                'autocomplete': 'false'  # Get exact matches
            }
            
            logger.debug(f"Geocoding: {query}")
            logger.debug(f"URL: {geocoding_url}")
            
            # Make API request with retries
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(geocoding_url, params=params, timeout=15)
                    logger.debug(f"Response status: {response.status_code}")
                    
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
                                logger.debug(f"✅ Geocoded: {query} -> {lat:.6f}, {lng:.6f} (confidence: {confidence:.2f})")
                                return (lat, lng)
                            else:
                                logger.warning(f"Invalid coordinates returned: {lat}, {lng}")
                                return None
                        else:
                            logger.debug(f"No geocoding results for: {query}")
                            return None
                    
                    elif response.status_code == 401:
                        logger.error("401 Unauthorized - Invalid token")
                        return None
                    elif response.status_code == 403:
                        logger.error("403 Forbidden - Token restrictions or permissions issue")
                        return None
                    elif response.status_code == 404:
                        logger.debug(f"404 Not Found for: {query}")
                        # Try alternative endpoint format
                        return self._try_alternative_endpoint(query)
                    elif response.status_code == 429:
                        logger.warning("429 Rate limited - waiting before retry")
                        time.sleep(2)
                        continue
                    else:
                        logger.warning(f"Unexpected status {response.status_code}: {response.text[:100]}...")
                        if attempt < self.max_retries - 1:
                            time.sleep(1)
                            continue
                        return None
                        
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Geocoding failed after {self.max_retries} attempts: {e}")
                        return None
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)
            
            return None
                
        except Exception as e:
            logger.error(f"Unexpected error geocoding {company_name}: {e}")
            return None
    
    def _try_alternative_endpoint(self, query: str) -> Optional[Tuple[float, float]]:
        """Try alternative endpoint format if the .json format fails"""
        try:
            logger.debug("Trying alternative endpoint format...")
            
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
            logger.debug(f"Alternative endpoint response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('features') and len(data['features']) > 0:
                    feature = data['features'][0]
                    coordinates = feature['geometry']['coordinates']
                    confidence = feature.get('relevance', 0)
                    
                    lng, lat = coordinates
                    
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        logger.debug(f"✅ Alternative endpoint worked: {query} -> {lat:.6f}, {lng:.6f}")
                        return (lat, lng)
            
            return None
            
        except Exception as e:
            logger.error(f"Alternative endpoint failed: {e}")
            return None
    
    def test_geocoding(self) -> bool:
        """Test the geocoding API with correct format"""
        logger.info("Testing Mapbox geocoding API with correct endpoint format...")
        
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
    
    def geocode_fatalities(self, batch_size: int = 50, max_records: int = None, replace_existing: bool = False) -> Dict[str, int]:
        """Geocode fatality records in batches"""
        if not self.token:
            logger.error("Cannot proceed without Mapbox token")
            return {"success": 0, "failed": 0, "skipped": 0, "replaced": 0}
        
        db = SessionLocal()
        try:
            # Get fatality records to geocode
            if replace_existing:
                # Replace all fatality coordinates (including approximate ones)
                query = db.query(WorkplaceIncident).filter(
                    WorkplaceIncident.incident_type == 'fatality'
                )
                logger.info("🔄 MODE: Replacing ALL fatality coordinates")
            else:
                # Only geocode records without coordinates
                query = db.query(WorkplaceIncident).filter(
                    and_(
                        WorkplaceIncident.incident_type == 'fatality',
                        WorkplaceIncident.latitude.is_(None)
                    )
                )
                logger.info("🎯 MODE: Processing ONLY fatalities missing coordinates")
            
            if max_records:
                query = query.limit(max_records)
                logger.info(f"📊 LIMIT: Processing maximum {max_records:,} records")
            
            fatality_records = query.all()
            total_records = len(fatality_records)
            
            logger.info("=" * 60)
            logger.info(f"📋 FOUND: {total_records:,} fatality records to process")
            logger.info("=" * 60)
            
            if total_records == 0:
                logger.info("✅ No fatality records to geocode!")
                return {"success": 0, "failed": 0, "skipped": 0, "replaced": 0}
            
            # Process in batches
            success_count = 0
            failed_count = 0
            skipped_count = 0
            replaced_count = 0
            
            for i, record in enumerate(fatality_records):
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
                
                # Skip if already has good coordinates (unless replacing)
                if not replace_existing and record.latitude and record.longitude:
                    logger.info(f"   ⏭️  SKIPPED: Already has coordinates ({record.latitude:.6f}, {record.longitude:.6f})")
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
                    # Check if we're replacing existing coordinates
                    if record.latitude and record.longitude:
                        replaced_count += 1
                        logger.info(f"   🔄 REPLACED: Old ({record.latitude:.6f}, {record.longitude:.6f}) → New ({coordinates[0]:.6f}, {coordinates[1]:.6f})")
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
                logger.info(f"   📊 Progress: {success_count:,} success, {failed_count:,} failed, {skipped_count:,} skipped")
                logger.info("-" * 50)
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                # Commit every batch_size records
                if (i + 1) % batch_size == 0:
                    try:
                        db.commit()
                        logger.info(f"💾 COMMITTED: Batch {i//batch_size + 1} ({i+1:,} records)")
                        logger.info("=" * 60)
                    except Exception as e:
                        logger.error(f"❌ Error committing batch: {e}")
                        db.rollback()
            
            # Commit any remaining records
            if total_records % batch_size != 0:
                try:
                    db.commit()
                    logger.info(f"💾 COMMITTED: Final batch ({total_records:,} total records)")
                except Exception as e:
                    logger.error(f"❌ Error committing final batch: {e}")
                    db.rollback()
            
            # Final summary
            logger.info("=" * 60)
            logger.info("🎯 FINAL GEOCODING RESULTS:")
            logger.info(f"   ✅ Success: {success_count:,}")
            logger.info(f"   ❌ Failed: {failed_count:,}")
            logger.info(f"   ⏭️  Skipped: {skipped_count:,}")
            logger.info(f"   🔄 Replaced: {replaced_count:,}")
            logger.info(f"   📊 Total Processed: {total_records:,}")
            logger.info("=" * 60)
            
            return {"success": success_count, "failed": failed_count, "skipped": skipped_count, "replaced": replaced_count}
            
        except Exception as e:
            logger.error(f"❌ Error during geocoding: {e}")
            db.rollback()
            return {"success": 0, "failed": 0, "skipped": 0, "replaced": 0}
        finally:
            db.close()

def main():
    """Main function"""
    logger.info("🚀 Starting Corrected Mapbox Geocoding Process")
    logger.info("Using official documentation endpoint format")
    
    geocoder = CorrectedMapboxGeocoder()
    
    # Test the API first
    if not geocoder.test_geocoding():
        logger.error("Geocoding test failed. Please check your Mapbox token and account settings.")
        return
    
    # Start geocoding process
    logger.info("Starting geocoding of fatality records...")
    
    # Process ALL fatalities missing coordinates (no limit, no replacement)
    results = geocoder.geocode_fatalities(
        batch_size=50, 
        max_records=None,  # Process ALL records
        replace_existing=False  # Only process missing coordinates
    )
    
    # Final results display
    if results['success'] > 0:
        logger.info("🎉 SUCCESS: Geocoding completed!")
        logger.info(f"📍 {results['success']:,} fatalities now have exact coordinates!")
        logger.info("🗺️  You can now see precise fatality locations on the map!")
    else:
        logger.warning("⚠️  No records were geocoded. Check the logs for issues.")

if __name__ == "__main__":
    main()

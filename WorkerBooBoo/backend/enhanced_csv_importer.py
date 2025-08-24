#!/usr/bin/env python3
"""
Enhanced CSV Importer with Duplicate Prevention
Prevents duplicate records during data imports using multiple strategies
"""

import os
import csv
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy import create_engine, text, and_, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import your models
from database import Base, WorkplaceIncident, Industry, SessionLocal

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedCSVImporter:
    """Enhanced CSV importer with duplicate prevention strategies"""
    
    def __init__(self, db_url: str = None):
        """Initialize the importer"""
        if db_url:
            self.engine = create_engine(db_url)
        else:
            # Use default SQLite database
            self.engine = create_engine('sqlite:///workplace_safety.db')
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Duplicate detection strategies
        self.duplicate_strategies = {
            'osha_id': 'Exact OSHA ID match',
            'company_location_date': 'Company + Location + Date combination',
            'company_incident_type': 'Company + Incident Type + Date',
            'address_coordinates': 'Address + Coordinates (if available)'
        }
    
    def detect_duplicates(self, records: List[Dict], strategy: str = 'all') -> Tuple[List[Dict], List[Dict]]:
        """
        Detect duplicate records using specified strategy
        
        Returns:
            Tuple of (unique_records, duplicate_records)
        """
        logger.info(f"🔍 Detecting duplicates using strategy: {strategy}")
        
        unique_records = []
        duplicate_records = []
        
        # Get existing records from database for comparison
        db = self.SessionLocal()
        try:
            existing_records = db.query(WorkplaceIncident).all()
            existing_lookup = self._build_existing_lookup(existing_records)
            
            for record in records:
                is_duplicate = False
                duplicate_reason = ""
                
                # Strategy 1: Check OSHA ID (most reliable)
                if record.get('osha_id') and record['osha_id'] in existing_lookup['osha_ids']:
                    is_duplicate = True
                    duplicate_reason = f"OSHA ID already exists: {record['osha_id']}"
                
                # Strategy 2: Check Company + Location + Date
                elif self._check_company_location_date_duplicate(record, existing_lookup):
                    is_duplicate = True
                    duplicate_reason = "Company + Location + Date combination already exists"
                
                # Strategy 3: Check Company + Incident Type + Date
                elif self._check_company_incident_type_duplicate(record, existing_lookup):
                    is_duplicate = True
                    duplicate_reason = "Company + Incident Type + Date combination already exists"
                
                # Strategy 4: Check Address + Coordinates (if available)
                elif self._check_address_coordinates_duplicate(record, existing_lookup):
                    is_duplicate = True
                    duplicate_reason = "Address + Coordinates combination already exists"
                
                if is_duplicate:
                    duplicate_records.append({
                        'record': record,
                        'reason': duplicate_reason
                    })
                    logger.debug(f"Duplicate detected: {duplicate_reason}")
                else:
                    unique_records.append(record)
            
            logger.info(f"✅ Duplicate detection complete:")
            logger.info(f"   Unique records: {len(unique_records):,}")
            logger.info(f"   Duplicate records: {len(duplicate_records):,}")
            
        except Exception as e:
            logger.error(f"Error during duplicate detection: {e}")
            # If duplicate detection fails, treat all as unique
            unique_records = records
            duplicate_records = []
        finally:
            db.close()
        
        return unique_records, duplicate_records
    
    def _build_existing_lookup(self, existing_records: List[WorkplaceIncident]) -> Dict:
        """Build lookup dictionaries for efficient duplicate checking"""
        lookup = {
            'osha_ids': set(),
            'company_location_dates': set(),
            'company_incident_type_dates': set(),
            'address_coordinates': set()
        }
        
        for record in existing_records:
            # OSHA ID lookup
            if record.osha_id:
                lookup['osha_ids'].add(record.osha_id)
            
            # Company + Location + Date lookup
            if record.company_name and record.city and record.state and record.incident_date:
                key = (
                    record.company_name.lower().strip(),
                    record.city.lower().strip(),
                    record.state.lower().strip(),
                    record.incident_date.date()
                )
                lookup['company_location_dates'].add(key)
            
            # Company + Incident Type + Date lookup
            if record.company_name and record.incident_type and record.incident_date:
                key = (
                    record.company_name.lower().strip(),
                    record.incident_type.lower().strip(),
                    record.incident_date.date()
                )
                lookup['company_incident_type_dates'].add(key)
            
            # Address + Coordinates lookup
            if record.address and record.latitude and record.longitude:
                key = (
                    record.address.lower().strip(),
                    round(record.latitude, 6),
                    round(record.longitude, 6)
                )
                lookup['address_coordinates'].add(key)
        
        return lookup
    
    def _check_company_location_date_duplicate(self, record: Dict, existing_lookup: Dict) -> bool:
        """Check if Company + Location + Date combination already exists"""
        if not all([record.get('company_name'), record.get('city'), record.get('state'), record.get('incident_date')]):
            return False
        
        try:
            # Parse incident_date if it's a string
            if isinstance(record['incident_date'], str):
                incident_date = datetime.strptime(record['incident_date'], '%Y-%m-%d').date()
            else:
                incident_date = record['incident_date'].date()
            
            key = (
                record['company_name'].lower().strip(),
                record['city'].lower().strip(),
                record['state'].lower().strip(),
                incident_date
            )
            
            return key in existing_lookup['company_location_dates']
        except:
            return False
    
    def _check_company_incident_type_duplicate(self, record: Dict, existing_lookup: Dict) -> bool:
        """Check if Company + Incident Type + Date combination already exists"""
        if not all([record.get('company_name'), record.get('incident_type'), record.get('incident_date')]):
            return False
        
        try:
            # Parse incident_date if it's a string
            if isinstance(record['incident_date'], str):
                incident_date = datetime.strptime(record['incident_date'], '%Y-%m-%d').date()
            else:
                incident_date = record['incident_date'].date()
            
            key = (
                record['company_name'].lower().strip(),
                record['incident_type'].lower().strip(),
                incident_date
            )
            
            return key in existing_lookup['company_incident_type_dates']
        except:
            return False
    
    def _check_address_coordinates_duplicate(self, record: Dict, existing_lookup: Dict) -> bool:
        """Check if Address + Coordinates combination already exists"""
        if not all([record.get('address'), record.get('latitude'), record.get('longitude')]):
            return False
        
        try:
            key = (
                record['address'].lower().strip(),
                round(float(record['latitude']), 6),
                round(float(record['longitude']), 6)
            )
            
            return key in existing_lookup['address_coordinates']
        except:
            return False
    
    def import_csv_with_duplicate_prevention(self, file_path: str, 
                                          duplicate_strategy: str = 'all',
                                          update_existing: bool = False,
                                          batch_size: int = 1000) -> Dict:
        """
        Import CSV with comprehensive duplicate prevention
        
        Args:
            file_path: Path to CSV file
            duplicate_strategy: Strategy for duplicate detection
            update_existing: Whether to update existing records
            batch_size: Number of records to process in each batch
        """
        try:
            logger.info(f"🚀 Starting enhanced CSV import: {file_path}")
            logger.info(f"📊 Duplicate strategy: {duplicate_strategy}")
            logger.info(f"🔄 Update existing: {update_existing}")
            
            # Read CSV file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            # Read CSV with pandas for better handling
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"📋 Loaded {len(df):,} records from CSV")
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Detect duplicates
            unique_records, duplicate_records = self.detect_duplicates(records, duplicate_strategy)
            
            if len(duplicate_records) > 0:
                logger.warning(f"⚠️  Found {len(duplicate_records):,} duplicate records")
                
                # Show sample of duplicates
                logger.info("📝 Sample duplicates:")
                for i, dup in enumerate(duplicate_records[:5]):
                    record = dup['record']
                    logger.info(f"   {i+1}. {record.get('company_name', 'N/A')} - {dup['reason']}")
                
                if not update_existing:
                    logger.info("💡 Use --update-existing to update existing records instead of skipping")
            
            # Process unique records
            if len(unique_records) == 0:
                logger.info("✅ No new records to import")
                return {
                    'total_processed': 0,
                    'imported': 0,
                    'updated': 0,
                    'duplicates_skipped': len(duplicate_records),
                    'errors': 0
                }
            
            # Import unique records
            logger.info(f"📥 Importing {len(unique_records):,} unique records...")
            
            results = self._import_records_batch(unique_records, batch_size, update_existing)
            
            # Final summary
            logger.info("=" * 60)
            logger.info("🎯 IMPORT SUMMARY:")
            logger.info(f"   📋 Total processed: {results['total_processed']:,}")
            logger.info(f"   ✅ New records imported: {results['imported']:,}")
            logger.info(f"   🔄 Existing records updated: {results['updated']:,}")
            logger.info(f"   ⏭️  Duplicates skipped: {len(duplicate_records):,}")
            logger.info(f"   ❌ Errors: {results['errors']:,}")
            logger.info("=" * 60)
            
            return {
                'total_processed': results['total_processed'],
                'imported': results['imported'],
                'updated': results['updated'],
                'duplicates_skipped': len(duplicate_records),
                'errors': results['errors']
            }
            
        except Exception as e:
            logger.error(f"❌ Import failed: {e}")
            return {
                'total_processed': 0,
                'imported': 0,
                'updated': 0,
                'duplicates_skipped': 0,
                'errors': 1
            }
    
    def _import_records_batch(self, records: List[Dict], batch_size: int, update_existing: bool) -> Dict:
        """Import records in batches with error handling"""
        total_processed = 0
        imported = 0
        updated = 0
        errors = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch):,} records)")
            
            try:
                db = self.SessionLocal()
                
                for record in batch:
                    try:
                        # Check if record already exists
                        existing_record = None
                        if record.get('osha_id'):
                            existing_record = db.query(WorkplaceIncident).filter(
                                WorkplaceIncident.osha_id == record['osha_id']
                            ).first()
                        
                        if existing_record and update_existing:
                            # Update existing record
                            self._update_existing_record(existing_record, record)
                            updated += 1
                        elif existing_record and not update_existing:
                            # Skip existing record
                            continue
                        else:
                            # Create new record
                            new_record = self._create_new_record(record)
                            db.add(new_record)
                            imported += 1
                        
                        total_processed += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing record: {e}")
                        errors += 1
                        continue
                
                # Commit batch
                db.commit()
                logger.info(f"💾 Committed batch {batch_num}")
                
            except Exception as e:
                logger.error(f"❌ Error in batch {batch_num}: {e}")
                if db:
                    db.rollback()
                errors += len(batch)
            finally:
                if db:
                    db.close()
        
        return {
            'total_processed': total_processed,
            'imported': imported,
            'updated': updated,
            'errors': errors
        }
    
    def _create_new_record(self, record: Dict) -> WorkplaceIncident:
        """Create a new WorkplaceIncident record"""
        # Convert date strings to datetime objects
        incident_date = self._parse_date(record.get('incident_date'))
        created_at = self._parse_date(record.get('created_at')) or datetime.now()
        updated_at = self._parse_date(record.get('updated_at')) or datetime.now()
        
        return WorkplaceIncident(
            osha_id=record.get('osha_id'),
            company_name=record.get('company_name'),
            address=record.get('address'),
            city=record.get('city'),
            state=record.get('state'),
            zip_code=record.get('zip_code'),
            latitude=record.get('latitude'),
            longitude=record.get('longitude'),
            incident_date=incident_date,
            incident_type=record.get('incident_type'),
            industry=record.get('industry'),
            naics_code=record.get('naics_code'),
            description=record.get('description'),
            investigation_status=record.get('investigation_status'),
            citations_issued=record.get('citations_issued'),
            penalty_amount=record.get('penalty_amount'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date value from various formats"""
        if not date_value or pd.isna(date_value):
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            # Try multiple date formats
            date_formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y',
                '%m/%d/%Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try pandas parsing
            try:
                return pd.to_datetime(date_value)
            except:
                pass
        
        return None
    
    def _update_existing_record(self, existing_record: WorkplaceIncident, new_data: Dict):
        """Update existing record with new data"""
        # Update fields that might have changed
        if new_data.get('company_name'):
            existing_record.company_name = new_data['company_name']
        if new_data.get('address'):
            existing_record.address = new_data['address']
        if new_data.get('city'):
            existing_record.city = new_data['city']
        if new_data.get('state'):
            existing_record.state = new_data['state']
        if new_data.get('zip_code'):
            existing_record.zip_code = new_data['zip_code']
        if new_data.get('latitude'):
            existing_record.latitude = new_data['latitude']
        if new_data.get('longitude'):
            existing_record.longitude = new_data['longitude']
        if new_data.get('incident_date'):
            existing_record.incident_date = self._parse_date(new_data['incident_date'])
        if new_data.get('incident_type'):
            existing_record.incident_type = new_data['incident_type']
        if new_data.get('industry'):
            existing_record.industry = new_data['industry']
        if new_data.get('naics_code'):
            existing_record.naics_code = new_data['naics_code']
        if new_data.get('description'):
            existing_record.description = new_data['description']
        if new_data.get('investigation_status'):
            existing_record.investigation_status = new_data['investigation_status']
        if new_data.get('citations_issued') is not None:
            existing_record.citations_issued = new_data['citations_issued']
        if new_data.get('penalty_amount') is not None:
            existing_record.penalty_amount = new_data['penalty_amount']
        
        existing_record.updated_at = datetime.now()

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Enhanced CSV Importer with Duplicate Prevention')
    parser.add_argument('file_path', help='Path to CSV file to import')
    parser.add_argument('--duplicate-strategy', choices=['all', 'osha_id', 'company_location_date', 'company_incident_type', 'address_coordinates'],
                       default='all', help='Strategy for duplicate detection')
    parser.add_argument('--update-existing', action='store_true', 
                       help='Update existing records instead of skipping them')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Number of records to process in each batch')
    parser.add_argument('--export-template', action='store_true',
                       help='Export a template CSV file')
    
    args = parser.parse_args()
    
    if args.export_template:
        # Export template functionality
        template_data = [
            {
                'osha_id': 'EXAMPLE-001',
                'company_name': 'Example Company Inc.',
                'address': '123 Main St',
                'city': 'Example City',
                'state': 'CA',
                'zip_code': '12345',
                'latitude': '37.7749',
                'longitude': '-122.4194',
                'incident_date': '2024-01-15',
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': 'Example incident description',
                'investigation_status': 'Open',
                'citations_issued': 'false',
                'penalty_amount': '0.0'
            }
        ]
        
        template_file = 'osha_import_template.csv'
        with open(template_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=template_data[0].keys())
            writer.writeheader()
            writer.writerows(template_data)
        
        logger.info(f"📄 Template exported to: {template_file}")
        return
    
    # Import CSV
    importer = EnhancedCSVImporter()
    results = importer.import_csv_with_duplicate_prevention(
        file_path=args.file_path,
        duplicate_strategy=args.duplicate_strategy,
        update_existing=args.update_existing,
        batch_size=args.batch_size
    )
    
    if results['errors'] == 0:
        logger.info("🎉 Import completed successfully!")
    else:
        logger.warning(f"⚠️  Import completed with {results['errors']} errors")

if __name__ == "__main__":
    main()

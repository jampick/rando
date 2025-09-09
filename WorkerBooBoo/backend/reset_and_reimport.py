#!/usr/bin/env python3
"""
Reset Database and Reimport with Proper OIICS Matching
This script resets the database and reimports data with accurate OIICS field matching
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident, Industry, Base, engine
from models import IncidentCreate
from icon_categories import icon_mapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseResetAndReimport:
    """Reset database and reimport with proper OIICS matching"""
    
    def __init__(self, db_path: str = "workplace_safety.db"):
        """Initialize the resetter"""
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Source data paths
        self.data_dir = Path("../data/osha")
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # OIICS field mappings for different data types
        self.oiics_mappings = {
            'sir': {
                'Part of Body Title': 'body_part',
                'EventTitle': 'event_type', 
                'SourceTitle': 'source',
                'Secondary Source Title': 'secondary_source',
                'Hospitalized': 'hospitalized',
                'Amputation': 'amputation',
                'Inspection': 'inspection_id',
                'FederalState': 'jurisdiction'
            },
            'fatality': {
                'Event Date': 'incident_date',
                'Establishment Name': 'company_name',
                'Site City': 'city',
                'Site State': 'state',
                'Site NAICS': 'industry',
                'Inspection #': 'inspection_id',
                'Jurisdiction': 'jurisdiction'
            }
        }
    
    def reset_database(self):
        """Reset the database by dropping and recreating tables"""
        logger.info("🗑️  Resetting database...")
        
        try:
            # Drop all tables
            Base.metadata.drop_all(bind=engine)
            logger.info("✓ Dropped all existing tables")
            
            # Recreate all tables
            Base.metadata.create_all(bind=engine)
            logger.info("✓ Recreated all tables")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"✓ Database tables: {tables}")
            
        except Exception as e:
            logger.error(f"❌ Error resetting database: {e}")
            raise
    
    def detect_data_type(self, df) -> str:
        """Detect if this is SIR or fatality data"""
        columns = set(df.columns)
        
        # Check for SIR indicators
        sir_indicators = {'EventDate', 'NatureTitle', 'Part of Body Title', 'Hospitalized', 'Amputation'}
        sir_score = len(columns.intersection(sir_indicators))
        
        # Check for fatality indicators
        fatality_indicators = {'Event Date', 'Establishment Name', 'Victim Name (Age)', 'Opening Conference Date'}
        fatality_score = len(columns.intersection(fatality_indicators))
        
        if sir_score > fatality_score:
            return 'sir'
        elif fatality_score > sir_score:
            return 'fatality'
        else:
            return 'sir'  # Default to SIR
    
    def process_oiics_data(self, df, data_type: str):
        """Process and map OIICS fields from source data"""
        logger.info(f"Processing OIICS data for {data_type} format...")
        
        # Get the appropriate mapping
        mapping = self.oiics_mappings.get(data_type, self.oiics_mappings['sir'])
        
        # Create new dataframe with OIICS fields
        processed_data = []
        
        for idx, row in df.iterrows():
            if idx % 10000 == 0:
                logger.info(f"Processing record {idx:,} of {len(df):,}")
            
            # Map OIICS fields using primary mapping
            oiics_record = {}
            for source_col, our_col in mapping.items():
                if source_col in row.index and pd.notna(row[source_col]):
                    oiics_record[our_col] = row[source_col]
            
            # For fatality data, set default OIICS values since they don't have detailed injury classification
            if data_type == 'fatality':
                oiics_record['body_part'] = 'Multiple/Unspecified'
                oiics_record['event_type'] = 'Fatality'
                oiics_record['source'] = 'Workplace incident'
                oiics_record['secondary_source'] = None
                oiics_record['hospitalized'] = False  # Fatalities don't result in hospitalization
                oiics_record['amputation'] = False
                oiics_record['inspection_id'] = oiics_record.get('inspection_id')
                oiics_record['jurisdiction'] = oiics_record.get('jurisdiction')
            else:
                # Process boolean fields for SIR data
                if 'hospitalized' in oiics_record:
                    oiics_record['hospitalized'] = self._parse_boolean(oiics_record['hospitalized'])
                
                if 'amputation' in oiics_record:
                    oiics_record['amputation'] = self._parse_boolean(oiics_record['amputation'])
                
                # Fix amputation data inconsistencies
                # If incident type is "Amputations" but amputation field is False/None, 
                # infer from description and set to True
                if (row.get('NatureTitle') == 'Amputations' and 
                    (oiics_record.get('amputation') is False or oiics_record.get('amputation') is None)):
                    
                    # Check description for amputation indicators
                    description = str(row.get('Final Narrative', '')).lower()
                    amputation_indicators = [
                        'amputat', 'cut off', 'severed', 'removed', 'lost', 'detached',
                        'finger', 'toe', 'limb', 'digit', 'extremity'
                    ]
                    
                    has_amputation_indicators = any(indicator in description for indicator in amputation_indicators)
                    
                    if has_amputation_indicators:
                        logger.info(f"Fixing amputation field for OSHA ID {row.get('ID', 'Unknown')}: "
                                  f"NatureTitle=Amputations but amputation=False, setting to True")
                        oiics_record['amputation'] = True
            
            # Add original row data for matching
            oiics_record['original_data'] = row.to_dict()
            processed_data.append(oiics_record)
        
        return processed_data
    
    def _parse_boolean(self, value) -> Optional[bool]:
        """Parse boolean values from various formats"""
        if pd.isna(value):
            return None
        
        if isinstance(value, bool):
            return value
        
        value_str = str(value).lower().strip()
        
        if value_str in ['1', 'true', 'yes', 'y', 'on']:
            return True
        elif value_str in ['0', 'false', 'no', 'n', 'off']:
            return False
        
        return None
    
    def _parse_date(self, date_str) -> Optional[datetime.date]:
        """Parse date string to date object"""
        if pd.isna(date_str):
            return None
        
        try:
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    parsed_date = datetime.strptime(str(date_str), fmt)
                    return parsed_date.date()
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching"""
        if not name:
            return ""
        
        # Remove common suffixes and normalize
        normalized = str(name).upper().strip()
        suffixes = [' INC', ' LLC', ' CORP', ' CORPORATION', ' CO', ' COMPANY']
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        # Remove special characters and extra spaces
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def reimport_with_oiics(self):
        """Reimport data with proper OIICS matching"""
        logger.info("🚀 Starting data reimport with OIICS matching...")
        
        try:
            import pandas as pd
            
            # Process each source data file
            source_files = list(self.raw_dir.glob("*.csv")) + list(self.raw_dir.glob("*.xlsx"))
            
            all_oiics_data = []
            
            for source_file in source_files:
                logger.info(f"Processing source file: {source_file.name}")
                
                try:
                    # Read the file
                    if source_file.suffix == '.csv':
                        df = pd.read_csv(source_file, low_memory=False, quoting=1)  # QUOTE_ALL
                    else:
                        df = pd.read_excel(source_file)
                    
                    # Detect data type
                    data_type = self.detect_data_type(df)
                    logger.info(f"Detected data type: {data_type}")
                    
                    # Process OIICS data
                    oiics_data = self.process_oiics_data(df, data_type)
                    logger.info(f"Processed {len(oiics_data)} records with OIICS data")
                    
                    all_oiics_data.extend(oiics_data)
                    
                except Exception as e:
                    error_msg = f"Error processing {source_file.name}: {e}"
                    logger.error(error_msg)
            
            logger.info(f"Total OIICS records processed: {len(all_oiics_data)}")
            
            # Now create incidents with proper OIICS data
            self._create_incidents_from_oiics(all_oiics_data)
            
        except Exception as e:
            logger.error(f"Error during reimport: {e}")
            raise
    
    def _create_incidents_from_oiics(self, oiics_data):
        """Create incidents from OIICS data"""
        logger.info("Creating incidents from OIICS data...")
        
        # First, deduplicate the data by OSHA ID or inspection number
        logger.info("Deduplicating OIICS data...")
        unique_incidents = {}
        for oiics_record in oiics_data:
            orig_data = oiics_record['original_data']
            
            # For SIR data, use OSHA ID; for fatality data, use inspection number
            if 'ID' in orig_data and orig_data.get('ID'):
                unique_key = f"SIR_{orig_data['ID']}"
            elif 'Inspection #' in orig_data and orig_data.get('Inspection #'):
                unique_key = f"FATALITY_{orig_data['Inspection #']}"
            else:
                # Fallback for records without clear identifiers
                unique_key = f"UNKNOWN_{len(unique_incidents)}"
            
            if unique_key not in unique_incidents:
                unique_incidents[unique_key] = oiics_record
        
        logger.info(f"Deduplicated from {len(oiics_data)} to {len(unique_incidents)} unique incidents")
        
        db = self.SessionLocal()
        created_count = 0
        
        try:
            for i, (unique_key, oiics_record) in enumerate(unique_incidents.items()):
                if i % 10000 == 0:
                    logger.info(f"Creating incident {i:,} of {len(unique_incidents):,}")
                
                try:
                    orig_data = oiics_record['original_data']
                    
                    # Generate appropriate OSHA ID for the incident
                    if unique_key.startswith('SIR_'):
                        osha_id = unique_key.replace('SIR_', '')
                    elif unique_key.startswith('FATALITY_'):
                        osha_id = f"FATALITY-{unique_key.replace('FATALITY_', '')}"
                    else:
                        osha_id = unique_key
                    
                    # Extract basic incident data
                    incident_data = {
                        'osha_id': osha_id,
                        'company_name': str(orig_data.get('Employer', orig_data.get('Establishment Name', 'Unknown Company'))),
                        'address': str(orig_data.get('Address1', '')),
                        'city': str(orig_data.get('City', orig_data.get('Site City', ''))),
                        'state': str(orig_data.get('State', orig_data.get('Site State', ''))),
                        'latitude': float(orig_data.get('Latitude', 0)) if pd.notna(orig_data.get('Latitude')) else None,
                        'longitude': float(orig_data.get('Longitude', 0)) if pd.notna(orig_data.get('Longitude')) else None,
                        'incident_date': self._parse_date(orig_data.get('EventDate', orig_data.get('Event Date'))) or datetime.now().date(),
                        'incident_type': str(orig_data.get('NatureTitle', 'Fatality')),
                        'industry': str(orig_data.get('Primary NAICS', orig_data.get('Site NAICS', 'Unknown'))),
                        'description': str(orig_data.get('Final Narrative', f"Fatality incident at {orig_data.get('Establishment Name', 'Unknown Company')}")),
                        'investigation_status': 'Reported',
                        'citations_issued': False,
                        'penalty_amount': 0.0,
                        # OIICS Fields
                        'body_part': oiics_record.get('body_part'),
                        'event_type': oiics_record.get('event_type'),
                        'source': oiics_record.get('source'),
                        'secondary_source': oiics_record.get('secondary_source'),
                        'hospitalized': oiics_record.get('hospitalized'),
                        'amputation': oiics_record.get('amputation'),
                        'inspection_id': oiics_record.get('inspection_id'),
                        'jurisdiction': oiics_record.get('jurisdiction'),
                        # Icon Category Fields
                        'icon_injury': icon_mapper.map_injury_category(
                            oiics_record.get('body_part'), 
                            incident_data['incident_type']
                        ),
                        'icon_event': icon_mapper.map_event_category(
                            oiics_record.get('event_type')
                        ),
                        'icon_source': icon_mapper.map_source_category(
                            oiics_record.get('source')
                        ),
                        'icon_severity': icon_mapper.map_severity_category(
                            oiics_record.get('hospitalized'),
                            oiics_record.get('amputation'),
                            incident_data['incident_type']
                        ),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                    
                    # For fatality data, ensure we have a valid incident type
                    if 'Establishment Name' in orig_data and orig_data.get('Establishment Name'):
                        incident_data['incident_type'] = 'Fatality'
                        incident_data['description'] = f"Fatality incident at {orig_data['Establishment Name']}"
                        if 'Victim Name (Age)' in orig_data and orig_data.get('Victim Name (Age)'):
                            incident_data['description'] += f" - Victim: {orig_data['Victim Name (Age)']}"
                    
                    # Create the incident
                    incident = WorkplaceIncident(**incident_data)
                    db.add(incident)
                    created_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error creating incident {i}: {e}")
                    continue
            
            # Commit all changes
            db.commit()
            logger.info(f"✅ Successfully created {created_count} incidents with OIICS data")
            
        except Exception as e:
            logger.error(f"Error creating incidents: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def validate_reimport(self):
        """Validate the reimported data"""
        logger.info("Validating reimported data...")
        
        db = self.SessionLocal()
        validation_results = {
            'total_incidents': 0,
            'incidents_with_oiics': 0,
            'oiics_field_counts': {},
            'sample_incidents': []
        }
        
        try:
            # Get total incidents
            total_incidents = db.query(WorkplaceIncident).count()
            validation_results['total_incidents'] = total_incidents
            
            # Count incidents with OIICS data
            incidents_with_oiics = db.query(WorkplaceIncident).filter(
                (WorkplaceIncident.body_part.isnot(None)) |
                (WorkplaceIncident.event_type.isnot(None)) |
                (WorkplaceIncident.source.isnot(None)) |
                (WorkplaceIncident.hospitalized.isnot(None)) |
                (WorkplaceIncident.amputation.isnot(None))
            ).count()
            validation_results['incidents_with_oiics'] = incidents_with_oiics
            
            # Count each OIICS field
            oiics_fields = ['body_part', 'event_type', 'source', 'secondary_source', 
                           'hospitalized', 'amputation', 'inspection_id', 'jurisdiction']
            
            for field in oiics_fields:
                count = db.query(WorkplaceIncident).filter(
                    getattr(WorkplaceIncident, field).isnot(None)
                ).count()
                validation_results['oiics_field_counts'][field] = count
            
            # Get sample incidents with OIICS data
            sample_incidents = db.query(WorkplaceIncident).filter(
                (WorkplaceIncident.body_part.isnot(None)) |
                (WorkplaceIncident.event_type.isnot(None)) |
                (WorkplaceIncident.source.isnot(None))
            ).limit(5).all()
            
            for incident in sample_incidents:
                sample_data = {
                    'id': incident.id,
                    'osha_id': incident.osha_id,
                    'company_name': incident.company_name,
                    'incident_type': incident.incident_type,
                    'oiics_fields': {
                        'body_part': incident.body_part,
                        'event_type': incident.event_type,
                        'source': incident.source,
                        'secondary_source': incident.secondary_source,
                        'hospitalized': incident.hospitalized,
                        'amputation': incident.amputation,
                        'inspection_id': incident.inspection_id,
                        'jurisdiction': incident.jurisdiction
                    }
                }
                validation_results['sample_incidents'].append(sample_data)
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            raise
        finally:
            db.close()
        
        return validation_results

def main():
    """Main function"""
    logger.info("🎯 Starting Database Reset and OIICS Reimport")
    
    try:
        # Initialize resetter
        resetter = DatabaseResetAndReimport()
        
        # Reset database
        resetter.reset_database()
        
        # Reimport with OIICS
        resetter.reimport_with_oiics()
        
        # Validate results
        validation_results = resetter.validate_reimport()
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("📊 REIMPORT RESULTS SUMMARY")
        logger.info("="*60)
        
        if validation_results:
            logger.info("\nValidation Results:")
            validation = validation_results
            logger.info(f"  Total incidents: {validation['total_incidents']}")
            logger.info(f"  Incidents with OIICS data: {validation['incidents_with_oiics']}")
            if validation['total_incidents'] > 0:
                logger.info(f"  OIICS coverage: {(validation['incidents_with_oiics']/validation['total_incidents']*100):.1f}%")
            else:
                logger.info("  OIICS coverage: N/A (no incidents)")
            
            logger.info("\nOIICS field counts:")
            for field, count in validation['oiics_field_counts'].items():
                logger.info(f"  {field}: {count}")
            
            if validation['sample_incidents']:
                logger.info("\nSample incidents with OIICS data:")
                for i, incident in enumerate(validation['sample_incidents'][:3], 1):
                    logger.info(f"  {i}. {incident['company_name']} - {incident['incident_type']}")
                    oiics_fields = incident['oiics_fields']
                    if oiics_fields['body_part']:
                        logger.info(f"     Body Part: {oiics_fields['body_part']}")
                    if oiics_fields['source']:
                        logger.info(f"     Source: {oiics_fields['source']}")
        
        logger.info("\n🎉 Database reset and reimport completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Reset and reimport failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Reimport Existing Data with OIICS Fields
This script reimports existing OSHA data and populates the new OIICS fields
from the source data, then validates the results.
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident, Industry
from models import IncidentCreate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OIICSDataReimporter:
    """Reimport existing data with OIICS fields populated"""
    
    def __init__(self, db_path: str = "workplace_safety.db"):
        """Initialize the reimporter"""
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
                'Event': 'event_type',
                'Source': 'source',
                'SecondarySource': 'secondary_source',
                'Inspection': 'inspection_id',
                'FederalState': 'jurisdiction'
            }
        }
        
        # Alternative mappings for different column name variations
        self.alt_mappings = {
            'Part of Body': 'body_part',
            'Event': 'event_type',
            'Source': 'source',
            'Secondary Source': 'secondary_source'
        }
    
    def detect_data_type(self, df: pd.DataFrame) -> str:
        """Detect if this is SIR or fatality data"""
        columns = set(df.columns)
        
        # Check for SIR indicators
        sir_indicators = {'EventDate', 'NatureTitle', 'Part of Body Title', 'Hospitalized', 'Amputation'}
        sir_score = len(columns.intersection(sir_indicators))
        
        # Check for fatality indicators
        fatality_indicators = {'FatalityDate', 'Event', 'Source'}
        fatality_score = len(columns.intersection(fatality_indicators))
        
        if sir_score > fatality_score:
            return 'sir'
        elif fatality_score > sir_score:
            return 'fatality'
        else:
            return 'sir'  # Default to SIR
    
    def process_oiics_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
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
            
            # Try alternative mappings for missing fields
            for source_col, our_col in self.alt_mappings.items():
                if our_col not in oiics_record and source_col in row.index and pd.notna(row[source_col]):
                    oiics_record[our_col] = row[source_col]
            
            # Process boolean fields
            if 'hospitalized' in oiics_record:
                oiics_record['hospitalized'] = self._parse_boolean(oiics_record['hospitalized'])
            
            if 'amputation' in oiics_record:
                oiics_record['amputation'] = self._parse_boolean(oiics_record['amputation'])
            
            # Add original row data for matching
            oiics_record['original_data'] = row.to_dict()
            processed_data.append(oiics_record)
        
        return pd.DataFrame(processed_data)
    
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
    
    def match_and_update_incidents(self, oiics_df: pd.DataFrame, data_type: str) -> Tuple[int, int]:
        """Match OIICS data with existing incidents and update the database"""
        logger.info("Matching OIICS data with existing incidents...")
        
        db = self.SessionLocal()
        updated_count = 0
        matched_count = 0
        
        try:
            # Get all existing incidents
            existing_incidents = db.query(WorkplaceIncident).all()
            logger.info(f"Found {len(existing_incidents)} existing incidents to process")
            
            for incident in existing_incidents:
                # Try to find matching OIICS data
                oiics_match = self._find_oiics_match(incident, oiics_df, data_type)
                
                if oiics_match is not None:
                    matched_count += 1
                    # Update the incident with OIICS data
                    if self._update_incident_oiics(incident, oiics_match):
                        updated_count += 1
                
                # Log progress every 1000 incidents
                if matched_count % 1000 == 0 and matched_count > 0:
                    logger.info(f"Processed {matched_count} matches so far...")
            
            # Commit all changes
            db.commit()
            logger.info(f"Successfully updated {updated_count} incidents with OIICS data")
            
        except Exception as e:
            logger.error(f"Error updating incidents: {e}")
            db.rollback()
            raise
        except:
            logger.error("Unknown error updating incidents")
            db.rollback()
            raise
        finally:
            db.close()
        
        return updated_count, matched_count
    
    def _find_oiics_match(self, incident: WorkplaceIncident, oiics_df: pd.DataFrame, data_type: str) -> Optional[Dict]:
        """Find matching OIICS data for an incident"""
        # Try multiple matching strategies
        
        # Strategy 1: Match by OSHA ID
        if incident.osha_id:
            # Check if 'ID' column exists in oiics_df
            if 'ID' in oiics_df.columns:
                match = oiics_df[oiics_df['ID'] == incident.osha_id]
                if not match.empty:
                    return match.iloc[0]
            else:
                # Try to find ID in original_data
                for _, oiics_row in oiics_df.iterrows():
                    if 'original_data' in oiics_row:
                        orig_data = oiics_row['original_data']
                        if 'ID' in orig_data and str(orig_data['ID']) == incident.osha_id:
                            return oiics_row
        
        # Strategy 2: Match by company name and date
        if incident.company_name and incident.incident_date:
            # Normalize company name for matching
            company_normalized = self._normalize_company_name(incident.company_name)
            
            # Look for matches in the OIICS data
            for _, oiics_row in oiics_df.iterrows():
                if 'original_data' in oiics_row:
                    orig_data = oiics_row['original_data']
                    
                    # Check company name
                    if 'Employer' in orig_data and 'EventDate' in orig_data:
                        oiics_company = self._normalize_company_name(str(orig_data['Employer']))
                        oiics_date = self._parse_date(orig_data['EventDate'])
                        
                        if (oiics_company == company_normalized and 
                            oiics_date == incident.incident_date.date()):
                            return oiics_row
        
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
    
    def _update_incident_oiics(self, incident: WorkplaceIncident, oiics_data: Dict) -> bool:
        """Update incident with OIICS data"""
        try:
            # Update OIICS fields
            if 'body_part' in oiics_data:
                incident.body_part = oiics_data['body_part']
            
            if 'event_type' in oiics_data:
                incident.event_type = oiics_data['event_type']
            
            if 'source' in oiics_data:
                incident.source = oiics_data['source']
            
            if 'secondary_source' in oiics_data:
                incident.secondary_source = oiics_data['secondary_source']
            
            if 'hospitalized' in oiics_data:
                incident.hospitalized = oiics_data['hospitalized']
            
            if 'amputation' in oiics_data:
                incident.amputation = oiics_data['amputation']
            
            if 'inspection_id' in oiics_data:
                incident.inspection_id = oiics_data['inspection_id']
            
            if 'jurisdiction' in oiics_data:
                incident.jurisdiction = oiics_data['jurisdiction']
            
            incident.updated_at = datetime.now()
            return True
            
        except Exception as e:
            logger.warning(f"Error updating incident {incident.id}: {e}")
            return False
    
    def validate_oiics_data(self) -> Dict:
        """Validate the OIICS data after import"""
        logger.info("Validating OIICS data...")
        
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
    
    def run_reimport(self) -> Dict:
        """Run the complete reimport process"""
        logger.info("🚀 Starting OIICS data reimport process...")
        
        results = {
            'files_processed': [],
            'incidents_updated': 0,
            'validation_results': None,
            'errors': []
        }
        
        try:
            # Process each source data file
            source_files = list(self.raw_dir.glob("*.csv")) + list(self.raw_dir.glob("*.xlsx"))
            
            for source_file in source_files:
                logger.info(f"Processing source file: {source_file.name}")
                
                try:
                    # Read the file
                    if source_file.suffix == '.csv':
                        df = pd.read_csv(source_file)
                    else:
                        df = pd.read_excel(source_file)
                    
                    # Detect data type
                    data_type = self.detect_data_type(df)
                    logger.info(f"Detected data type: {data_type}")
                    
                    # Process OIICS data
                    oiics_df = self.process_oiics_data(df, data_type)
                    logger.info(f"Processed {len(oiics_df)} records with OIICS data")
                    
                    # Match and update incidents
                    try:
                        updated, matched = self.match_and_update_incidents(oiics_df, data_type)
                        results['incidents_updated'] += updated
                        
                        results['files_processed'].append({
                            'file': source_file.name,
                            'data_type': data_type,
                            'records_processed': len(oiics_df),
                            'incidents_updated': updated,
                            'incidents_matched': matched
                        })
                    except Exception as e:
                        error_msg = f"Error updating incidents from {source_file.name}: {e}"
                        logger.error(error_msg)
                        results['errors'].append(error_msg)
                    
                except Exception as e:
                    error_msg = f"Error processing {source_file.name}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Validate the results
            logger.info("Running validation...")
            results['validation_results'] = self.validate_oiics_data()
            
            logger.info("✅ OIICS data reimport completed successfully!")
            
        except Exception as e:
            error_msg = f"Fatal error during reimport: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            raise
        
        return results

def main():
    """Main function"""
    logger.info("🎯 Starting OIICS Data Reimport Process")
    
    try:
        # Initialize reimporter
        reimporter = OIICSDataReimporter()
        
        # Run the reimport
        results = reimporter.run_reimport()
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("📊 REIMPORT RESULTS SUMMARY")
        logger.info("="*60)
        
        logger.info(f"Files processed: {len(results['files_processed'])}")
        logger.info(f"Total incidents updated: {results['incidents_updated']}")
        
        if results['files_processed']:
            logger.info("\nFile processing details:")
            for file_result in results['files_processed']:
                logger.info(f"  📁 {file_result['file']} ({file_result['data_type']})")
                logger.info(f"     Records processed: {file_result['records_processed']}")
                logger.info(f"     Incidents updated: {file_result['incidents_updated']}")
                logger.info(f"     Incidents matched: {file_result['incidents_matched']}")
        
        if results['validation_results']:
            logger.info("\nValidation Results:")
            validation = results['validation_results']
            logger.info(f"  Total incidents: {validation['total_incidents']}")
            logger.info(f"  Incidents with OIICS data: {validation['incidents_with_oiics']}")
            logger.info(f"  OIICS coverage: {(validation['incidents_with_oiics']/validation['total_incidents']*100):.1f}%")
            
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
        
        if results['errors']:
            logger.warning(f"\n⚠️  {len(results['errors'])} errors encountered:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        logger.info("\n🎉 Reimport process completed!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Reimport failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

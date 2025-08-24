#!/usr/bin/env python3
"""
CSV Importer for OSHA Data
This module provides functionality to import real OSHA data from CSV files
"""

import pandas as pd
import csv
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, WorkplaceIncident, Industry
from models import IncidentCreate
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSHACSVImporter:
    """Import OSHA data from CSV files"""
    
    def __init__(self, db_session: Session = None):
        self.db_session = db_session or SessionLocal()
        
        # Common OSHA CSV column mappings
        self.column_mappings = {
            # Standard OSHA columns
            'osha_id': ['osha_id', 'id', 'incident_id', 'case_id'],
            'company_name': ['company_name', 'employer', 'establishment', 'company', 'employer_name'],
            'address': ['address', 'street_address', 'location', 'street'],
            'city': ['city', 'city_name', 'municipality'],
            'state': ['state', 'state_code', 'state_abbr', 'st'],
            'zip_code': ['zip_code', 'zip', 'postal_code', 'postal'],
            'incident_date': ['incident_date', 'date', 'fatality_date', 'accident_date', 'event_date'],
            'incident_type': ['incident_type', 'type', 'event_type', 'accident_type'],
            'industry': ['industry', 'naics_title', 'sector', 'business_type'],
            'naics_code': ['naics_code', 'naics', 'industry_code'],
            'description': ['description', 'summary', 'cause', 'details', 'narrative'],
            'investigation_status': ['status', 'investigation_status', 'case_status', 'status_code'],
            'citations_issued': ['citations_issued', 'citations', 'violations', 'citations_flag'],
            'penalty_amount': ['penalty_amount', 'penalty', 'fine', 'penalty_dollars'],
            'latitude': ['latitude', 'lat', 'y_coordinate'],
            'longitude': ['longitude', 'long', 'lng', 'x_coordinate']
        }
    
    def import_csv(self, file_path: str, validate_only: bool = False) -> Dict:
        """
        Import OSHA data from CSV file
        
        Args:
            file_path: Path to CSV file
            validate_only: If True, only validate without importing
            
        Returns:
            Dict with import results and statistics
        """
        logger.info(f"Starting CSV import from: {file_path}")
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'total_records': 0,
                'valid_records': 0,
                'imported_records': 0,
                'errors': []
            }
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Map columns to our schema
            mapped_data = self._map_columns(df)
            
            # Validate data
            validation_results = self._validate_data(mapped_data)
            
            if not validation_results['is_valid']:
                logger.error(f"Data validation failed: {validation_results['errors']}")
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'total_records': len(df),
                    'valid_records': validation_results['valid_count'],
                    'imported_records': 0,
                    'errors': validation_results['errors']
                }
            
            if validate_only:
                logger.info("Validation only mode - no data imported")
                return {
                    'success': True,
                    'message': 'Data validation successful',
                    'total_records': len(df),
                    'valid_records': validation_results['valid_count'],
                    'imported_records': 0,
                    'errors': validation_results['errors']
                }
            
            # Import valid data
            import_results = self._import_data(mapped_data)
            
            logger.info(f"Import completed: {import_results['imported_count']} records imported")
            
            return {
                'success': True,
                'message': 'Import completed successfully',
                'total_records': len(df),
                'valid_records': validation_results['valid_count'],
                'imported_records': import_results['imported_count'],
                'errors': validation_results['errors'] + import_results['errors']
            }
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_records': 0,
                'valid_records': 0,
                'imported_records': 0,
                'errors': [str(e)]
            }
    
    def _map_columns(self, df: pd.DataFrame) -> List[Dict]:
        """Map CSV columns to our data schema"""
        mapped_records = []
        
        for _, row in df.iterrows():
            mapped_record = {}
            
            # Map each field using our column mappings
            for target_field, possible_columns in self.column_mappings.items():
                value = None
                
                # Try to find a matching column
                for col in possible_columns:
                    if col in df.columns:
                        value = row[col]
                        break
                
                # Set default values for required fields
                if target_field == 'incident_type' and not value:
                    value = 'fatality'  # Default for OSHA data
                elif target_field == 'investigation_status' and not value:
                    value = 'Open'
                elif target_field == 'citations_issued' and not value:
                    value = False
                elif target_field == 'penalty_amount' and not value:
                    value = 0.0
                elif target_field == 'created_at' and not value:
                    value = datetime.now()
                elif target_field == 'updated_at' and not value:
                    value = datetime.now()
                
                # Convert date strings to datetime objects
                if target_field == 'incident_date' and isinstance(value, str):
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        # Try alternative date formats
                        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                            try:
                                value = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            # If all formats fail, use today's date
                            value = datetime.now()
                
                mapped_record[target_field] = value
            
            # Generate OSHA ID if not present
            if not mapped_record.get('osha_id') or pd.isna(mapped_record.get('osha_id')):
                mapped_record['osha_id'] = f"CSV-{datetime.now().year}-{len(mapped_records):06d}"
            
            mapped_records.append(mapped_record)
        
        return mapped_records
    
    def _validate_data(self, data: List[Dict]) -> Dict:
        """Validate imported data"""
        errors = []
        valid_count = 0
        
        for i, record in enumerate(data):
            record_errors = []
            
            # Check required fields
            required_fields = ['company_name', 'state', 'incident_date']
            for field in required_fields:
                if not record.get(field):
                    record_errors.append(f"Missing required field: {field}")
            
            # Validate date format
            if record.get('incident_date'):
                try:
                    if isinstance(record['incident_date'], str):
                        datetime.strptime(record['incident_date'], '%Y-%m-%d')
                except ValueError:
                    record_errors.append(f"Invalid date format: {record['incident_date']}")
            
            # Validate numeric fields
            if record.get('penalty_amount'):
                try:
                    float(record['penalty_amount'])
                except (ValueError, TypeError):
                    record_errors.append(f"Invalid penalty amount: {record['penalty_amount']}")
            
            if record.get('latitude') and pd.notna(record.get('latitude')):
                try:
                    lat = float(record['latitude'])
                    if not -90 <= lat <= 90:
                        record_errors.append(f"Invalid latitude: {lat}")
                except (ValueError, TypeError):
                    record_errors.append(f"Invalid latitude: {record['latitude']}")
            
            if record.get('longitude') and pd.notna(record.get('longitude')):
                try:
                    lng = float(record['longitude'])
                    if not -180 <= lng <= 180:
                        record_errors.append(f"Invalid longitude: {lng}")
                except (ValueError, TypeError):
                    record_errors.append(f"Invalid longitude: {record['longitude']}")
            
            if record_errors:
                errors.append(f"Row {i+1}: {'; '.join(record_errors)}")
            else:
                valid_count += 1
        
        return {
            'is_valid': valid_count > 0,
            'valid_count': valid_count,
            'error_count': len(errors),
            'errors': errors
        }
    
    def _import_data(self, data: List[Dict]) -> Dict:
        """Import validated data into database"""
        imported_count = 0
        errors = []
        
        try:
            batch_size = 1000
            for i, record in enumerate(data):
                try:
                    # Check if record already exists
                    existing = self.db_session.query(WorkplaceIncident).filter_by(
                        osha_id=record['osha_id']
                    ).first()
                    
                    if existing:
                        logger.warning(f"Record already exists: {record['osha_id']}")
                        continue
                    
                    # Create new incident
                    incident = WorkplaceIncident(**record)
                    self.db_session.add(incident)
                    imported_count += 1
                    
                    # Commit in batches to avoid memory issues
                    if (i + 1) % batch_size == 0:
                        try:
                            self.db_session.commit()
                            logger.info(f"Committed batch of {batch_size} records. Total imported: {imported_count}")
                        except Exception as commit_error:
                            logger.error(f"Commit error: {commit_error}")
                            self.db_session.rollback()
                            # Continue with next batch
                    
                except Exception as e:
                    error_msg = f"Error importing record {record.get('osha_id', 'Unknown')}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    # Rollback this record and continue
                    try:
                        self.db_session.rollback()
                    except:
                        pass
            
            # Commit any remaining records
            if imported_count % batch_size != 0:
                try:
                    self.db_session.commit()
                except Exception as commit_error:
                    logger.error(f"Final commit error: {commit_error}")
                    self.db_session.rollback()
            
            logger.info(f"Successfully imported {imported_count} records")
            
        except Exception as e:
            try:
                self.db_session.rollback()
            except:
                pass
            error_msg = f"Database error during import: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        return {
            'imported_count': imported_count,
            'errors': errors
        }
    
    def export_sample_csv(self, output_path: str = "osha_sample_template.csv"):
        """Export a sample CSV template for users to fill in"""
        sample_data = [
            {
                'company_name': 'Sample Company Inc',
                'address': '123 Main Street',
                'city': 'Anytown',
                'state': 'CA',
                'zip_code': '90210',
                'incident_date': '2024-01-15',
                'incident_type': 'fatality',
                'industry': 'Construction',
                'naics_code': '236220',
                'description': 'Worker fell from scaffolding',
                'investigation_status': 'Open',
                'citations_issued': 'true',
                'penalty_amount': '15000.00',
                'latitude': '34.0522',
                'longitude': '-118.2437'
            }
        ]
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(sample_data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(sample_data)
            
            logger.info(f"Sample CSV template exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting sample CSV: {e}")
            return False

def main():
    """Command line interface for CSV import"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import OSHA data from CSV')
    parser.add_argument('file_path', nargs='?', help='Path to CSV file')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not import')
    parser.add_argument('--export-template', action='store_true', help='Export sample CSV template')
    
    args = parser.parse_args()
    
    importer = OSHACSVImporter()
    
    if args.export_template:
        importer.export_sample_csv()
        return
    
    if not args.file_path:
        print("❌ Please provide a file path or use --export-template")
        return
    
    # Import or validate CSV
    results = importer.import_csv(args.file_path, validate_only=args.validate_only)
    
    if results['success']:
        print(f"✅ {results['message']}")
        print(f"📊 Total records: {results['total_records']}")
        print(f"✅ Valid records: {results['valid_records']}")
        print(f"📥 Imported records: {results['imported_records']}")
        
        if results['errors']:
            print(f"⚠️  Errors: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
    else:
        print(f"❌ Import failed: {results['error']}")
        if results['errors']:
            for error in results['errors']:
                print(f"   - {error}")

if __name__ == "__main__":
    main()

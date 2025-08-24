#!/usr/bin/env python3
"""
SIR Data Processor
Processes Serious Injury Reports data from OSHA and converts to our importable format
"""

import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SIRDataProcessor:
    """Process SIR (Serious Injury Reports) data from OSHA"""
    
    def __init__(self):
        self.raw_file = "../data/osha/raw/January2015toFebruary2025.csv"
        self.processed_file = "../data/osha/processed/sir_data_processed.csv"
        
        # SIR to our schema mapping
        self.column_mapping = {
            'ID': 'osha_id',
            'Employer': 'company_name',
            'Address1': 'address',
            'City': 'city',
            'State': 'state',
            'Zip': 'zip_code',
            'EventDate': 'incident_date',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Primary NAICS': 'naics_code',
            'Final Narrative': 'description',
            'NatureTitle': 'incident_type',
            'Part of Body Title': 'body_part',
            'EventTitle': 'event_type',
            'SourceTitle': 'source',
            'Secondary Source Title': 'secondary_source',
            'Hospitalized': 'hospitalized',
            'Amputation': 'amputation',
            'Inspection': 'inspection_id',
            'FederalState': 'jurisdiction'
        }
    
    def process_sir_data(self):
        """Process the SIR data file"""
        logger.info("Starting SIR data processing...")
        
        if not os.path.exists(self.raw_file):
            logger.error(f"Raw file not found: {self.raw_file}")
            return False
        
        try:
            # Read the CSV file
            logger.info("Reading SIR data file...")
            df = pd.read_csv(self.raw_file)
            logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
            
            # Display column information
            logger.info("Original columns:")
            for i, col in enumerate(df.columns):
                logger.info(f"  {i+1:2d}. {col}")
            
            # Process and clean the data
            processed_df = self._process_dataframe(df)
            
            # Save processed data
            self._save_processed_data(processed_df)
            
            # Generate summary statistics
            self._generate_summary(processed_df)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing SIR data: {e}")
            return False
    
    def _process_dataframe(self, df):
        """Process the dataframe and map to our schema"""
        logger.info("Processing and mapping data...")
        
        # Create new dataframe with our schema
        processed_data = []
        
        for idx, row in df.iterrows():
            if idx % 10000 == 0:
                logger.info(f"Processing record {idx:,} of {len(df):,}")
            
            # Map SIR data to our schema
            processed_record = self._map_record(row)
            
            if processed_record:
                processed_data.append(processed_record)
        
        # Convert to dataframe
        processed_df = pd.DataFrame(processed_data)
        logger.info(f"Processed {len(processed_df)} records")
        
        return processed_df
    
    def _map_record(self, row):
        """Map a single SIR record to our schema"""
        try:
            # Basic mapping
            mapped = {}
            
            # Map known columns
            for sir_col, our_col in self.column_mapping.items():
                if sir_col in row.index:
                    mapped[our_col] = row[sir_col]
            
            # Set required fields with defaults
            mapped['incident_type'] = mapped.get('incident_type', 'serious_injury')
            mapped['investigation_status'] = 'Reported'
            mapped['citations_issued'] = False
            mapped['penalty_amount'] = 0.0
            mapped['created_at'] = datetime.now().strftime('%Y-%m-%d')
            mapped['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            
            # Process incident type
            if pd.notna(mapped.get('nature_title')):
                mapped['incident_type'] = self._categorize_incident(mapped['nature_title'])
            
            # Process date
            if pd.notna(mapped.get('incident_date')):
                mapped['incident_date'] = self._parse_date(mapped['incident_date'])
            
            # Process coordinates
            if pd.notna(mapped.get('latitude')) and pd.notna(mapped.get('longitude')):
                try:
                    mapped['latitude'] = float(mapped['latitude'])
                    mapped['longitude'] = float(mapped['longitude'])
                except (ValueError, TypeError):
                    mapped['latitude'] = None
                    mapped['longitude'] = None
            
            # Process NAICS code
            if pd.notna(mapped.get('naics_code')):
                try:
                    mapped['naics_code'] = str(int(mapped['naics_code']))
                except (ValueError, TypeError):
                    mapped['naics_code'] = ''
            
            # Generate industry from NAICS if available
            if mapped.get('naics_code'):
                mapped['industry'] = self._get_industry_from_naics(mapped['naics_code'])
            else:
                mapped['industry'] = 'Unknown'
            
            # Validate required fields
            if not mapped.get('company_name') or not mapped.get('state'):
                return None
            
            return mapped
            
        except Exception as e:
            logger.warning(f"Error mapping record {row.get('ID', 'Unknown')}: {e}")
            return None
    
    def _categorize_incident(self, nature_title):
        """Categorize incident type from nature title"""
        if pd.isna(nature_title):
            return 'serious_injury'
        
        nature_lower = str(nature_title).lower()
        
        if 'fracture' in nature_lower:
            return 'fracture'
        elif 'burn' in nature_lower:
            return 'burn'
        elif 'amputation' in nature_lower:
            return 'amputation'
        elif 'fall' in nature_lower:
            return 'fall'
        elif 'cut' in nature_lower or 'laceration' in nature_lower:
            return 'cut'
        elif 'strain' in nature_lower or 'sprain' in nature_lower:
            return 'strain'
        else:
            return 'serious_injury'
    
    def _parse_date(self, date_str):
        """Parse date string to YYYY-MM-DD format"""
        if pd.isna(date_str):
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try different date formats
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                try:
                    parsed_date = datetime.strptime(str(date_str), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If all formats fail, return today's date
            logger.warning(f"Could not parse date: {date_str}")
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.warning(f"Date parsing error for {date_str}: {e}")
            return datetime.now().strftime('%Y-%m-%d')
    
    def _get_industry_from_naics(self, naics_code):
        """Get industry name from NAICS code"""
        # Basic NAICS industry mapping
        naics_industries = {
            '11': 'Agriculture, Forestry, Fishing and Hunting',
            '21': 'Mining, Quarrying, and Oil and Gas Extraction',
            '22': 'Utilities',
            '23': 'Construction',
            '31': 'Manufacturing',
            '32': 'Manufacturing',
            '33': 'Manufacturing',
            '42': 'Wholesale Trade',
            '44': 'Retail Trade',
            '45': 'Retail Trade',
            '48': 'Transportation and Warehousing',
            '49': 'Transportation and Warehousing',
            '51': 'Information',
            '52': 'Finance and Insurance',
            '53': 'Real Estate and Rental and Leasing',
            '54': 'Professional, Scientific, and Technical Services',
            '55': 'Management of Companies and Enterprises',
            '56': 'Administrative and Support and Waste Management',
            '61': 'Educational Services',
            '62': 'Health Care and Social Assistance',
            '71': 'Arts, Entertainment, and Recreation',
            '72': 'Accommodation and Food Services',
            '81': 'Other Services (except Public Administration)',
            '92': 'Public Administration'
        }
        
        if naics_code and len(str(naics_code)) >= 2:
            first_two = str(naics_code)[:2]
            return naics_industries.get(first_two, 'Unknown')
        
        return 'Unknown'
    
    def _save_processed_data(self, df):
        """Save processed data to CSV"""
        logger.info(f"Saving processed data to {self.processed_file}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.processed_file), exist_ok=True)
        
        # Save to CSV
        df.to_csv(self.processed_file, index=False)
        logger.info(f"Processed data saved: {self.processed_file}")
        
        # Also save a sample for review
        sample_file = self.processed_file.replace('.csv', '_sample.csv')
        df.head(100).to_csv(sample_file, index=False)
        logger.info(f"Sample data saved: {sample_file}")
    
    def _generate_summary(self, df):
        """Generate summary statistics"""
        logger.info("Generating summary statistics...")
        
        print("\n" + "="*60)
        print("📊 SIR DATA PROCESSING SUMMARY")
        print("="*60)
        print(f"Total records processed: {len(df):,}")
        print(f"Records with coordinates: {df['latitude'].notna().sum():,}")
        print(f"Records with NAICS codes: {df['naics_code'].notna().sum():,}")
        
        print(f"\n📅 Date range:")
        if 'incident_date' in df.columns:
            dates = pd.to_datetime(df['incident_date'], errors='coerce')
            valid_dates = dates.dropna()
            if len(valid_dates) > 0:
                print(f"   Earliest: {valid_dates.min().strftime('%Y-%m-%d')}")
                print(f"   Latest: {valid_dates.max().strftime('%Y-%m-%d')}")
        
        print(f"\n🏭 Top industries:")
        if 'industry' in df.columns:
            industry_counts = df['industry'].value_counts().head(10)
            for industry, count in industry_counts.items():
                print(f"   {industry}: {count:,}")
        
        print(f"\n📍 Top states:")
        if 'state' in df.columns:
            state_counts = df['state'].value_counts().head(10)
            for state, count in state_counts.items():
                print(f"   {state}: {count:,}")
        
        print(f"\n💼 Top companies:")
        if 'company_name' in df.columns:
            company_counts = df['company_name'].value_counts().head(10)
            for company, count in company_counts.items():
                print(f"   {company}: {count:,}")
        
        print("="*60)

def main():
    """Main processing function"""
    processor = SIRDataProcessor()
    
    print("🏭 Processing SIR (Serious Injury Reports) Data")
    print("="*50)
    
    success = processor.process_sir_data()
    
    if success:
        print("\n✅ SIR data processing completed successfully!")
        print(f"📁 Processed file: {processor.processed_file}")
        print("\nNext steps:")
        print("1. Review the processed data")
        print("2. Validate with: python3 csv_importer.py ../data/osha/processed/sir_data_processed.csv --validate-only")
        print("3. Import data: python3 csv_importer.py ../data/osha/processed/sir_data_processed.csv")
    else:
        print("\n❌ SIR data processing failed!")
        print("Check the logs above for errors.")

if __name__ == "__main__":
    main()

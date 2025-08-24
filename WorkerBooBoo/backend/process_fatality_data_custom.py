#!/usr/bin/env python3
"""
Custom Fatality Data Processor
Processes the specific fatality data format from the user's data2.xlsx file
"""

import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomFatalityDataProcessor:
    """Process the specific fatality data format"""

    def __init__(self):
        self.raw_file = "../data/osha/raw/fatality_data.csv"
        self.processed_file = "../data/osha/processed/fatality_data_processed.csv"

        # Map the actual column names to our schema
        self.column_mapping = {
            'Opening Conference Date': 'conference_date',
            'Event Date': 'incident_date',
            'Inspection #': 'inspection_id',
            'Establishment Name': 'company_name',
            'Site NAICS': 'naics_code',
            'Site City': 'city',
            'Site State': 'state',
            'Site County': 'county',
            'Jurisdiction': 'jurisdiction',
            'Victim Name (Age)': 'victim_info'
        }

    def process_fatality_data(self):
        """Process the fatality data file"""
        logger.info("Starting custom fatality data processing...")

        if not os.path.exists(self.raw_file):
            logger.error(f"Raw file not found: {self.raw_file}")
            return False

        try:
            # Read the CSV file
            logger.info("Reading fatality data file...")
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
            logger.error(f"Error processing fatality data: {e}")
            return False

    def _process_dataframe(self, df):
        """Process the dataframe and map to our schema"""
        logger.info("Processing and mapping fatality data...")

        # Create new dataframe with our schema
        processed_data = []

        for idx, row in df.iterrows():
            if idx % 5000 == 0:
                logger.info(f"Processing record {idx:,} of {len(df):,}")

            # Map fatality data to our schema
            processed_record = self._map_record(row, idx)

            if processed_record:
                processed_data.append(processed_record)

        # Convert to dataframe
        processed_df = pd.DataFrame(processed_data)
        logger.info(f"Processed {len(processed_df)} records")

        return processed_df

    def _map_record(self, row, idx):
        """Map a single fatality record to our schema"""
        try:
            # Basic mapping
            mapped = {}

            # Map known columns
            for source_col, our_col in self.column_mapping.items():
                if source_col in row.index:
                    mapped[our_col] = row[source_col]

            # Set required fields with defaults for fatalities
            mapped['incident_type'] = 'fatality'
            mapped['investigation_status'] = 'Closed'
            mapped['citations_issued'] = False
            mapped['penalty_amount'] = 0.0
            mapped['created_at'] = datetime.now().strftime('%Y-%m-%d')
            mapped['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            
            # Generate unique OSHA ID for fatalities
            if pd.notna(mapped.get('inspection_id')):
                # Use inspection ID + row index to ensure uniqueness
                mapped['osha_id'] = f"FATALITY-{mapped['inspection_id']}-{idx:06d}"
            else:
                mapped['osha_id'] = f"FATALITY-{idx:06d}"

            # Process incident type based on victim info or other clues
            mapped['incident_type'] = self._categorize_fatality(row)

            # Process date - use Event Date if available, otherwise Opening Conference Date
            incident_date = self._parse_date(row.get('Event Date'))
            if incident_date:
                mapped['incident_date'] = incident_date
            else:
                # Fall back to conference date
                mapped['incident_date'] = self._parse_date(row.get('Opening Conference Date'))

            # Process coordinates - we don't have them, so set to None
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

            # Extract age from victim info if available
            if pd.notna(mapped.get('victim_info')):
                mapped['victim_age'] = self._extract_age(mapped['victim_info'])

            # Set address fields
            mapped['address'] = ''
            mapped['zip_code'] = ''

            # Validate required fields
            if not mapped.get('company_name') or not mapped.get('state'):
                return None

            return mapped

        except Exception as e:
            logger.warning(f"Error mapping record {row.get('Inspection #', 'Unknown')}: {e}")
            return None

    def _categorize_fatality(self, row):
        """Categorize fatality type based on available information"""
        # For now, categorize as general fatality
        # In the future, we could analyze victim info or other fields
        return 'fatality'

    def _extract_age(self, victim_info):
        """Extract age from victim info string like 'John Doe (45)'"""
        if pd.isna(victim_info):
            return None
        
        try:
            # Look for age in parentheses
            import re
            age_match = re.search(r'\((\d+)\)', str(victim_info))
            if age_match:
                return int(age_match.group(1))
        except:
            pass
        
        return None

    def _parse_date(self, date_str):
        """Parse date string to YYYY-MM-DD format"""
        if pd.isna(date_str):
            return None

        try:
            # Handle pandas NaT
            if pd.isna(date_str) or str(date_str) == 'NaT':
                return None

            # Try different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y']:
                try:
                    if isinstance(date_str, str):
                        parsed_date = datetime.strptime(date_str, fmt)
                    else:
                        # Handle pandas datetime objects
                        parsed_date = pd.to_datetime(date_str).to_pydatetime()
                    return parsed_date.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue

            # If all formats fail, return None
            logger.warning(f"Could not parse date: {date_str}")
            return None

        except Exception as e:
            logger.warning(f"Date parsing error for {date_str}: {e}")
            return None

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
        print("💀 FATALITY DATA PROCESSING SUMMARY")
        print("="*60)
        print(f"Total fatality records processed: {len(df):,}")
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

        print(f"\n👥 Victim age statistics:")
        if 'victim_age' in df.columns:
            ages = df['victim_age'].dropna()
            if len(ages) > 0:
                print(f"   Average age: {ages.mean():.1f}")
                print(f"   Youngest: {ages.min()}")
                print(f"   Oldest: {ages.max()}")

        print("="*60)

def main():
    """Main processing function"""
    processor = CustomFatalityDataProcessor()

    print("💀 Processing Custom Fatality Data")
    print("="*50)

    success = processor.process_fatality_data()

    if success:
        print("\n✅ Fatality data processing completed successfully!")
        print(f"📁 Processed file: {processor.processed_file}")
        print("\nNext steps:")
        print("1. Review the processed data")
        print("2. Validate with: python3 csv_importer.py ../data/osha/processed/fatality_data_processed.csv --validate-only")
        print("3. Import data: python3 csv_importer.py ../data/osha/processed/fatality_data_processed.csv")
    else:
        print("\n❌ Fatality data processing failed!")
        print("Check the logs above for errors.")

if __name__ == "__main__":
    main()

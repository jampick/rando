#!/usr/bin/env python3
"""
Debug OIICS Matching
Simple script to test the OIICS data matching logic
"""

import sys
import pandas as pd
from pathlib import Path
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident

def debug_oiics_matching():
    """Debug the OIICS matching logic"""
    print("🔍 Debugging OIICS Matching Logic")
    
    # Load a sample of OIICS data
    data_file = Path("../data/osha/raw/January2015toFebruary2025.csv")
    print(f"Loading data from: {data_file}")
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    # Load sample data
    df = pd.read_csv(data_file, nrows=100)
    print(f"✓ Loaded {len(df)} sample records")
    print(f"Columns: {list(df.columns)}")
    
    # Show first few rows
    print("\nFirst 3 rows:")
    print(df[['ID', 'Employer', 'EventDate', 'Part of Body Title', 'SourceTitle']].head(3))
    
    # Check database
    db = SessionLocal()
    try:
        # Get a few incidents
        incidents = db.query(WorkplaceIncident).limit(5).all()
        print(f"\n✓ Found {len(incidents)} incidents in database")
        
        for i, incident in enumerate(incidents):
            print(f"\nIncident {i+1}:")
            print(f"  OSHA ID: {incident.osha_id}")
            print(f"  Company: {incident.company_name}")
            print(f"  Date: {incident.incident_date}")
            print(f"  Type: {incident.incident_type}")
            
            # Try to find a match
            if incident.osha_id:
                matches = df[df['ID'] == incident.osha_id]
                if not matches.empty:
                    print(f"  ✓ Found {len(matches)} OIICS matches by ID")
                    match = matches.iloc[0]
                    print(f"    Body Part: {match.get('Part of Body Title', 'N/A')}")
                    print(f"    Source: {match.get('SourceTitle', 'N/A')}")
                    print(f"    Event: {match.get('EventTitle', 'N/A')}")
                else:
                    print(f"  ❌ No OIICS matches found by ID")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_oiics_matching()





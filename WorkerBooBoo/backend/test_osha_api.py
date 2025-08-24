#!/usr/bin/env python3
"""
Test script for OSHA API integration
This script tests the real OSHA fatalities API to see what data we can fetch
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_processor import OSHADataProcessor

def test_osha_api():
    """Test the OSHA API integration"""
    print("🧪 Testing OSHA API Integration")
    print("=" * 50)
    
    # Initialize the data processor
    processor = OSHADataProcessor()
    
    # Test 1: Basic API connectivity
    print("\n1️⃣ Testing basic API connectivity...")
    test_urls = [
        "https://www.osha.gov/fatalities/api/fatalities",
        "https://data.osha.gov/api/v1/fatalities",
        "https://www.osha.gov/data/fatalities"
    ]
    
    for url in test_urls:
        print(f"\n   Testing: {url}")
        try:
            response = processor.session.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success! Data keys: {list(data.keys()) if isinstance(data, dict) else 'List data'}")
                    if isinstance(data, dict) and len(data) > 0:
                        print(f"   Sample data structure: {json.dumps(list(data.items())[:3], indent=2)}")
                except json.JSONDecodeError:
                    print(f"   ⚠️  Response is not JSON: {response.text[:200]}...")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 2: Try to fetch actual fatality data
    print("\n2️⃣ Testing fatality data fetching...")
    try:
        # Try to get recent fatalities
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        print(f"   Fetching fatalities from {start_date} to {end_date}")
        fatalities = processor.fetch_fatality_data(start_date=start_date, end_date=end_date)
        
        if fatalities:
            print(f"   ✅ Successfully fetched {len(fatalities)} fatalities")
            if len(fatalities) > 0:
                print(f"   Sample fatality: {json.dumps(fatalities[0], indent=2, default=str)}")
        else:
            print("   ❌ No fatalities fetched")
            
    except Exception as e:
        print(f"   ❌ Error fetching fatalities: {e}")
    
    # Test 3: Test rate limiting
    print("\n3️⃣ Testing rate limiting...")
    start_time = datetime.now()
    for i in range(3):
        print(f"   Request {i+1}: {datetime.now().strftime('%H:%M:%S')}")
        try:
            response = processor.session.get("https://www.osha.gov", timeout=5)
            print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"   Total time for 3 requests: {duration:.2f} seconds")
    
    # Test 4: Check if we can access the main OSHA page
    print("\n4️⃣ Testing main OSHA page access...")
    try:
        response = processor.session.get("https://www.osha.gov", timeout=10)
        print(f"   Main page status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Can access main OSHA page")
            # Look for any API endpoints mentioned
            content = response.text.lower()
            if 'api' in content:
                print("   📍 API endpoints mentioned on main page")
            if 'fatalities' in content:
                print("   📍 Fatalities data mentioned on main page")
        else:
            print(f"   ❌ Cannot access main OSHA page")
    except Exception as e:
        print(f"   ❌ Error accessing main page: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

if __name__ == "__main__":
    test_osha_api()

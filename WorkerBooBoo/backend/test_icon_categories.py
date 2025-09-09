#!/usr/bin/env python3
"""
Test Script: Icon Category Implementation
This script tests the icon category implementation to ensure everything is working correctly
"""

import os
import sys
import logging
import requests
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident
from sqlalchemy import func
from icon_categories import icon_mapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_icon_mapper():
    """Test the icon category mapper with sample data"""
    logger.info("🧪 Testing Icon Category Mapper...")
    
    # Test cases
    test_cases = [
        {
            'name': 'Amputation Case',
            'body_part': 'Finger(s), fingernail(s), n.e.c.',
            'event_type': 'Struck by falling object or equipment, unspecified',
            'source': 'Ramps, loading docks, dock plates',
            'hospitalized': True,
            'amputation': True,
            'incident_type': 'Amputations',
            'expected': {
                'icon_injury': 'amputation',
                'icon_event': 'struck_by',
                'icon_source': 'structures_surfaces',
                'icon_severity': 'amputation'
            }
        },
        {
            'name': 'Fracture Case',
            'body_part': 'Lower leg(s)',
            'event_type': 'Fall from elevation',
            'source': 'Ladders, scaffolds, manlifts',
            'hospitalized': True,
            'amputation': False,
            'incident_type': 'Fractures',
            'expected': {
                'icon_injury': 'fracture',
                'icon_event': 'fall',
                'icon_source': 'ladders_scaffolds',
                'icon_severity': 'hospitalized'
            }
        },
        {
            'name': 'Burn Case',
            'body_part': 'Leg(s), n.e.c.',
            'event_type': 'Contact with hot object or substance',
            'source': 'Welding, cutting, and blow torches',
            'hospitalized': False,
            'amputation': False,
            'incident_type': 'Burns',
            'expected': {
                'icon_injury': 'burn',
                'icon_event': 'other',
                'icon_source': 'fire_heat',
                'icon_severity': 'minor'
            }
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        logger.info(f"Testing: {test_case['name']}")
        
        result = icon_mapper.map_all_categories(
            body_part=test_case['body_part'],
            event_type=test_case['event_type'],
            source=test_case['source'],
            hospitalized=test_case['hospitalized'],
            amputation=test_case['amputation'],
            incident_type=test_case['incident_type']
        )
        
        # Check results
        all_correct = True
        for field, expected_value in test_case['expected'].items():
            actual_value = result[field]
            if actual_value != expected_value:
                logger.warning(f"  ❌ {field}: expected '{expected_value}', got '{actual_value}'")
                all_correct = False
            else:
                logger.info(f"  ✅ {field}: '{actual_value}'")
        
        if all_correct:
            passed += 1
            logger.info(f"  ✅ Test passed!")
        else:
            logger.warning(f"  ❌ Test failed!")
        
        logger.info("")
    
    logger.info(f"📊 Icon Mapper Test Results: {passed}/{total} tests passed")
    return passed == total

def test_database_icon_fields():
    """Test that icon fields are properly populated in the database"""
    logger.info("🗄️ Testing Database Icon Fields...")
    
    db = SessionLocal()
    try:
        # Check total incidents
        total_incidents = db.query(WorkplaceIncident).count()
        logger.info(f"Total incidents: {total_incidents}")
        
        # Check incidents with icon fields
        incidents_with_icons = db.query(WorkplaceIncident).filter(
            (WorkplaceIncident.icon_injury.isnot(None)) &
            (WorkplaceIncident.icon_event.isnot(None)) &
            (WorkplaceIncident.icon_source.isnot(None)) &
            (WorkplaceIncident.icon_severity.isnot(None))
        ).count()
        
        coverage = (incidents_with_icons / total_incidents) * 100
        logger.info(f"Incidents with icon fields: {incidents_with_icons}")
        logger.info(f"Icon coverage: {coverage:.1f}%")
        
        # Get icon distributions
        icon_injury_counts = db.query(WorkplaceIncident.icon_injury, 
                                     func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_injury).all()
        
        logger.info("Icon Injury Distribution:")
        for category, count in icon_injury_counts:
            logger.info(f"  {category}: {count}")
        
        # Test specific record
        test_record = db.query(WorkplaceIncident).filter(
            WorkplaceIncident.osha_id == '2015042008'
        ).first()
        
        if test_record:
            logger.info(f"Test record (OSHA ID 2015042008):")
            logger.info(f"  icon_injury: {test_record.icon_injury}")
            logger.info(f"  icon_event: {test_record.icon_event}")
            logger.info(f"  icon_source: {test_record.icon_source}")
            logger.info(f"  icon_severity: {test_record.icon_severity}")
        
        success = coverage >= 99.0  # Expect at least 99% coverage
        logger.info(f"Database test {'✅ PASSED' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        logger.error(f"❌ Database test error: {e}")
        return False
    finally:
        db.close()

def test_api_endpoints():
    """Test that API endpoints work with icon fields"""
    logger.info("🌐 Testing API Endpoints...")
    
    try:
        # Test statistics endpoint
        response = requests.get('http://localhost:8000/api/statistics/overview')
        if response.status_code == 200:
            logger.info("✅ Statistics endpoint working")
        else:
            logger.error(f"❌ Statistics endpoint failed: {response.status_code}")
            return False
        
        # Test incidents endpoint
        response = requests.get('http://localhost:8000/api/incidents/?limit=1')
        if response.status_code == 200:
            data = response.json()
            if data['incidents'] and 'icon_injury' in data['incidents'][0]:
                logger.info("✅ Incidents endpoint working with icon fields")
            else:
                logger.error("❌ Incidents endpoint missing icon fields")
                return False
        else:
            logger.error(f"❌ Incidents endpoint failed: {response.status_code}")
            return False
        
        # Test maps endpoint
        response = requests.get('http://localhost:8000/api/maps/incidents?limit=1')
        if response.status_code == 200:
            data = response.json()
            if data['incidents'] and 'icon_injury' in data['incidents'][0]:
                logger.info("✅ Maps endpoint working with icon fields")
            else:
                logger.error("❌ Maps endpoint missing icon fields")
                return False
        else:
            logger.error(f"❌ Maps endpoint failed: {response.status_code}")
            return False
        
        logger.info("API test ✅ PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ API test error: {e}")
        return False

def test_icon_category_distributions():
    """Test that icon categories have reasonable distributions"""
    logger.info("📊 Testing Icon Category Distributions...")
    
    db = SessionLocal()
    try:
        # Get distributions
        icon_injury_counts = db.query(WorkplaceIncident.icon_injury, 
                                     func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_injury).all()
        
        icon_event_counts = db.query(WorkplaceIncident.icon_event, 
                                    func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_event).all()
        
        icon_source_counts = db.query(WorkplaceIncident.icon_source, 
                                     func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_source).all()
        
        icon_severity_counts = db.query(WorkplaceIncident.icon_severity, 
                                       func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_severity).all()
        
        # Check for reasonable distributions
        total_incidents = db.query(WorkplaceIncident).count()
        
        # Check that 'other' category isn't too dominant (>80%)
        injury_other_pct = next((count/total_incidents*100 for category, count in icon_injury_counts if category == 'other'), 0)
        event_other_pct = next((count/total_incidents*100 for category, count in icon_event_counts if category == 'other'), 0)
        source_other_pct = next((count/total_incidents*100 for category, count in icon_source_counts if category == 'other'), 0)
        
        logger.info(f"Injury 'other' category: {injury_other_pct:.1f}%")
        logger.info(f"Event 'other' category: {event_other_pct:.1f}%")
        logger.info(f"Source 'other' category: {source_other_pct:.1f}%")
        
        # Check that we have reasonable category diversity
        injury_categories = len(icon_injury_counts)
        event_categories = len(icon_event_counts)
        source_categories = len(icon_source_counts)
        severity_categories = len(icon_severity_counts)
        
        logger.info(f"Number of categories:")
        logger.info(f"  Injury: {injury_categories}")
        logger.info(f"  Event: {event_categories}")
        logger.info(f"  Source: {source_categories}")
        logger.info(f"  Severity: {severity_categories}")
        
        # Success criteria
        success = (
            injury_other_pct < 80 and
            event_other_pct < 80 and
            source_other_pct < 80 and
            injury_categories >= 5 and
            event_categories >= 5 and
            source_categories >= 8 and
            severity_categories >= 3
        )
        
        logger.info(f"Distribution test {'✅ PASSED' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        logger.error(f"❌ Distribution test error: {e}")
        return False
    finally:
        db.close()

def main():
    """Run all tests"""
    logger.info("🚀 Starting Icon Category Tests")
    
    tests = [
        ("Icon Mapper", test_icon_mapper),
        ("Database Icon Fields", test_database_icon_fields),
        ("API Endpoints", test_api_endpoints),
        ("Icon Category Distributions", test_icon_category_distributions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"📊 FINAL TEST RESULTS: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Icon category implementation is working correctly.")
    else:
        logger.error("❌ Some tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main()

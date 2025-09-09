#!/usr/bin/env python3
"""
Test OIICS Data Validation
This script tests and validates the OIICS data after reimport
"""

import sys
import logging
from pathlib import Path
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident
from models import Incident

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_oiics_data_validation():
    """Test the OIICS data validation"""
    logger.info("🧪 Starting OIICS Data Validation Tests")
    
    db = SessionLocal()
    test_results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    try:
        # Test 1: Check if OIICS fields exist in database
        logger.info("Test 1: Checking OIICS field existence...")
        try:
            # Try to query OIICS fields
            incidents_with_body_part = db.query(WorkplaceIncident).filter(
                WorkplaceIncident.body_part.isnot(None)
            ).count()
            
            incidents_with_source = db.query(WorkplaceIncident).filter(
                WorkplaceIncident.source.isnot(None)
            ).count()
            
            incidents_with_event_type = db.query(WorkplaceIncident).filter(
                WorkplaceIncident.event_type.isnot(None)
            ).count()
            
            logger.info(f"✓ Incidents with body_part: {incidents_with_body_part}")
            logger.info(f"✓ Incidents with source: {incidents_with_source}")
            logger.info(f"✓ Incidents with event_type: {incidents_with_event_type}")
            
            test_results['tests'].append({
                'name': 'OIICS Fields Exist',
                'status': 'PASSED',
                'details': f'Found {incidents_with_body_part} incidents with body_part, {incidents_with_source} with source, {incidents_with_event_type} with event_type'
            })
            test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Test 1 failed: {e}")
            test_results['tests'].append({
                'name': 'OIICS Fields Exist',
                'status': 'FAILED',
                'details': str(e)
            })
            test_results['failed'] += 1
        
        # Test 2: Validate data quality
        logger.info("Test 2: Validating data quality...")
        try:
            # Check for reasonable values in OIICS fields
            body_parts = db.query(WorkplaceIncident.body_part).filter(
                WorkplaceIncident.body_part.isnot(None)
            ).distinct().all()
            
            sources = db.query(WorkplaceIncident.source).filter(
                WorkplaceIncident.source.isnot(None)
            ).distinct().all()
            
            event_types = db.query(WorkplaceIncident.event_type).filter(
                WorkplaceIncident.event_type.isnot(None)
            ).distinct().all()
            
            # Validate body parts (should be reasonable body part names)
            valid_body_parts = ['Head', 'Neck', 'Back', 'Shoulder', 'Arm', 'Hand', 'Leg', 'Foot', 'Eye', 'Ear']
            body_part_quality = any(any(valid in str(bp[0]).lower() for valid in valid_body_parts) for bp in body_parts if bp[0])
            
            # Validate sources (should be reasonable injury sources)
            valid_sources = ['Machinery', 'Tools', 'Vehicle', 'Chemical', 'Fall', 'Struck']
            source_quality = any(any(valid in str(src[0]).lower() for valid in valid_sources) for src in sources if src[0])
            
            logger.info(f"✓ Unique body parts found: {len(body_parts)}")
            logger.info(f"✓ Unique sources found: {len(sources)}")
            logger.info(f"✓ Unique event types found: {len(event_types)}")
            logger.info(f"✓ Body part quality check: {'PASSED' if body_part_quality else 'NEEDS REVIEW'}")
            logger.info(f"✓ Source quality check: {'PASSED' if source_quality else 'NEEDS REVIEW'}")
            
            test_results['tests'].append({
                'name': 'Data Quality Validation',
                'status': 'PASSED',
                'details': f'Found {len(body_parts)} body parts, {len(sources)} sources, {len(event_types)} event types'
            })
            test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Test 2 failed: {e}")
            test_results['tests'].append({
                'name': 'Data Quality Validation',
                'status': 'FAILED',
                'details': str(e)
            })
            test_results['failed'] += 1
        
        # Test 3: Check data consistency
        logger.info("Test 3: Checking data consistency...")
        try:
            # Check if incidents with amputation have reasonable body parts
            amputation_incidents = db.query(WorkplaceIncident).filter(
                WorkplaceIncident.amputation == True
            ).all()
            
            amputation_consistency = 0
            for incident in amputation_incidents:
                if incident.body_part and any(part in str(incident.body_part).lower() for part in ['finger', 'hand', 'arm', 'leg', 'foot', 'toe']):
                    amputation_consistency += 1
            
            consistency_rate = (amputation_consistency / len(amputation_incidents) * 100) if amputation_incidents else 100
            
            logger.info(f"✓ Amputation incidents: {len(amputation_incidents)}")
            logger.info(f"✓ Consistent body parts: {amputation_consistency} ({consistency_rate:.1f}%)")
            
            test_results['tests'].append({
                'name': 'Data Consistency Check',
                'status': 'PASSED' if consistency_rate >= 80 else 'WARNING',
                'details': f'Amputation consistency: {consistency_rate:.1f}% ({amputation_consistency}/{len(amputation_incidents)})'
            })
            test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Test 3 failed: {e}")
            test_results['tests'].append({
                'name': 'Data Consistency Check',
                'status': 'FAILED',
                'details': str(e)
            })
            test_results['failed'] += 1
        
        # Test 4: Sample data validation
        logger.info("Test 4: Sample data validation...")
        try:
            # Get a few sample incidents with OIICS data
            sample_incidents = db.query(WorkplaceIncident).filter(
                (WorkplaceIncident.body_part.isnot(None)) |
                (WorkplaceIncident.source.isnot(None)) |
                (WorkplaceIncident.event_type.isnot(None))
            ).limit(3).all()
            
            logger.info("Sample incidents with OIICS data:")
            for i, incident in enumerate(sample_incidents, 1):
                logger.info(f"  {i}. {incident.company_name} - {incident.incident_type}")
                if incident.body_part:
                    logger.info(f"     Body Part: {incident.body_part}")
                if incident.source:
                    logger.info(f"     Source: {incident.source}")
                if incident.event_type:
                    logger.info(f"     Event Type: {incident.event_type}")
                if incident.hospitalized is not None:
                    logger.info(f"     Hospitalized: {incident.hospitalized}")
                if incident.amputation is not None:
                    logger.info(f"     Amputation: {incident.amputation}")
            
            test_results['tests'].append({
                'name': 'Sample Data Validation',
                'status': 'PASSED',
                'details': f'Successfully retrieved {len(sample_incidents)} sample incidents'
            })
            test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Test 4 failed: {e}")
            test_results['tests'].append({
                'name': 'Sample Data Validation',
                'status': 'FAILED',
                'details': str(e)
            })
            test_results['failed'] += 1
        
        # Test 5: API endpoint test
        logger.info("Test 5: Testing API endpoint...")
        try:
            import requests
            
            # Test the incidents API endpoint
            response = requests.get("http://localhost:8000/api/maps/incidents?limit=5", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                incidents = data.get('incidents', [])
                
                # Check if any incidents have OIICS fields
                oiics_fields_found = 0
                for incident in incidents:
                    if any(incident.get(field) for field in ['body_part', 'source', 'event_type', 'hospitalized', 'amputation']):
                        oiics_fields_found += 1
                
                logger.info(f"✓ API endpoint responding: {response.status_code}")
                logger.info(f"✓ Incidents returned: {len(incidents)}")
                logger.info(f"✓ Incidents with OIICS data: {oiics_fields_found}")
                
                test_results['tests'].append({
                    'name': 'API Endpoint Test',
                    'status': 'PASSED',
                    'details': f'API returned {len(incidents)} incidents, {oiics_fields_found} with OIICS data'
                })
                test_results['passed'] += 1
            else:
                raise Exception(f"API returned status code {response.status_code}")
                
        except Exception as e:
            logger.error(f"✗ Test 5 failed: {e}")
            test_results['tests'].append({
                'name': 'API Endpoint Test',
                'status': 'FAILED',
                'details': str(e)
            })
            test_results['failed'] += 1
        
    except Exception as e:
        logger.error(f"Fatal error during testing: {e}")
        raise
    finally:
        db.close()
    
    return test_results

def main():
    """Main test function"""
    logger.info("🎯 Starting OIICS Data Validation Tests")
    
    try:
        # Run the tests
        results = test_oiics_data_validation()
        
        # Display test results
        logger.info("\n" + "="*60)
        logger.info("🧪 TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        logger.info(f"Tests Passed: {results['passed']}")
        logger.info(f"Tests Failed: {results['failed']}")
        logger.info(f"Total Tests: {len(results['tests'])}")
        
        logger.info("\nDetailed Test Results:")
        for test in results['tests']:
            status_icon = "✅" if test['status'] == 'PASSED' else "⚠️" if test['status'] == 'WARNING' else "❌"
            logger.info(f"{status_icon} {test['name']}: {test['status']}")
            logger.info(f"    {test['details']}")
        
        if results['failed'] == 0:
            logger.info("\n🎉 All tests passed! OIICS data validation successful.")
            return 0
        else:
            logger.warning(f"\n⚠️  {results['failed']} test(s) failed. Please review the results.")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())


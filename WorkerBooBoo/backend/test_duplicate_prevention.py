#!/usr/bin/env python3
"""
Test suite for duplicate prevention functionality
Tests the enhanced CSV importer and coordinate quality tracker
"""

import unittest
import os
import tempfile
import pandas as pd
from datetime import datetime, date
from unittest.mock import patch, MagicMock

# Import the classes to test
from enhanced_csv_importer import EnhancedCSVImporter
from coordinate_quality_tracker import CoordinateQualityTracker
from database import WorkplaceIncident, SessionLocal, Base, engine

class TestDuplicatePrevention(unittest.TestCase):
    """Test duplicate prevention functionality"""
    
    def setUp(self):
        """Set up test database and sample data"""
        # Create in-memory SQLite database for testing
        self.test_db_url = 'sqlite:///:memory:'
        self.engine = engine
        
        # Create tables in the test database
        Base.metadata.create_all(bind=self.engine)
        
        # Create test session
        self.SessionLocal = SessionLocal
        
        # Sample test data
        self.sample_records = [
            {
                'osha_id': 'TEST-001',
                'company_name': 'Test Company A',
                'address': '123 Main St',
                'city': 'Test City',
                'state': 'CA',
                'zip_code': '12345',
                'latitude': 37.7749,
                'longitude': -122.4194,
                'incident_date': '2024-01-15',
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': 'Test incident 1',
                'investigation_status': 'Open',
                'citations_issued': False,
                'penalty_amount': 0.0
            },
            {
                'osha_id': 'TEST-002',
                'company_name': 'Test Company B',
                'address': '456 Oak Ave',
                'city': 'Test City',
                'state': 'CA',
                'zip_code': '12345',
                'latitude': 37.7849,
                'longitude': -122.4294,
                'incident_date': '2024-01-16',
                'incident_type': 'fatality',
                'industry': 'Construction',
                'naics_code': '236000',
                'description': 'Test incident 2',
                'investigation_status': 'Closed',
                'citations_issued': True,
                'penalty_amount': 5000.0
            }
        ]
        
        # Create test CSV file
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df = pd.DataFrame(self.sample_records)
        df.to_csv(self.temp_csv.name, index=False)
        self.temp_csv.close()
        
        # Initialize importer with test database
        self.importer = EnhancedCSVImporter(self.test_db_url)
        
        # Ensure the importer uses the test database
        self.importer.engine = self.engine
        self.importer.SessionLocal = self.SessionLocal
        
    def tearDown(self):
        """Clean up test files and database"""
        # Remove temporary CSV file
        if os.path.exists(self.temp_csv.name):
            os.unlink(self.temp_csv.name)
        
        # Clean up database
        Base.metadata.drop_all(bind=self.engine)
    
    def test_osha_id_duplicate_detection(self):
        """Test that duplicate OSHA IDs are detected"""
        # Import first record
        results1 = self.importer.import_csv_with_duplicate_prevention(
            self.temp_csv.name,
            duplicate_strategy='osha_id'
        )
        
        self.assertEqual(results1['imported'], 2)
        self.assertEqual(results1['duplicates_skipped'], 0)
        
        # Try to import the same data again
        results2 = self.importer.import_csv_with_duplicate_prevention(
            self.temp_csv.name,
            duplicate_strategy='osha_id'
        )
        
        # Should detect duplicates and skip them
        self.assertEqual(results2['imported'], 0)
        self.assertEqual(results2['duplicates_skipped'], 2)
    
    def test_company_location_date_duplicate_detection(self):
        """Test duplicate detection using company + location + date"""
        # Create CSV with same company, location, date but different OSHA ID
        duplicate_data = [
            {
                'osha_id': 'TEST-003',  # Different OSHA ID
                'company_name': 'Test Company A',  # Same company
                'address': '123 Main St',  # Same address
                'city': 'Test City',  # Same city
                'state': 'CA',  # Same state
                'incident_date': '2024-01-15',  # Same date
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': 'Duplicate incident',
                'investigation_status': 'Open',
                'citations_issued': False,
                'penalty_amount': 0.0
            }
        ]
        
        # Create temporary CSV for duplicate data
        temp_dup_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df_dup = pd.DataFrame(duplicate_data)
        df_dup.to_csv(temp_dup_csv.name, index=False)
        temp_dup_csv.close()
        
        try:
            # Import original data
            self.importer.import_csv_with_duplicate_prevention(
                self.temp_csv.name,
                duplicate_strategy='company_location_date'
            )
            
            # Import duplicate data
            results = self.importer.import_csv_with_duplicate_prevention(
                temp_dup_csv.name,
                duplicate_strategy='company_location_date'
            )
            
            # Should detect duplicate based on company + location + date
            self.assertEqual(results['duplicates_skipped'], 1)
            self.assertEqual(results['imported'], 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_dup_csv.name):
                os.unlink(temp_dup_csv.name)
    
    def test_update_existing_records(self):
        """Test updating existing records instead of skipping"""
        # Import original data
        self.importer.import_csv_with_duplicate_prevention(
            self.temp_csv.name,
            duplicate_strategy='osha_id'
        )
        
        # Create updated data (same OSHA ID, different description)
        updated_data = [
            {
                'osha_id': 'TEST-001',
                'company_name': 'Test Company A',
                'address': '123 Main St',
                'city': 'Test City',
                'state': 'CA',
                'zip_code': '12345',
                'latitude': 37.7749,
                'longitude': -122.4194,
                'incident_date': '2024-01-15',
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': 'UPDATED: Test incident 1',  # Changed description
                'investigation_status': 'Open',
                'citations_issued': False,
                'penalty_amount': 0.0
            }
        ]
        
        # Create temporary CSV for updated data
        temp_update_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df_update = pd.DataFrame(updated_data)
        df_update.to_csv(temp_update_csv.name, index=False)
        temp_update_csv.close()
        
        try:
            # Import with update_existing flag
            results = self.importer.import_csv_with_duplicate_prevention(
                temp_update_csv.name,
                duplicate_strategy='osha_id',
                update_existing=True
            )
            
            # Should update existing record
            self.assertEqual(results['updated'], 1)
            self.assertEqual(results['imported'], 0)
            self.assertEqual(results['duplicates_skipped'], 0)
            
            # Verify the update actually happened
            db = self.SessionLocal()
            try:
                updated_record = db.query(WorkplaceIncident).filter(
                    WorkplaceIncident.osha_id == 'TEST-001'
                ).first()
                
                self.assertIsNotNone(updated_record)
                self.assertEqual(updated_record.description, 'UPDATED: Test incident 1')
                
            finally:
                db.close()
                
        finally:
            # Clean up
            if os.path.exists(temp_update_csv.name):
                os.unlink(temp_update_csv.name)
    
    def test_batch_processing(self):
        """Test that batch processing works correctly"""
        # Create larger dataset for batch testing
        large_data = []
        for i in range(2500):  # More than 2 batches of 1000
            large_data.append({
                'osha_id': f'BATCH-{i:04d}',
                'company_name': f'Batch Company {i}',
                'city': 'Batch City',
                'state': 'CA',
                'incident_date': '2024-01-15',
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': f'Batch incident {i}',
                'investigation_status': 'Open',
                'citations_issued': False,
                'penalty_amount': 0.0
            })
        
        # Create temporary CSV for large data
        temp_large_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df_large = pd.DataFrame(large_data)
        df_large.to_csv(temp_large_csv.name, index=False)
        temp_large_csv.close()
        
        try:
            # Import with custom batch size
            results = self.importer.import_csv_with_duplicate_prevention(
                temp_large_csv.name,
                duplicate_strategy='osha_id',
                batch_size=1000
            )
            
            # Should import all records
            self.assertEqual(results['imported'], 2500)
            self.assertEqual(results['errors'], 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_large_csv.name):
                os.unlink(temp_large_csv.name)
    
    def test_error_handling(self):
        """Test error handling during import"""
        # Create CSV with invalid data
        invalid_data = [
            {
                'osha_id': 'INVALID-001',
                'company_name': 'Invalid Company',
                'city': 'Invalid City',
                'state': 'CA',
                'incident_date': 'invalid-date',  # Invalid date
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': 'Invalid incident',
                'investigation_status': 'Open',
                'citations_issued': False,
                'penalty_amount': 0.0
            }
        ]
        
        # Create temporary CSV for invalid data
        temp_invalid_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df_invalid = pd.DataFrame(invalid_data)
        df_invalid.to_csv(temp_invalid_csv.name, index=False)
        temp_invalid_csv.close()
        
        try:
            # Import invalid data
            results = self.importer.import_csv_with_duplicate_prevention(
                temp_invalid_csv.name,
                duplicate_strategy='osha_id'
            )
            
            # Should handle errors gracefully
            self.assertGreaterEqual(results['errors'], 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_invalid_csv.name):
                os.unlink(temp_invalid_csv.name)

class TestCoordinateQualityTracker(unittest.TestCase):
    """Test coordinate quality tracking functionality"""
    
    def setUp(self):
        """Set up test database and sample data"""
        # Create in-memory SQLite database for testing
        self.test_db_url = 'sqlite:///:memory:'
        self.engine = engine
        Base.metadata.create_all(bind=self.engine)
        
        # Create test session
        self.SessionLocal = SessionLocal
        
        # Initialize tracker
        self.tracker = CoordinateQualityTracker()
        
        # Ensure the tracker uses the test database
        self.tracker.db = self.SessionLocal()
        
        # Add test records with different coordinate qualities
        self._add_test_records()
    
    def tearDown(self):
        """Clean up database"""
        Base.metadata.drop_all(bind=self.engine)
    
    def _add_test_records(self):
        """Add test records with various coordinate qualities"""
        db = self.SessionLocal()
        try:
            # Very precise coordinates (6+ decimal places)
            precise_record = WorkplaceIncident(
                osha_id='PRECISE-001',
                company_name='Precise Company',
                city='Precise City',
                state='CA',
                latitude=37.774900,
                longitude=-122.419400,
                incident_date=date(2024, 1, 15),
                incident_type='injury',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(precise_record)
            
            # Approximate coordinates (2-3 decimal places)
            approx_record = WorkplaceIncident(
                osha_id='APPROX-001',
                company_name='Approx Company',
                city='Approx City',
                state='CA',
                latitude=37.77,
                longitude=-122.42,
                incident_date=date(2024, 1, 15),
                incident_type='injury',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(approx_record)
            
            # Rough coordinates (0-1 decimal places) - likely state centers
            rough_record = WorkplaceIncident(
                osha_id='ROUGH-001',
                company_name='Rough Company',
                city='Rough City',
                state='CA',
                latitude=39.0,  # Very round number
                longitude=-105.0,  # Very round number
                incident_date=date(2024, 1, 15),
                incident_type='injury',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(rough_record)
            
            # No coordinates
            no_coords_record = WorkplaceIncident(
                osha_id='NOCOORDS-001',
                company_name='No Coords Company',
                city='No Coords City',
                state='CA',
                latitude=None,
                longitude=None,
                incident_date=date(2024, 1, 15),
                incident_type='injury',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(no_coords_record)
            
            db.commit()
            
        finally:
            db.close()
    
    def test_coordinate_quality_analysis(self):
        """Test coordinate quality analysis"""
        analysis = self.tracker.analyze_coordinate_quality()
        
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis['total_records'], 4)
        
        # Check precision breakdown
        precision = analysis['precision_breakdown']
        self.assertEqual(precision['very_precise'], 1)  # PRECISE-001
        self.assertEqual(precision['approximate'], 1)   # APPROX-001
        self.assertEqual(precision['rough'], 1)         # ROUGH-001
        
        # Check source breakdown
        source = analysis['source_breakdown']
        self.assertEqual(source['likely_geocoded'], 1)  # PRECISE-001
        self.assertEqual(source['likely_fallback'], 1)  # ROUGH-001
    
    def test_records_needing_improvement(self):
        """Test identification of records needing improvement"""
        records = self.tracker.get_records_needing_improvement(limit=10)
        
        # Should find records with low precision or no coordinates
        self.assertGreater(len(records), 0)
        
        # Check that we found the expected records
        osha_ids = [r.osha_id for r in records]
        self.assertIn('ROUGH-001', osha_ids)  # Very round coordinates
        self.assertIn('NOCOORDS-001', osha_ids)  # No coordinates
    
    def test_quality_report_generation(self):
        """Test quality report generation"""
        report = self.tracker.generate_quality_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('COORDINATE QUALITY REPORT', report)
        self.assertIn('Total Records: 4', report)
        self.assertIn('PRECISION BREAKDOWN', report)
        self.assertIn('SOURCE BREAKDOWN', report)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test environment"""
        # Create in-memory SQLite database for testing
        self.test_db_url = 'sqlite:///:memory:'
        self.engine = engine
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize components
        self.importer = EnhancedCSVImporter(self.test_db_url)
        
        # Ensure the importer uses the test database
        self.importer.engine = self.engine
        self.importer.SessionLocal = self.SessionLocal
        
        self.tracker = CoordinateQualityTracker()
        
        # Ensure the tracker uses the test database
        self.tracker.db = self.SessionLocal()
    
    def tearDown(self):
        """Clean up"""
        Base.metadata.drop_all(bind=self.engine)
    
    def test_full_workflow(self):
        """Test complete workflow: import -> analyze -> improve"""
        # Step 1: Import initial data
        sample_data = [
            {
                'osha_id': 'WORKFLOW-001',
                'company_name': 'Workflow Company',
                'city': 'Workflow City',
                'state': 'CA',
                'latitude': 39.0,  # Rough coordinates
                'longitude': -105.0,
                'incident_date': '2024-01-15',
                'incident_type': 'injury',
                'industry': 'Manufacturing',
                'naics_code': '332000',
                'description': 'Workflow test incident',
                'investigation_status': 'Open',
                'citations_issued': False,
                'penalty_amount': 0.0
            }
        ]
        
        # Create temporary CSV
        temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df = pd.DataFrame(sample_data)
        df.to_csv(temp_csv.name, index=False)
        temp_csv.close()
        
        try:
            # Import data
            import_results = self.importer.import_csv_with_duplicate_prevention(
                temp_csv.name,
                duplicate_strategy='osha_id'
            )
            
            self.assertEqual(import_results['imported'], 1)
            
            # Step 2: Analyze coordinate quality
            analysis = self.tracker.analyze_coordinate_quality()
            self.assertEqual(analysis['total_records'], 1)
            
            # Step 3: Check if record needs improvement
            records_needing_improvement = self.tracker.get_records_needing_improvement()
            self.assertEqual(len(records_needing_improvement), 1)
            self.assertEqual(records_needing_improvement[0].osha_id, 'WORKFLOW-001')
            
        finally:
            # Clean up
            if os.path.exists(temp_csv.name):
                os.unlink(temp_csv.name)

def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes using TestLoader
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicatePrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinateQualityTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("🧪 TEST RESULTS SUMMARY:")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

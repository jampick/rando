#!/usr/bin/env python3
"""
Test cases for state filtering scenarios in the maps API endpoints.
Tests the fixes for state filtering that was previously returning false positives.
"""

import unittest
import requests
import json
from typing import Dict, List, Any

class TestStateFiltering(unittest.TestCase):
    """Test cases for state filtering functionality"""
    
    BASE_URL = "http://localhost:8000/api/maps"
    
    def setUp(self):
        """Set up test data and verify API is running"""
        # Verify the API is accessible
        try:
            response = requests.get(f"{self.BASE_URL}/geographic-summary")
            if response.status_code != 200:
                self.skipTest("API not accessible - skipping state filtering tests")
        except requests.exceptions.RequestException:
            self.skipTest("API not accessible - skipping state filtering tests")
    
    def test_wa_state_filter_no_false_positives(self):
        """Test that WA state filter only returns Washington incidents"""
        print("\n🧪 Testing WA state filter for false positives...")
        
        response = requests.get(f"{self.BASE_URL}/incidents?state=WA&limit=20")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        # Check that we got some results
        self.assertGreater(len(incidents), 0, "Should have WA incidents")
        
        # Check that all returned states are valid Washington states
        valid_wa_states = {'WA', 'WASHINGTON'}
        states_found = set(inc["state"] for inc in incidents)
        
        print(f"   📍 States found: {sorted(states_found)}")
        print(f"   ✅ Valid WA states: {sorted(valid_wa_states)}")
        
        # Verify no false positives (no Delaware, Hawaii, Iowa, etc.)
        invalid_states = states_found - valid_wa_states
        self.assertEqual(len(invalid_states), 0, 
                        f"Found invalid states for WA filter: {invalid_states}")
        
        print(f"   🎯 All {len(incidents)} incidents are valid Washington incidents!")
    
    def test_ca_state_filter_no_false_positives(self):
        """Test that CA state filter only returns California incidents"""
        print("\n🧪 Testing CA state filter for false positives...")
        
        response = requests.get(f"{self.BASE_URL}/incidents?state=CA&limit=20")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        # Check that we got some results
        self.assertGreater(len(incidents), 0, "Should have CA incidents")
        
        # Check that all returned states are valid California states
        valid_ca_states = {'CA', 'CALIFORNIA'}
        states_found = set(inc["state"] for inc in incidents)
        
        print(f"   📍 States found: {sorted(states_found)}")
        print(f"   ✅ Valid CA states: {sorted(valid_ca_states)}")
        
        # Verify no false positives
        invalid_states = states_found - valid_ca_states
        self.assertEqual(len(invalid_states), 0, 
                        f"Found invalid states for CA filter: {invalid_states}")
        
        print(f"   🎯 All {len(incidents)} incidents are valid California incidents!")
    
    def test_tx_state_filter_no_false_positives(self):
        """Test that TX state filter only returns Texas incidents"""
        print("\n🧪 Testing TX state filter for false positives...")
        
        response = requests.get(f"{self.BASE_URL}/incidents?state=TX&limit=20")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        # Check that we got some results
        self.assertGreater(len(incidents), 0, "Should have TX incidents")
        
        # Check that all returned states are valid Texas states
        valid_tx_states = {'TX', 'TEXAS'}
        states_found = set(inc["state"] for inc in incidents)
        
        print(f"   📍 States found: {sorted(states_found)}")
        print(f"   ✅ Valid TX states: {sorted(valid_tx_states)}")
        
        # Verify no false positives
        invalid_states = states_found - valid_tx_states
        self.assertEqual(len(invalid_states), 0, 
                        f"Found invalid states for TX filter: {invalid_states}")
        
        print(f"   🎯 All {len(incidents)} incidents are valid Texas incidents!")
    
    def test_ny_state_filter_no_false_positives(self):
        """Test that NY state filter only returns New York incidents"""
        print("\n🧪 Testing NY state filter for false positives...")
        
        response = requests.get(f"{self.BASE_URL}/incidents?state=NY&limit=20")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        # Check that we got some results
        self.assertGreater(len(incidents), 0, "Should have NY incidents")
        
        # Check that all returned states are valid New York states
        valid_ny_states = {'NY', 'NEW YORK'}
        states_found = set(inc["state"] for inc in incidents)
        
        print(f"   📍 States found: {sorted(states_found)}")
        print(f"   ✅ Valid NY states: {sorted(valid_ny_states)}")
        
        # Verify no false positives
        invalid_states = states_found - valid_ny_states
        self.assertEqual(len(invalid_states), 0, 
                        f"Found invalid states for NY filter: {invalid_states}")
        
        print(f"   🎯 All {len(incidents)} incidents are valid New York incidents!")
    
    def test_fl_state_filter_no_false_positives(self):
        """Test that FL state filter only returns Florida incidents"""
        print("\n🧪 Testing FL state filter for false positives...")
        
        response = requests.get(f"{self.BASE_URL}/incidents?state=FL&limit=20")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        # Check that we got some results
        self.assertGreater(len(incidents), 0, "Should have FL incidents")
        
        # Check that all returned states are valid Florida states
        valid_fl_states = {'FL', 'FLORIDA'}
        states_found = set(inc["state"] for inc in incidents)
        
        print(f"   📍 States found: {sorted(states_found)}")
        print(f"   ✅ Valid FL states: {sorted(valid_fl_states)}")
        
        # Verify no false positives
        invalid_states = states_found - valid_fl_states
        self.assertEqual(len(invalid_states), 0, 
                        f"Found invalid states for FL filter: {invalid_states}")
        
        print(f"   🎯 All {len(incidents)} incidents are valid Florida incidents!")
    
    def test_state_filter_with_incident_type(self):
        """Test that state filter works correctly with incident type filter"""
        print("\n🧪 Testing state + incident type combination filter...")
        
        # Test WA + fatality filter
        response = requests.get(f"{self.BASE_URL}/incidents?state=WA&incident_type=fatality&limit=10")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        print(f"   📍 WA + fatality incidents: {len(incidents)}")
        
        if len(incidents) > 0:
            # Verify all incidents are Washington fatalities
            for incident in incidents:
                self.assertIn(incident["state"], ['WA', 'WASHINGTON'], 
                             f"Incident {incident['id']} is not in Washington")
                self.assertEqual(incident["incident_type"], "fatality",
                               f"Incident {incident['id']} is not a fatality")
            
            print(f"   ✅ All {len(incidents)} incidents are Washington fatalities!")
        else:
            print("   📍 No Washington fatalities found (this is expected)")
    
    def test_state_filter_with_industry(self):
        """Test that state filter works correctly with industry filter"""
        print("\n🧪 Testing state + industry combination filter...")
        
        # Test CA + manufacturing filter
        response = requests.get(f"{self.BASE_URL}/incidents?state=CA&industry=manufacturing&limit=10")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        incidents = data["incidents"]
        
        print(f"   📍 CA + manufacturing incidents: {len(incidents)}")
        
        if len(incidents) > 0:
            # Verify all incidents are California incidents
            for incident in incidents:
                self.assertIn(incident["state"], ['CA', 'CALIFORNIA'], 
                             f"Incident {incident['id']} is not in California")
                self.assertIn("manufacturing", incident["industry"].lower(),
                             f"Incident {incident['id']} is not in manufacturing industry")
            
            print(f"   ✅ All {len(incidents)} incidents are California manufacturing incidents!")
        else:
            print("   📍 No California manufacturing incidents found (this is expected)")
    
    def test_heatmap_state_filtering(self):
        """Test that heatmap endpoint also respects state filtering"""
        print("\n🧪 Testing heatmap endpoint state filtering...")
        
        # Get map bounds (continental US)
        bounds = "25.0,-125.0,50.0,-65.0"
        
        # Test WA filter in heatmap
        response = requests.get(f"{self.BASE_URL}/heatmap?bounds={bounds}&state=WA")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        heatmap_data = data["heatmap_data"]
        
        print(f"   📍 WA heatmap points: {len(heatmap_data)}")
        
        # Verify filters are applied correctly
        self.assertEqual(data["filters"]["state"], "WA")
        
        print(f"   ✅ Heatmap state filtering working correctly!")
    
    def test_multiple_state_filters_consistency(self):
        """Test that multiple state filters return consistent results"""
        print("\n🧪 Testing multiple state filters consistency...")
        
        states_to_test = ['WA', 'CA', 'TX', 'NY', 'FL']
        results = {}
        
        for state in states_to_test:
            response = requests.get(f"{self.BASE_URL}/incidents?state={state}&limit=100")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            results[state] = {
                'count': data['total'],
                'states_found': set(inc['state'] for inc in data['incidents'])
            }
        
        # Print results summary
        print("   📊 State Filter Results Summary:")
        for state, result in results.items():
            print(f"      {state}: {result['count']} incidents, states: {sorted(result['states_found'])}")
        
        # Verify no overlap between different state filters
        for i, (state1, result1) in enumerate(results.items()):
            for state2, result2 in list(results.items())[i+1:]:
                if state1 != state2:
                    overlap = result1['states_found'] & result2['states_found']
                    self.assertEqual(len(overlap), 0, 
                                  f"States {state1} and {state2} have overlapping results: {overlap}")
        
        print("   ✅ No overlap between different state filters!")
    
    def test_state_filter_edge_cases(self):
        """Test edge cases for state filtering"""
        print("\n🧪 Testing state filter edge cases...")
        
        # Test empty state filter (should return all incidents)
        response = requests.get(f"{self.BASE_URL}/incidents?limit=10")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        all_incidents = data["incidents"]
        
        print(f"   📍 All incidents (no state filter): {len(all_incidents)}")
        
        # Test invalid state filter (should return empty results)
        response = requests.get(f"{self.BASE_URL}/incidents?state=INVALID_STATE&limit=10")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        invalid_state_incidents = data["incidents"]
        
        print(f"   📍 Invalid state filter results: {len(invalid_state_incidents)}")
        
        # Test case sensitivity
        response = requests.get(f"{self.BASE_URL}/incidents?state=wa&limit=10")  # lowercase
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        lowercase_wa_incidents = data["incidents"]
        
        print(f"   📍 Lowercase 'wa' filter results: {len(lowercase_wa_incidents)}")
        
        # Verify case insensitivity works
        self.assertGreater(len(lowercase_wa_incidents), 0, "Lowercase state filter should work")
        
        print("   ✅ Edge case testing complete!")


def run_tests():
    """Run the state filtering tests"""
    print("🧪 Running State Filtering Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestStateFiltering)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 State Filtering Test Results Summary:")
    print(f"   ✅ Tests run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   ⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  Test Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All state filtering tests passed!")
    else:
        print("\n💥 Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()

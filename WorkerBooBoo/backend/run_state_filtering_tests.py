#!/usr/bin/env python3
"""
Simple runner script for state filtering tests.
Run this to test the state filtering functionality.
"""

from test_state_filtering import run_tests

if __name__ == "__main__":
    print("🚀 Starting State Filtering Tests...")
    success = run_tests()
    
    if success:
        print("\n🎉 All tests passed! State filtering is working correctly.")
        exit(0)
    else:
        print("\n💥 Some tests failed! Check the output above for details.")
        exit(1)

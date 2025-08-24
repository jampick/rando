#!/usr/bin/env python3
"""
Simple test runner for duplicate prevention tests
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run duplicate prevention tests"""
    print("🧪 Running Duplicate Prevention Tests")
    print("=" * 50)
    
    try:
        # Import and run tests
        from test_duplicate_prevention import run_tests
        
        success = run_tests()
        
        if success:
            print("\n✅ All duplicate prevention tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Test runner script for WorkerBooBoo backend
Provides easy access to different test configurations
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest pytest-asyncio pytest-cov")
        return False

def main():
    """Main test runner function"""
    print("🧪 WorkerBooBoo Backend Test Runner")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage: python run_tests.py [option]")
        print("\nOptions:")
        print("  all          - Run all tests with coverage")
        print("  unit         - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  maps         - Run map-related tests only")
        print("  stats        - Run statistics tests only")
        print("  incidents    - Run incident tests only")
        print("  coverage     - Run tests with HTML coverage report")
        print("  quick        - Run tests without coverage (faster)")
        print("  help         - Show this help message")
        return
    
    option = sys.argv[1].lower()
    
    if option == "help":
        print("\nUsage: python run_tests.py [option]")
        print("\nOptions:")
        print("  all          - Run all tests with coverage")
        print("  unit         - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  maps         - Run map-related tests only")
        print("  stats        - Run statistics tests only")
        print("  incidents    - Run incident tests only")
        print("  coverage     - Run tests with HTML coverage report")
        print("  quick        - Run tests without coverage (faster)")
        return
    
    # Ensure we're in the backend directory
    if not os.path.exists("tests"):
        print("❌ Tests directory not found. Make sure you're in the backend directory.")
        return
    
    success = True
    
    if option == "all":
        success = run_command(
            ["pytest", "tests/", "-v", "--cov=.", "--cov-report=term-missing"],
            "All tests with coverage"
        )
    
    elif option == "unit":
        success = run_command(
            ["pytest", "tests/", "-v", "-m", "unit"],
            "Unit tests only"
        )
    
    elif option == "integration":
        success = run_command(
            ["pytest", "tests/", "-v", "-m", "integration"],
            "Integration tests only"
        )
    
    elif option == "maps":
        success = run_command(
            ["pytest", "tests/routers/test_maps.py", "-v"],
            "Map-related tests only"
        )
    
    elif option == "stats":
        success = run_command(
            ["pytest", "tests/routers/test_statistics.py", "-v"],
            "Statistics tests only"
        )
    
    elif option == "incidents":
        success = run_command(
            ["pytest", "tests/routers/test_incidents.py", "-v"],
            "Incident tests only"
        )
    
    elif option == "coverage":
        success = run_command(
            ["pytest", "tests/", "-v", "--cov=.", "--cov-report=html", "--cov-report=term-missing"],
            "Tests with HTML coverage report"
        )
        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    
    elif option == "quick":
        success = run_command(
            ["pytest", "tests/", "-v"],
            "Quick tests without coverage"
        )
    
    else:
        print(f"❌ Unknown option: {option}")
        print("Use 'python run_tests.py help' for available options")
        return
    
    if success:
        print(f"\n🎉 All {option} tests completed successfully!")
    else:
        print(f"\n💥 Some {option} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Grim Observer Test Runner
Single wrapper to run all tests with clear pass/fail outcomes
"""

import sys
import os
import subprocess
import time
import tempfile
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def run_test(self, test_name, test_func, *args, **kwargs):
        """Run a single test and record results"""
        self.total_tests += 1
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if result:
                self.passed_tests += 1
                print(f"✅ PASS: {test_name} ({duration:.2f}s)")
                self.results.append((test_name, "PASS", duration))
            else:
                print(f"❌ FAIL: {test_name} ({duration:.2f}s)")
                self.results.append((test_name, "FAIL", duration))
                
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.results.append((test_name, "ERROR", 0))
            
        return result
    
    def test_parser(self):
        """Test the log parser functionality"""
        try:
            # Test basic parser import
            from grim_observer import ConanLogParser, LogEvent
            
            parser = ConanLogParser()
            
            # Test player connection parsing
            test_line = "[2025.08.09-22.00.00:000][1]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 TestPlayer (192.168.1.100:12345) connected"
            event = parser.parse_line(test_line)
            
            if event and event.event_type == 'player_connected' and event.player_name == 'TestPlayer':
                return True
            else:
                print(f"   Parser failed: Expected player_connected, got {event.event_type if event else 'None'}")
                return False
                
        except Exception as e:
            print(f"   Parser test error: {e}")
            return False
    
    def test_scan_monitor(self):
        """Test scan-monitor functionality"""
        try:
            # Create a temporary test log
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as f:
                f.write("[2025.08.09-22.00.00:000][1]LogServerStats: Status report. Uptime=0 Mem=1000000000:2000000000:500000000:800000000 CPU=0.0:0.0 Players=0 FPS=30.0:30.0:300.0\n")
                f.write("[2025.08.09-22.00.01:000][2]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 TestPlayer (192.168.1.100:12345) connected\n")
                f.write("[2025.08.09-22.00.02:000][3]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 TestPlayer disconnected\n")
                temp_log = f.name
            
            # Test scan mode
            cmd = [sys.executable, 'grim_observer.py', 'scan', temp_log, '--verbose']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Clean up
            os.unlink(temp_log)
            
            if result.returncode == 0 and "TestPlayer" in result.stdout:
                return True
            else:
                print(f"   Scan test failed: return code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   Scan test error: {e}")
            return False
    
    def test_empty_message(self):
        """Test empty server message generation"""
        try:
            from grim_observer import GrimObserver
            
            observer = GrimObserver("/tmp/test.log", map_name="test")
            payload = observer._generate_empty_server_message()
            
            if payload and 'embeds' in payload and len(payload['embeds']) > 0:
                return True
            else:
                print(f"   Empty message test failed: Invalid payload structure")
                return False
                
        except Exception as e:
            print(f"   Empty message test error: {e}")
            return False
    
    def test_config_loading(self):
        """Test configuration and secrets loading"""
        try:
            from grim_observer import load_secrets
            
            # Test loading secrets (should not crash even if files don't exist)
            secrets = load_secrets('exiled')
            secrets = load_secrets('siptah')
            
            return True
            
        except Exception as e:
            print(f"   Config test error: {e}")
            return False
    
    def print_summary(self):
        """Print final test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, status, duration in self.results:
            icon = "✅" if status == "PASS" else "❌"
            print(f"{icon} {test_name:<25} {status:<6} {duration:>6.2f}s")
        
        print("-" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n💥 {self.total_tests - self.passed_tests} TEST(S) FAILED!")
            return 1

def main():
    """Main test runner"""
    print("🚀 Grim Observer Test Suite")
    print("=" * 40)
    
    runner = TestRunner()
    
    # Run all tests
    runner.run_test("Log Parser", runner.test_parser)
    runner.run_test("Scan Monitor", runner.test_scan_monitor)
    runner.run_test("Empty Message", runner.test_empty_message)
    runner.run_test("Config Loading", runner.test_config_loading)
    
    # Print summary and exit with appropriate code
    exit_code = runner.print_summary()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

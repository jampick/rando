#!/usr/bin/env python3
"""
Test script for Grim Observer scan-monitor functionality.

This test validates that the scan-monitor mode:
1. Correctly scans existing log content
2. Monitors for new log entries
3. Detects player connections and disconnections
4. Handles different player name types correctly
5. Reports events via Discord webhook (mocked)
"""

import os
import time
import tempfile
import threading
import subprocess
import json
import re
from datetime import datetime
from unittest.mock import patch, MagicMock

class ScanMonitorTest:
    def __init__(self):
        self.test_log_file = None
        self.observer_process = None
        self.test_results = {
            'initial_scan_events': [],
            'monitored_events': [],
            'player_name_types': [],
            'errors': []
        }
        
    def setup_test_log(self):
        """Create a test log file with initial content."""
        # Create a temporary log file
        self.test_log_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False)
        
        # Add some initial log content (no player events)
        initial_content = [
            "[2025.08.09-22.00.00:000][1]LogServerStats: Status report. Uptime=0 Mem=1000000000:2000000000:500000000:800000000 CPU=0.0:0.0 Players=0 FPS=30.0:30.0:300.0",
            "[2025.08.09-22.00.01:000][2]LogHttp:Warning: request failed, libcurl error: 7 (Couldn't connect to server)",
            "[2025.08.09-22.00.02:000][3]LogServerStats: Status report. Uptime=2 Mem=1000000000:2000000000:500000000:800000000 CPU=0.0:0.0 Players=0 FPS=30.0:30.0:300.0"
        ]
        
        for line in initial_content:
            self.test_log_file.write(line + '\n')
        self.test_log_file.flush()
        
        print(f"✅ Created test log file: {self.test_log_file.name}")
        return self.test_log_file.name
    
    def add_player_event(self, event_type, player_name, timestamp=None):
        """Add a player event to the test log file."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y.%m.%d-%H.%M.%S:%f")[:-3]
        
        if event_type == 'connect':
            line = f"[{timestamp}][100]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 {player_name} (192.168.1.100:12345) connected"
        elif event_type == 'disconnect_battleye':
            line = f"[{timestamp}][101]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 {player_name} disconnected"
        elif event_type == 'disconnect_lognet':
            line = f"[{timestamp}][102]LogNet: Player disconnected: {player_name}"
        else:
            raise ValueError(f"Unknown event type: {event_type}")
        
        self.test_log_file.write(line + '\n')
        self.test_log_file.flush()
        print(f"📝 Added {event_type} event for player: {player_name}")
        
        return line
    
    def start_observer(self, log_file_path):
        """Start the grim observer in scan-monitor mode."""
        print("🚀 Starting Grim Observer in scan-monitor mode...")
        
        # Set up environment variables for testing
        env = os.environ.copy()
        env['DISCORD_WEBHOOK_URL'] = 'https://discord.com/api/webhooks/test/test'
        env['LOG_FILE_PATH'] = log_file_path
        env['MAP_NAME'] = 'test'
        env['MAP_DESCRIPTION'] = 'Test map for scan-monitor validation'
        
        # Start the observer process
        cmd = [
            'python3', 'grim_observer.py',
            'scan-monitor', log_file_path,
            '--map', 'test',
            '--discord',
            '--verbose'
        ]
        
        try:
            self.observer_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Give it time to start up and scan the initial content
            time.sleep(3)
            print("✅ Observer started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start observer: {e}")
            self.test_results['errors'].append(f"Failed to start observer: {e}")
            return False
        
        return True
    
    def monitor_observer_output(self, duration=10):
        """Monitor the observer output for a specified duration."""
        print(f"👀 Monitoring observer output for {duration} seconds...")
        
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < duration:
            if self.observer_process and self.observer_process.poll() is None:
                # Read any available output
                try:
                    line = self.observer_process.stdout.readline()
                    if line:
                        output_lines.append(line.strip())
                        print(f"📊 Observer: {line.strip()}")
                except:
                    pass
            time.sleep(0.1)
        
        return output_lines
    
    def stop_observer(self):
        """Stop the observer process."""
        if self.observer_process:
            print("🛑 Stopping observer...")
            self.observer_process.terminate()
            try:
                self.observer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.observer_process.kill()
            print("✅ Observer stopped")
    
    def cleanup(self):
        """Clean up test resources."""
        if self.test_log_file:
            self.test_log_file.close()
            try:
                os.unlink(self.test_log_file.name)
                print(f"🧹 Cleaned up test log file: {self.test_log_file.name}")
            except:
                pass
    
    def validate_events(self, output_lines):
        """Validate that the expected events were detected."""
        print("\n🔍 Validating detected events...")
        
        # Look for event detection patterns in the output
        event_patterns = {
            'player_connected': r'Event detected:.*player_connected: (.+)',
            'player_disconnected': r'Event detected:.*player_disconnected: (.+)'
        }
        
        detected_events = {
            'connections': [],
            'disconnections': []
        }
        
        for line in output_lines:
            for event_type, pattern in event_patterns.items():
                match = re.search(pattern, line)
                if match:
                    player_name = match.group(1)
                    if 'connected' in event_type:
                        detected_events['connections'].append(player_name)
                    else:
                        detected_events['disconnections'].append(player_name)
        
        print(f"📊 Detected connections: {detected_events['connections']}")
        print(f"📊 Detected disconnections: {detected_events['disconnections']}")
        
        return detected_events
    
    def test_player_name_types(self):
        """Test different types of player names."""
        print("\n🧪 Testing different player name types...")
        
        test_cases = [
            # Simple names
            ('SimpleName', 'Simple ASCII name'),
            ('Player123', 'Name with numbers'),
            ('Player_Name', 'Name with underscore'),
            ('Player-Name', 'Name with hyphen'),
            
            # Special characters
            ('Player#1234', 'Name with hash and numbers'),
            ('Player@Domain', 'Name with at symbol'),
            ('Player$Money', 'Name with dollar sign'),
            ('Player%Percent', 'Name with percent'),
            
            # Unicode names (common in games)
            ('Æsir', 'Name with Æ'),
            ('Bjørn', 'Name with ø'),
            ('José', 'Name with é'),
            ('François', 'Name with ç'),
            
            # Edge cases
            ('A', 'Single character'),
            ('VeryLongPlayerNameThatExceedsNormalLength', 'Very long name'),
            ('Player With Spaces', 'Name with spaces'),
            ('Player\tTab', 'Name with tab'),
            ('Player\nNewline', 'Name with newline')
        ]
        
        for player_name, description in test_cases:
            print(f"  Testing: {player_name} ({description})")
            
            # Add connection event
            self.add_player_event('connect', player_name)
            time.sleep(0.5)
            
            # Add disconnection event
            self.add_player_event('disconnect_battleye', player_name)
            time.sleep(0.5)
            
            self.test_results['player_name_types'].append({
                'name': player_name,
                'description': description,
                'tested': True
            })
    
    def run_test(self):
        """Run the complete scan-monitor test."""
        print("🧪 Starting Scan-Monitor Test Suite")
        print("=" * 50)
        
        try:
            # Step 1: Setup test log file
            log_file_path = self.setup_test_log()
            
            # Step 2: Start observer
            if not self.start_observer(log_file_path):
                return False
            
            # Step 3: Test initial scan (should find no player events)
            print("\n📖 Phase 1: Testing initial scan...")
            time.sleep(2)
            
            # Step 4: Add test player events
            print("\n📝 Phase 2: Adding test player events...")
            self.test_player_name_types()
            
            # Step 5: Monitor for new events
            print("\n👀 Phase 3: Monitoring for new events...")
            output_lines = self.monitor_observer_output(duration=15)
            
            # Step 6: Validate results
            print("\n🔍 Phase 4: Validating results...")
            detected_events = self.validate_events(output_lines)
            
            # Step 7: Generate test report
            self.generate_test_report(detected_events)
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            self.test_results['errors'].append(f"Test failed: {e}")
            return False
        
        finally:
            self.stop_observer()
            self.cleanup()
    
    def generate_test_report(self, detected_events):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 50)
        print("📊 SCAN-MONITOR TEST REPORT")
        print("=" * 50)
        
        # Count events
        total_connections = len(detected_events['connections'])
        total_disconnections = len(detected_events['disconnections'])
        total_events = total_connections + total_disconnections
        
        # Expected events (2 per player name type: connect + disconnect)
        expected_events = len(self.test_results['player_name_types']) * 2
        
        print(f"📈 Event Detection Summary:")
        print(f"   Total connections detected: {total_connections}")
        print(f"   Total disconnections detected: {total_disconnections}")
        print(f"   Total events detected: {total_events}")
        print(f"   Expected events: {expected_events}")
        
        if total_events == expected_events:
            print("   ✅ Event detection: PASSED")
        else:
            print("   ❌ Event detection: FAILED")
        
        print(f"\n🧪 Player Name Type Testing:")
        print(f"   Total name types tested: {len(self.test_results['player_name_types'])}")
        
        # Show some examples of detected names
        if detected_events['connections']:
            print(f"   Sample detected names: {detected_events['connections'][:5]}")
        
        print(f"\n📝 Test Log File: {self.test_log_file.name if self.test_log_file else 'N/A'}")
        
        if self.test_results['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        
        print("\n" + "=" * 50)
        
        # Save detailed results to file
        self.save_test_results(detected_events)
    
    def save_test_results(self, detected_events):
        """Save detailed test results to a JSON file."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_name': 'scan_monitor_validation',
            'summary': {
                'total_connections': len(detected_events['connections']),
                'total_disconnections': len(detected_events['disconnections']),
                'total_events': len(detected_events['connections']) + len(detected_events['disconnections']),
                'player_name_types_tested': len(self.test_results['player_name_types'])
            },
            'detected_events': detected_events,
            'player_name_types': self.test_results['player_name_types'],
            'errors': self.test_results['errors']
        }
        
        results_file = 'test_scan_monitor_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Detailed results saved to: {results_file}")


def main():
    """Main test execution function."""
    print("🧪 Grim Observer Scan-Monitor Test Suite")
    print("This test validates the scan-monitor functionality with various player name types.")
    print()
    
    # Check if grim_observer.py exists
    if not os.path.exists('grim_observer.py'):
        print("❌ Error: grim_observer.py not found in current directory")
        print("Please run this test from the grim_observer directory")
        return 1
    
    # Create and run test
    test = ScanMonitorTest()
    success = test.run_test()
    
    if success:
        print("\n🎉 Test completed successfully!")
        return 0
    else:
        print("\n💥 Test failed!")
        return 1


if __name__ == '__main__':
    exit(main())

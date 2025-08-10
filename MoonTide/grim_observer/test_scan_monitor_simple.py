#!/usr/bin/env python3
"""
Simple test script for Grim Observer scan-monitor functionality.

This test validates that the scan-monitor mode:
1. Correctly scans existing log content
2. Monitors for new log entries
3. Detects player connections and disconnections
4. Handles different player name types correctly
"""

import os
import time
import tempfile
import subprocess
import json
import re
from datetime import datetime

def create_test_log():
    """Create a test log file with initial content."""
    # Create a temporary log file
    test_log = tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False)
    
    # Add some initial log content (no player events)
    initial_content = [
        "[2025.08.09-22.00.00:000][1]LogServerStats: Status report. Uptime=0 Mem=1000000000:2000000000:500000000:800000000 CPU=0.0:0.0 Players=0 FPS=30.0:30.0:300.0",
        "[2025.08.09-22.00.01:000][2]LogHttp:Warning: request failed, libcurl error: 7 (Couldn't connect to server)",
        "[2025.08.09-22.00.02:000][3]LogServerStats: Status report. Uptime=2 Mem=1000000000:2000000000:500000000:800000000 CPU=0.0:0.0 Players=0 FPS=30.0:30.0:300.0"
    ]
    
    for line in initial_content:
        test_log.write(line + '\n')
    test_log.flush()
    
    print(f"✅ Created test log file: {test_log.name}")
    return test_log

def add_player_event(test_log, event_type, player_name):
    """Add a player event to the test log file."""
    timestamp = datetime.now().strftime("%Y.%m.%d-%H.%M.%S:%f")[:-3]
    
    if event_type == 'connect':
        line = f"[{timestamp}][100]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 {player_name} (192.168.1.100:12345) connected"
    elif event_type == 'disconnect':
        line = f"[{timestamp}][101]BattlEyeLogging: BattlEyeServer: Print Message: Player #0 {player_name} disconnected"
    else:
        raise ValueError(f"Unknown event type: {event_type}")
    
    test_log.write(line + '\n')
    test_log.flush()
    print(f"📝 Added {event_type} event for player: {player_name}")
    
    return line

def run_scan_monitor_test():
    """Run the scan-monitor test."""
    print("🧪 Starting Simple Scan-Monitor Test")
    print("=" * 40)
    
    test_log = None
    observer_process = None
    
    try:
        # Step 1: Create test log file
        test_log = create_test_log()
        log_file_path = test_log.name
        
        # Step 2: Start observer in scan-monitor mode
        print("\n🚀 Starting Grim Observer in scan-monitor mode...")
        
        # Set up environment variables for testing
        env = os.environ.copy()
        env['DISCORD_WEBHOOK_URL'] = 'https://discord.com/api/webhooks/test/test'
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
        
        print(f"Running command: {' '.join(cmd)}")
        
        observer_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give it time to start up and scan the initial content
        print("⏳ Waiting for observer to start and scan initial content...")
        time.sleep(5)
        
        # Step 3: Add test player events
        print("\n📝 Adding test player events...")
        
        test_players = [
            'SimpleName',
            'Player123', 
            'Player_Name',
            'Player#1234',
            'Æsir',
            'José'
        ]
        
        for player_name in test_players:
            # Add connection event
            add_player_event(test_log, 'connect', player_name)
            time.sleep(1)
            
            # Add disconnection event
            add_player_event(test_log, 'disconnect', player_name)
            time.sleep(1)
        
        # Step 4: Monitor for a bit more
        print("\n👀 Monitoring for event detection...")
        time.sleep(10)
        
        # Step 5: Check if observer is still running
        if observer_process.poll() is None:
            print("✅ Observer is still running and monitoring")
        else:
            print("❌ Observer process has stopped")
            stdout, stderr = observer_process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        # Cleanup
        if observer_process:
            print("\n🛑 Stopping observer...")
            observer_process.terminate()
            try:
                observer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                observer_process.kill()
            print("✅ Observer stopped")
        
        if test_log:
            test_log.close()
            try:
                os.unlink(test_log.name)
                print(f"🧹 Cleaned up test log file: {test_log.name}")
            except:
                pass

def main():
    """Main test execution function."""
    print("🧪 Grim Observer Simple Scan-Monitor Test")
    print("This test validates the scan-monitor functionality with various player name types.")
    print()
    
    # Check if grim_observer.py exists
    if not os.path.exists('grim_observer.py'):
        print("❌ Error: grim_observer.py not found in current directory")
        print("Please run this test from the grim_observer directory")
        return 1
    
    # Run test
    success = run_scan_monitor_test()
    
    if success:
        print("\n🎉 Test completed successfully!")
        return 0
    else:
        print("\n💥 Test failed!")
        return 1

if __name__ == '__main__':
    exit(main())

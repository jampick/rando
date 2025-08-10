#!/usr/bin/env python3
"""
Test script for Grim Observer log parser.
Tests the parser against the sample log file to ensure it correctly identifies events.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import grim_observer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grim_observer import ConanLogParser, LogEvent


def test_parser():
    """Test the log parser with the sample log file."""
    sample_log_path = Path(__file__).parent / "tests" / "conansandbox.sample.log"
    
    if not sample_log_path.exists():
        print(f"Sample log file not found: {sample_log_path}")
        return
    
    parser = ConanLogParser()
    events = []
    
    print("Testing Grim Observer log parser...")
    print(f"Reading sample log: {sample_log_path}")
    print("-" * 60)
    
    try:
        with open(sample_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                event = parser.parse_line(line)
                if event:
                    events.append(event)
                    print(f"Line {line_num}: {event}")
        
        print("-" * 60)
        print(f"Total events found: {len(events)}")
        
        # Analyze events
        event_types = {}
        players = set()
        
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            if event.player_name:
                players.add(event.player_name)
        
        print(f"Event types: {event_types}")
        print(f"Unique players: {sorted(players)}")
        
        # Test specific patterns
        print("\nTesting specific patterns:")
        
        # Test player connection pattern
        test_conn = "BattlEyeServer: Print Message: Player #0 Zula (199.36.253.123:62866) connected"
        conn_event = parser.parse_line(f"[2025.08.09-22.09.34:373][583]BattlEyeLogging: {test_conn}")
        if conn_event:
            print(f"✓ Player connection pattern: {conn_event}")
        else:
            print("✗ Player connection pattern failed")
        
        # Test player disconnection pattern (BattlEye)
        test_disc_be = "BattlEyeServer: Print Message: Player #0 Zula disconnected"
        disc_be_event = parser.parse_line(f"[2025.08.09-22.09.35:575][589]BattlEyeLogging: {test_disc_be}")
        if disc_be_event:
            print(f"✓ Player disconnection (BattlEye) pattern: {disc_be_event}")
        else:
            print("✗ Player disconnection (BattlEye) pattern failed")
        
        # Test player disconnection pattern (LogNet)
        test_disc_ln = "LogNet: Player disconnected: Sweetbread#26947"
        disc_ln_event = parser.parse_line(f"[2025.08.09-22.19.25:898][187]{test_disc_ln}")
        if disc_ln_event:
            print(f"✓ Player disconnection (LogNet) pattern: {disc_ln_event}")
        else:
            print("✗ Player disconnection (LogNet) pattern failed")
        
        print("\nParser test completed successfully!")
        
    except Exception as e:
        print(f"Error testing parser: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_parser()

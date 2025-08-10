#!/usr/bin/env python3
"""
Demonstration script for Grim Observer.
Shows how the observer would work in real-time monitoring mode.
"""

import sys
import os
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grim_observer import GrimObserver


def demo_observer():
    """Demonstrate the observer functionality."""
    sample_log_path = Path(__file__).parent / "tests" / "conansandbox.sample.log"
    
    if not sample_log_path.exists():
        print(f"Sample log file not found: {sample_log_path}")
        return
    
    print("Grim Observer Demo")
    print("=" * 50)
    print(f"Monitoring: {sample_log_path}")
    print("This demo will process the existing log file and show detected events.")
    print()
    
    # Create a temporary output file for the demo
    output_file = Path(__file__).parent / "demo_events.json"
    
    try:
        # Create observer instance
        observer = GrimObserver(
            log_file_path=str(sample_log_path),
            output_file=str(output_file),
            verbose=True
        )
        
        print("Starting log processing...")
        print("-" * 50)
        
        # Process the entire file (simulating real-time monitoring)
        with open(sample_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                observer.process_line(line)
                
                # Show progress every 500 lines
                if line_num % 500 == 0:
                    print(f"Processed {line_num} lines...")
        
        print("-" * 50)
        print("Log processing completed!")
        print()
        
        # Show results
        print("Results:")
        print(f"Total events detected: {len(observer.events)}")
        
        if observer.events:
            print("\nEvent Summary:")
            event_types = {}
            players = set()
            
            for event in observer.events:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
                if event.player_name:
                    players.add(event.player_name)
            
            for event_type, count in event_types.items():
                print(f"  {event_type}: {count}")
            
            print(f"\nPlayers involved: {', '.join(sorted(players))}")
            
            # Show current player count
            current_count = observer.get_player_count()
            print(f"\nCurrent player count: {current_count}")
            
            # Show recent events (last 10 minutes)
            recent = observer.get_recent_events(minutes=10)
            if recent:
                print(f"\nRecent events (last 10 minutes): {len(recent)}")
                for event in recent[-3:]:  # Show last 3 events
                    print(f"  {event}")
        
        # Show output file info
        if output_file.exists():
            print(f"\nEvents saved to: {output_file}")
            print(f"File size: {output_file.stat().st_size} bytes")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up demo output file
        if output_file.exists():
            try:
                output_file.unlink()
                print("Demo output file cleaned up.")
            except:
                pass


if __name__ == '__main__':
    demo_observer()

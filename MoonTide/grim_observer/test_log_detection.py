#!/usr/bin/env python3
"""
Test script for Grim Observer log file auto-detection
"""

import os
import sys
import time
from pathlib import Path

# Add the grim_observer directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grim_observer import GrimObserver

def test_log_detection():
    """Test the log file auto-detection functionality."""
    print("=== Grim Observer Log File Auto-Detection Test ===")
    
    # Test with a directory that might contain log files
    test_directories = [
        "~/Library/Application Support/Steam/steamapps/common/Conan Exiles/ConanSandbox/Saved/Logs",
        "~/Library/Application Support/Epic/ConanSandbox/Saved/Logs",
        "./",  # Current directory
        "../"  # Parent directory
    ]
    
    for test_dir in test_directories:
        expanded_dir = os.path.expanduser(test_dir)
        print(f"\nTesting directory: {expanded_dir}")
        
        if not os.path.exists(expanded_dir):
            print(f"  Directory does not exist: {expanded_dir}")
            continue
        
        # Create a temporary observer
        observer = GrimObserver(
            log_file_path=expanded_dir,
            discord_webhook_url="",
            output_file="test_output.json"
        )
        
        # Try to detect log files
        detected_file = observer.detect_active_log_file(expanded_dir)
        print(f"  Detected file: {detected_file}")
        
        # List all files in the directory
        try:
            files = list(Path(expanded_dir).glob("*.log"))
            if files:
                print(f"  Found {len(files)} log files:")
                for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
                    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f.stat().st_mtime))
                    size = f.stat().st_size
                    print(f"    - {f.name} (modified: {mtime}, size: {size} bytes)")
            else:
                print(f"  No .log files found")
        except Exception as e:
            print(f"  Error listing files: {e}")

if __name__ == "__main__":
    test_log_detection()

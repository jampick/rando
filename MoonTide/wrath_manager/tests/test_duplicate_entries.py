#!/usr/bin/env python3
"""
Test case for duplicate entries bug fix.

This test verifies that wrath_manager properly handles and removes duplicate
settings in the ServerSettings.ini file, ensuring only one occurrence of
each setting key exists after updates.
"""

import sys
import os
import re
import tempfile
import shutil
from typing import Dict, List, Tuple

# Add parent directory to path to import wrath_manager functions
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import functions directly from wrath_manager module
try:
    from wrath_manager import (
        find_section_ranges,
        upsert_key_in_section,
        read_text_lines_with_meta,
        remove_duplicate_settings,
        main as wrath_main,
    )
except ImportError as e:
    print(f"ERROR: Failed to import wrath_manager functions: {e}", file=sys.stderr)
    print(f"Make sure you're running this from the tests/ directory", file=sys.stderr)
    print(f"Parent directory: {parent_dir}", file=sys.stderr)
    sys.exit(2)


def count_key_occurrences(lines: List[str], section_name: str, key: str) -> int:
    """Count how many times a key appears in a section (case-insensitive)."""
    sections = find_section_ranges(lines)
    if section_name not in sections:
        return 0
    
    start, end = sections[section_name]
    key_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.*$", re.IGNORECASE)
    count = 0
    
    for i in range(start + 1, end):
        line = lines[i].strip()
        if not line or line.startswith(';') or line.startswith('#'):
            continue
        if key_pattern.match(line):
            count += 1
    
    return count


def get_all_keys_in_section(lines: List[str], section_name: str) -> Dict[str, int]:
    """Get all keys in a section and their occurrence counts."""
    sections = find_section_ranges(lines)
    if section_name not in sections:
        return {}
    
    start, end = sections[section_name]
    key_pattern = re.compile(r"^\s*([^#;\s][^=\s]*)\s*=\s*.*\s*$", re.IGNORECASE)
    key_counts: Dict[str, int] = {}
    
    for i in range(start + 1, end):
        line = lines[i].strip()
        if not line or line.startswith(';') or line.startswith('#'):
            continue
        match = key_pattern.match(line)
        if match:
            key = match.group(1).strip()
            normalized_key = key.lower()
            key_counts[normalized_key] = key_counts.get(normalized_key, 0) + 1
    
    return key_counts


def create_test_ini_with_duplicates() -> str:
    """Create a test INI file with intentional duplicate entries."""
    content = """[ServerSettings]
HarvestAmountMultiplier=1.0
NPCDamageMultiplier=1.0
NPCHealthMultiplier=1.0
HarvestAmountMultiplier=2.0
NPCDamageMultiplier=1.5
MaxAggroRange=10000
NPCHealthMultiplier=1.2
MaxAggroRange=12000
PlayerDamageMultiplier=1.0
PlayerDamageMultiplier=1.1
PlayerDamageMultiplier=1.2
"""
    fd, path = tempfile.mkstemp(suffix='.ini', prefix='test_duplicates_')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    except Exception:
        os.close(fd)
        raise


def create_test_events_json() -> str:
    """Create a test events.json file for the test."""
    import json
    events_config = {
        "moon_phase": {
            "enabled": True,
            "gamma": 1.0,
            "mapping": {
                "HarvestAmountMultiplier": {"min": 1.0, "max": 6.0},
                "NPCDamageMultiplier": {"min": 1.0, "max": 2.0},
                "NPCHealthMultiplier": {"min": 1.0, "max": 2.0}
            }
        },
        "events": {
            "phases": {}
        },
        "precision": 6
    }
    
    fd, path = tempfile.mkstemp(suffix='.json', prefix='test_events_')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(events_config, f, indent=2)
        return path
    except Exception:
        os.close(fd)
        raise


def test_duplicate_removal():
    """Test that duplicate entries are properly removed."""
    print("🧪 Testing duplicate entries removal...")
    
    # Create test files
    ini_path = create_test_ini_with_duplicates()
    events_path = create_test_events_json()
    
    try:
        # Read initial state directly (without duplicate removal) to verify duplicates exist
        with open(ini_path, 'r', encoding='utf-8') as f:
            raw_lines = f.read().splitlines()
        initial_counts = get_all_keys_in_section(raw_lines, "ServerSettings")
        
        print(f"\n📋 Initial duplicate counts (before duplicate removal):")
        duplicates_found = False
        for key, count in initial_counts.items():
            if count > 1:
                duplicates_found = True
                print(f"  - {key}: {count} occurrences")
        
        if not duplicates_found:
            print("  ⚠️  No duplicates found in initial file - test may not be valid")
            return False
        
        # Run wrath_manager to update settings
        print(f"\n🔄 Running wrath_manager to update settings...")
        result = wrath_main([
            '--ini-path', ini_path,
            '--event-file', events_path,
            '--phase-day', '15',  # Full moon phase
        ])
        
        if result != 0:
            print(f"  ❌ wrath_manager exited with code {result}")
            return False
        
        # Read final state
        final_lines, _, _ = read_text_lines_with_meta(ini_path)
        final_counts = get_all_keys_in_section(final_lines, "ServerSettings")
        
        print(f"\n✅ Final key counts:")
        all_single = True
        for key, count in sorted(final_counts.items()):
            status = "✓" if count == 1 else "✗"
            print(f"  {status} {key}: {count} occurrence(s)")
            if count > 1:
                all_single = False
        
        # Verify specific keys that were duplicated
        test_keys = [
            "HarvestAmountMultiplier",
            "NPCDamageMultiplier", 
            "NPCHealthMultiplier",
            "MaxAggroRange",
            "PlayerDamageMultiplier"
        ]
        
        print(f"\n🔍 Verifying specific keys:")
        all_passed = True
        for key in test_keys:
            count = count_key_occurrences(final_lines, "ServerSettings", key)
            status = "✓ PASS" if count == 1 else f"✗ FAIL (found {count})"
            print(f"  {status}: {key}")
            if count != 1:
                all_passed = False
                # Show all occurrences
                sections = find_section_ranges(final_lines)
                if "ServerSettings" in sections:
                    start, end = sections["ServerSettings"]
                    key_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.*$", re.IGNORECASE)
                    for i in range(start + 1, end):
                        if key_pattern.match(final_lines[i].strip()):
                            print(f"      Line {i+1}: {final_lines[i].strip()}")
        
        return all_passed and all_single
        
    finally:
        # Cleanup
        try:
            os.remove(ini_path)
        except Exception:
            pass
        try:
            os.remove(events_path)
        except Exception:
            pass


def test_upsert_removes_duplicates():
    """Test that upsert_key_in_section properly removes duplicates."""
    print("\n🧪 Testing upsert_key_in_section duplicate removal...")
    
    # Create lines with duplicates
    lines = [
        "[ServerSettings]",
        "TestKey=value1",
        "OtherKey=other",
        "TestKey=value2",
        "TestKey=value3",
        "AnotherKey=test",
    ]
    
    # Upsert the key
    updated_lines, _ = upsert_key_in_section(
        lines, "ServerSettings", "TestKey", "newvalue"
    )
    
    # Count occurrences
    count = count_key_occurrences(updated_lines, "ServerSettings", "TestKey")
    
    if count == 1:
        print(f"  ✓ PASS: TestKey appears {count} time(s) after upsert")
        # Verify it's the new value
        sections = find_section_ranges(updated_lines)
        if "ServerSettings" in sections:
            start, end = sections["ServerSettings"]
            key_pattern = re.compile(r"^\s*TestKey\s*=\s*(.*)$", re.IGNORECASE)
            for i in range(start + 1, end):
                match = key_pattern.match(updated_lines[i].strip())
                if match:
                    value = match.group(1).strip()
                    if value == "newvalue":
                        print(f"  ✓ PASS: TestKey has correct value: {value}")
                        return True
                    else:
                        print(f"  ✗ FAIL: TestKey has wrong value: {value} (expected: newvalue)")
                        return False
        
        print(f"  ✗ FAIL: Could not find TestKey in section")
        return False
    else:
        print(f"  ✗ FAIL: TestKey appears {count} time(s) (expected 1)")
        return False


def main():
    """Run all duplicate entry tests."""
    print("=" * 60)
    print("TEST: Duplicate Entries Bug Fix")
    print("=" * 60)
    
    test1_passed = test_upsert_removes_duplicates()
    test2_passed = test_duplicate_removal()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        if not test1_passed:
            print("  - upsert_removes_duplicates test failed")
        if not test2_passed:
            print("  - duplicate_removal test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


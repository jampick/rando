# Grim Observer Test Suite

This directory contains tests for the Grim Observer application, specifically focusing on the `scan-monitor` functionality.

## Test Files

### `test_scan_monitor.py`
A comprehensive test suite that validates the scan-monitor functionality with extensive player name type testing.

**Features:**
- Creates a temporary test log file
- Starts the observer in scan-monitor mode
- Tests 20+ different player name types (ASCII, Unicode, special characters)
- Validates event detection and reporting
- Generates detailed test reports
- Saves results to JSON file

### `test_scan_monitor_simple.py`
A simplified test script that's easier to run and debug.

**Features:**
- Creates a temporary test log file
- Tests 6 common player name types
- Simpler output and error handling
- Good for quick validation

## Running the Tests

### Prerequisites
1. Make sure you're in the `grim_observer` directory
2. Ensure `grim_observer.py` is present
3. Python 3.6+ is installed

### Running the Simple Test
```bash
cd MoonTide/grim_observer
python3 tests/test_scan_monitor_simple.py
```

### Running the Comprehensive Test
```bash
cd MoonTide/grim_observer
python3 tests/test_scan_monitor.py
```

## What the Tests Validate

### 1. Initial Scan Phase
- ✅ Observer correctly scans existing log content
- ✅ No false positives from initial log entries
- ✅ Proper handling of non-player log lines

### 2. Monitoring Phase
- ✅ Observer continues monitoring after initial scan
- ✅ New log entries are detected in real-time
- ✅ Player events are processed as they appear

### 3. Player Event Detection
- ✅ Player connection events are detected
- ✅ Player disconnection events are detected
- ✅ Both BattlEye and LogNet disconnect formats are handled

### 4. Player Name Type Handling
The tests validate handling of various player name types:

**Simple Names:**
- `SimpleName` - Basic ASCII
- `Player123` - With numbers
- `Player_Name` - With underscore
- `Player-Name` - With hyphen

**Special Characters:**
- `Player#1234` - With hash and numbers
- `Player@Domain` - With at symbol
- `Player$Money` - With dollar sign
- `Player%Percent` - With percent

**Unicode Names:**
- `Æsir` - With Æ
- `Bjørn` - With ø
- `José` - With é
- `François` - With ç

**Edge Cases:**
- `A` - Single character
- `VeryLongPlayerNameThatExceedsNormalLength` - Very long name
- `Player With Spaces` - With spaces
- `Player\tTab` - With tab
- `Player\nNewline` - With newline

## Test Output

### Simple Test Output
```
🧪 Starting Simple Scan-Monitor Test
========================================
✅ Created test log file: /tmp/tmpXXXXXX.log
🚀 Starting Grim Observer in scan-monitor mode...
Running command: python3 grim_observer.py scan-monitor /tmp/tmpXXXXXX.log --map test --discord --verbose
⏳ Waiting for observer to start and scan initial content...
📝 Adding test player events...
📝 Added connect event for player: SimpleName
📝 Added disconnect event for player: SimpleName
...
👀 Monitoring for event detection...
✅ Observer is still running and monitoring
🎉 Test completed successfully!
```

### Comprehensive Test Output
The comprehensive test provides detailed validation and saves results to `test_scan_monitor_results.json`.

## Expected Behavior

1. **Initial Scan**: Observer should scan the test log and find no player events
2. **Monitoring**: Observer should continue running and monitoring for new entries
3. **Event Detection**: Each player connect/disconnect should be detected and logged
4. **Player Names**: All player name types should be handled correctly
5. **Discord Integration**: Events should be processed for Discord webhook (mocked)

## Troubleshooting

### Common Issues

**Observer fails to start:**
- Check that `grim_observer.py` exists in the current directory
- Ensure Python 3.6+ is installed
- Verify the script has execute permissions

**No events detected:**
- Check the observer output for error messages
- Verify the log file format matches expected patterns
- Ensure the observer is running in scan-monitor mode

**Test hangs:**
- The test may hang if the observer process doesn't start properly
- Check for Python import errors or missing dependencies
- Use Ctrl+C to interrupt and check error messages

### Debug Mode
For debugging, you can modify the test scripts to:
- Increase sleep times for slower systems
- Add more verbose output
- Check observer process status more frequently

## Test Results

Successful tests will:
- ✅ Create and clean up temporary log files
- ✅ Start and stop the observer cleanly
- ✅ Detect all expected player events
- ✅ Handle all player name types correctly
- ✅ Generate comprehensive test reports

Failed tests will show:
- ❌ Error messages and stack traces
- ❌ Observer process failures
- ❌ Event detection failures
- ❌ Resource cleanup issues

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines by:
1. Running them as part of the build process
2. Checking exit codes for pass/fail status
3. Parsing the JSON results for detailed reporting
4. Using the test output for automated validation

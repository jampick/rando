# Grim Observer Log File Auto-Detection

## New Features

The Grim Observer now supports automatic log file detection and monitoring, which solves the "Could not find valid connection time" issue by:

1. **Monitoring directories instead of specific files**
2. **Automatically detecting the most recent/active log file**
3. **Handling log file rotation and new file creation**
4. **Switching to new log files seamlessly**

## Usage

### Command Line Options

```bash
# Auto-detect log file in a directory
python grim_observer.py monitor ~/Library/Application\ Support/Steam/steamapps/common/Conan\ Exiles/ConanSandbox/Saved/Logs --auto-detect-log

# Specify a log directory explicitly
python grim_observer.py monitor /path/to/logs --log-directory /path/to/logs

# Use with map-specific configuration
python grim_observer.py monitor /path/to/logs --map exiled --auto-detect-log
```

### Configuration

Update your `config.json` to use directory paths:

```json
{
  "log_file_path": "~/Library/Application Support/Steam/steamapps/common/Conan Exiles/ConanSandbox/Saved/Logs",
  "auto_detect_log": true
}
```

## How It Works

1. **Directory Monitoring**: The system monitors a directory for log files matching patterns like:
   - `ConanSandbox.log`
   - `ConanSandbox*.log`
   - `ConanSandbox_*.log`
   - `ConanSandbox-*.log`

2. **File Selection**: Files are ranked by:
   - Modification time (most recent first)
   - File age (files older than 5 minutes are flagged as potentially stale)
   - Recent activity (files modified in the last 10 minutes are preferred)

3. **Automatic Switching**: Every 60 seconds, the system checks for new log files and switches if a more recent/active file is found.

4. **Seamless Transition**: When switching files, the system:
   - Scans the new file for existing events
   - Maintains player state continuity
   - Continues monitoring without interruption

## Benefits

- **Solves Connection Time Issues**: No more "Could not find valid connection time" errors
- **Handles Log Rotation**: Automatically switches to new log files when they're created
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Robust**: Handles various log file naming conventions
- **Backward Compatible**: Still works with specific file paths

## Testing

Run the test script to see what log files are detected:

```bash
python test_log_detection.py
```

This will scan common Conan Exiles log directories and show what files are found.

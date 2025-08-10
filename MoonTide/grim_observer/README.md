# Grim Observer - Conan Exiles Log Monitor

A Python-based log monitoring tool for Conan Exiles servers that tracks player connections, disconnections, and other events, with support for Discord webhook notifications.

## Features

- **Real-time log monitoring** with configurable check intervals
- **Player event detection** (connections, disconnections)
- **Discord webhook integration** for real-time notifications
- **Map-based configuration** (Exiled Lands, Isle of Siptah)
- **Simple Windows wrapper** for easy execution
- **Flexible operation modes** for different use cases

## Operation Modes

### 1. **scan** - One-time Processing
Processes the entire log file once and exits. Useful for:
- Historical analysis
- Batch processing of existing logs
- Testing configuration

### 2. **monitor** - Continuous Monitoring
Starts monitoring from the current log position only. Useful for:
- Live server monitoring
- When you only want new events
- Avoiding processing of historical data

### 3. **scan-monitor** - Scan Then Monitor (Default)
First processes the entire log file, then continues monitoring for new changes. Useful for:
- Getting complete history + live updates
- Server restarts where you want all events
- Most production scenarios

## Quick Start

### Windows (Recommended)
```batch
# Monitor Exiled Lands map
run_observer.bat exiled

# Monitor Isle of Siptah map
run_observer.bat siptah
```

The batch file automatically:
- Loads map-specific secrets (Discord webhook, log file path)
- Runs in scan-monitor mode (processes entire log + continues monitoring)
- Sends Discord notifications for player events
- Uses verbose logging for detailed output

### Direct Python Usage
```bash
# Scan entire log and continue monitoring (default behavior)
python grim_observer.py scan-monitor /path/to/ConanSandbox.log --map exiled

# Process entire log once and exit
python grim_observer.py scan /path/to/ConanSandbox.log --map exiled

# Start monitoring from current position only
python grim_observer.py monitor /path/to/ConanSandbox.log --map exiled

# With Discord webhook output
python grim_observer.py scan-monitor /path/to/ConanSandbox.log --map exiled --discord

# Webhook content only (no extra formatting)
python grim_observer.py scan-monitor /path/to/ConanSandbox.log --map exiled --webhook-only
```

## Configuration

### Map-Based Configuration
The system automatically loads configuration based on the specified map:

- **Exiled Lands** (`exiled`): Uses `configs/exiled/config.json`
- **Isle of Siptah** (`siptah`): Uses `configs/siptah/config.json`

### Secrets Management
Map-specific secrets are loaded automatically from Windows batch files:
- **Exiled Lands**: `secrets/secrets.exiled.bat`
- **Isle of Siptah**: `secrets/secrets.siptah.bat`

### Environment Variables
Set these in your secrets files:
- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
- `LOG_FILE_PATH`: Default log file path for the map
- `MAP_NAME`: Display name for the map
- `MAP_DESCRIPTION`: Description of the map

## File Structure

```
grim_observer/
├── grim_observer.py          # Main Python script
├── run_observer.bat          # Windows batch wrapper
├── config.json               # Default configuration
├── configs/                  # Map-specific configurations
│   ├── exiled/
│   │   └── config.json      # Exiled Lands config
│   └── siptah/
│       └── config.json      # Isle of Siptah config
├── secrets/                  # Map-specific secrets
│   ├── secrets.exiled.bat   # Windows secrets (Exiled)
│   └── secrets.siptah.bat   # Windows secrets (Siptah)
└── README.md                 # This file
```

## Discord Integration

When a Discord webhook URL is configured, the system will automatically send notifications for:

- **Player Connections**: 🟢 Player joined the server
- **Player Disconnections**: 🔴 Player left the server

### Webhook Format
```json
{
  "content": "🟢 **PlayerName** joined the server",
  "embeds": [{
    "title": "Player Connected",
    "description": "**PlayerName** has joined the server",
    "color": 0x00ff00,
    "fields": [
      {"name": "Player", "value": "PlayerName", "inline": true},
      {"name": "IP Address", "value": "192.168.1.100", "inline": true},
      {"name": "Time", "value": "2024-01-15 14:30:25", "inline": true}
    ]
  }]
}
```

## Testing

### Test with Sample Log
```bash
# Test scan mode with sample log
python grim_observer.py scan tests/conansandbox.sample.log --map exiled

# Test scan-monitor mode with sample log
python grim_observer.py scan-monitor tests/conansandbox.sample.log --map exiled
```

### Test Discord Webhooks
```bash
# Test webhook generation without sending
python grim_observer.py scan tests/conansandbox.sample.log --map exiled --webhook-only

# Test webhook generation and save to file
python grim_observer.py scan tests/conansandbox.sample.log --map exiled --discord --discord-output test_webhooks.json
```

## Troubleshooting

### Common Issues

1. **"No DISCORD_WEBHOOK_URL found"**
   - Check your secrets file has the correct webhook URL
   - Verify the secrets file is being loaded for your map

2. **"Missing log file path"**
   - Ensure LOG_FILE_PATH is set in your secrets file

3. **"Secrets file not found"**
   - Create the appropriate secrets file for your map
   - Use `run_observer.bat exiled` or `run_observer.bat siptah`

4. **Python not found**
   - Install Python 3.6+ and ensure it's in your PATH

### Log Levels
Use `--verbose` for detailed logging:
```bash
python grim_observer.py scan-monitor /path/to/log --map exiled --verbose
```

## Development

### Adding New Maps
1. Create `configs/{newmap}/config.json`
2. Create `secrets/secrets.{newmap}.bat` (Windows)
3. Update the batch file to support the new map

### Custom Event Patterns
Modify the regex patterns in `grim_observer.py` to detect additional event types.

## License

This project is part of the MoonTide Conan Exiles server management suite.

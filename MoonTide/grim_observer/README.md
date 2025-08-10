# Grim Observer

A Python script for monitoring Conan Exiles server logs and emitting Discord webhook events.

## Features

- **Real-time monitoring**: Tail log files for live event detection
- **Event parsing**: Extract player connections, disconnections, and other server events
- **Discord integration**: Generate and send Discord webhook payloads
- **Flexible output**: Multiple output formats including raw events, Discord format, and webhook-only
- **Map-based secrets**: Load Discord webhook URLs from map-specific secrets files

## Usage

### Basic Commands

```bash
# Scan entire log file for events
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log

# Monitor log file in real-time
python3 grim_observer.py monitor /path/to/ConanSandbox/Logs/ConanSandbox.log

# Output in Discord webhook format
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log --discord

# Show only Discord webhook content (no extra formatting)
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log --webhook-only

# Use map-specific secrets (loads Discord webhook URL from secrets file)
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log --map exiled
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log --map siptah
```

### Command Line Options

- `mode`: Operation mode (`scan` or `monitor`)
- `log_file`: Path to the ConanSandbox log file
- `--discord`: Output in Discord webhook format
- `--discord-output FILE`: Save Discord webhook payloads to JSON file
- `--webhook-only`: Show only Discord webhook content without extra formatting
- `--map MAP`: Specify map name (e.g., `exiled`, `siptah`) for secrets loading
- `--verbose`: Enable verbose logging

## Secrets Configuration

Grim Observer supports map-based secrets loading for Discord webhook URLs. Create secrets files in the `secrets/` directory:

### File Structure
```
secrets/
├── secrets.exiled.json      # Exiled Lands map secrets
├── secrets.siptah.json      # Isle of Siptah map secrets
└── default.json             # Default secrets (fallback)
```

### Secrets File Format
```json
{
    "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
    "map_name": "exiled",
    "description": "Secrets for the Exiled Lands map"
}
```

### Loading Priority
1. Map-specific secrets file (e.g., `secrets.exiled.json`)
2. Default secrets file (`secrets/default.json`)
3. Environment variable `DISCORD_WEBHOOK_URL`

## Event Types

Currently supported events:
- **Player Connected**: When a player joins the server
- **Player Disconnected**: When a player leaves the server

## Discord Webhook Format

Events are formatted as Discord webhook payloads with:
- Rich embeds with player information
- Color coding (green for joins, red for disconnects)
- Timestamps and IP addresses (when available)
- Automatic webhook sending when configured

## Examples

### Basic Scan
```bash
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log
```

### Discord Integration with Map Secrets
```bash
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log --map exiled --discord
```

### Webhook-Only Output
```bash
python3 grim_observer.py scan /path/to/ConanSandbox/Logs/ConanSandbox.log --map siptah --webhook-only
```

## Requirements

- Python 3.6+
- Access to Conan Exiles server log files
- Discord webhook URL (configured via secrets or environment)

## Installation

1. Clone or download the script
2. Create secrets files with your Discord webhook URLs
3. Run the script with appropriate parameters

## Notes

- The script automatically detects log file encoding and handles errors gracefully
- Webhook sending requires a valid Discord webhook URL
- Monitor mode runs continuously until interrupted (Ctrl+C)
- Scan mode processes the entire log file once and exits

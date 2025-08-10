# Grim Observer - Map-Based Configuration System

This directory contains map-specific configuration files for the Grim Observer system. Each map can have its own configuration settings, secrets, and event patterns.

## Directory Structure

```
configs/
├── README.md                 # This file
├── exiled/                   # Exiled Lands map configuration
│   └── config.json          # Exiled Lands specific settings
└── siptah/                   # Isle of Siptah map configuration
    └── config.json          # Isle of Siptah specific settings
```

## Usage

The system automatically loads map-specific configurations based on the map parameter:

- **Exiled Lands**: `--map exiled` → loads `configs/exiled/config.json`
- **Isle of Siptah**: `--map siptah` → loads `configs/siptah/config.json`

## Windows Batch Wrapper

The `run_observer.bat` file automatically handles map selection:

```batch
# Monitor Exiled Lands
run_observer.bat exiled

# Monitor Isle of Siptah  
run_observer.bat siptah
```

## Configuration Files

Each map's `config.json` can contain:

- **Output file names** (e.g., `grim_events_exiled.json`)
- **Map-specific settings** (check intervals, log levels)
- **Event patterns** (custom regex for different maps)
- **Notification settings** (Discord webhook configuration)

## Secrets Integration

Map-specific secrets are loaded from:
- **Exiled Lands**: `secrets/secrets.exiled.bat`
- **Isle of Siptah**: `secrets/secrets.siptah.bat`

These files set environment variables like:
- `DISCORD_WEBHOOK_URL`
- `LOG_FILE_PATH`
- `MAP_NAME`
- `MAP_DESCRIPTION`

## Fallback Behavior

If a map-specific config is not found, the system falls back to:
1. `configs/{map}/config.json` (map-specific)
2. `config.json` (default configuration)

## Adding New Maps

To add support for a new map:

1. **Create config directory**:
   ```
   configs/newmap/
   └── config.json
   ```

2. **Create secrets file**:
   ```
   secrets/secrets.newmap.bat
   ```

3. **Update batch file** (if needed):
   - Add the new map to the usage examples in `run_observer.bat`

## Example Configuration

```json
{
  "output_file": "grim_events_exiled.json",
  "check_interval": 1.0,
  "verbose": true,
  "log_level": "INFO",
  "max_events_in_memory": 10000,
  "event_retention_hours": 24,
  "player_count_update_interval": 30,
  "map_name": "exiled",
  "map_description": "Exiled Lands - The original Conan Exiles map",
  "patterns": {
    "player_connected": "BattlEyeServer: Print Message: Player #(\\d+) (\\S+) \\((\\S+):(\\d+)\\) connected",
    "player_disconnected_battleye": "BattlEyeServer: Print Message: Player #(\\d+) (\\S+) disconnected",
    "player_disconnected_lognet": "LogNet: Player disconnected: (\\S+) (filtered: excludes names with #numbers)"
  },
  "output_formats": ["json", "csv"],
  "notifications": {
    "discord_webhook": "",
    "email": {
      "smtp_server": "",
      "smtp_port": 587,
      "username": "",
      "password": "",
      "recipients": []
    }
  }
}
```

## Notes

- Configuration files use standard JSON format
- All paths are relative to the grim_observer directory
- Environment variables from secrets files take precedence over config values
- The system automatically validates configuration files on startup

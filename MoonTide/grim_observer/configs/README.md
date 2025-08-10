# Grim Observer Map-Based Configuration

This directory contains map-specific configurations for Grim Observer, allowing different settings for different Conan Exiles maps.

## Directory Structure

```
configs/
├── exiled/           # Exiled Lands map configuration
│   └── config.json   # Map-specific settings
├── siptah/           # Isle of Siptah map configuration
│   └── config.json   # Map-specific settings
└── README.md         # This file
```

## Usage

When running Grim Observer with the `--map` flag, it will automatically:

1. **Load map-specific secrets** from `secrets/secrets.{map}.bat`
2. **Use map-specific config** from `configs/{map}/config.json`
3. **Derive log file path** from the secrets file (unless overridden with `--log-file`)
4. **Set map-specific environment variables** for Discord webhooks and other settings

## Examples

### Exiled Lands Map (using default log file from secrets)
```cmd
run_observer.bat --map exiled
```

### Isle of Siptah Map (using default log file from secrets)
```cmd
run_observer.bat --map siptah
```

### Override log file path
```cmd
run_observer.bat --map exiled --log-file "C:\Custom\Path\To\Log.log"
```

### Custom config file
```cmd
run_observer.bat --map siptah --config "C:\path\to\custom_config.json"
```

## Configuration Files

Each map has its own `config.json` with:
- Map-specific output file names
- Map identification and description
- Same pattern matching and notification settings
- Customizable intervals and retention policies

**Note:** Log file paths are no longer stored in config files - they are derived from the secrets files.

## Secrets Integration

The secrets files (`secrets.exiled.bat`, `secrets.siptah.bat`) set environment variables like:
- `DISCORD_WEBHOOK_URL` - Discord webhook for the specific map
- `MAP_NAME` - Internal map identifier
- `MAP_DESCRIPTION` - Human-readable map description
- `LOG_FILE_PATH` - Default log file path for the map

## Fallback Behavior

If no map-specific config is found, Grim Observer falls back to:
1. Default `config.json` in the root directory
2. Default secrets (if any)
3. Command-line overrides

## Adding New Maps

To add support for a new map:

1. Create `configs/{newmap}/config.json`
2. Create `secrets/secrets.{newmap}.bat` with `LOG_FILE_PATH` variable
3. Update the batch files to recognize the new map value
4. Test with `run_observer.bat --map {newmap}`

## Log File Path Resolution

The log file path is resolved in this order:
1. Command-line `--log-file` parameter (highest priority)
2. `LOG_FILE_PATH` from the selected map's secrets file
3. Error if neither is available

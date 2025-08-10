# Grim Observer - Map-Based Configuration System

**Part of the Rando Server Management Suite**

This directory contains map-specific configuration files for the Grim Observer system. Each map can have its own configuration settings, secrets, and event patterns, enabling comprehensive server management across different Conan Exiles maps.

## 🎯 Overview

The configuration system provides:
- **Map-specific settings** for different Conan Exiles maps
- **Automatic configuration loading** based on map selection
- **Secrets management** for sensitive data like Discord webhooks
- **Fallback behavior** to default configurations when needed
- **Extensible architecture** for adding new maps

## 📁 Directory Structure

```
configs/
├── README.md                 # This file
├── exiled/                   # Exiled Lands map configuration
│   └── config.json          # Exiled Lands specific settings
└── siptah/                   # Isle of Siptah map configuration
    └── config.json          # Isle of Siptah specific settings
```

## 🚀 Usage

### Automatic Map Selection
The system automatically loads map-specific configurations based on the map parameter:

- **Exiled Lands**: `--map exiled` → loads `configs/exiled/config.json`
- **Isle of Siptah**: `--map siptah` → loads `configs/siptah/config.json`

### Windows Batch Wrapper
The `run_observer.bat` file automatically handles map selection:

```batch
# Monitor Exiled Lands
run_observer.bat exiled

# Monitor Isle of Siptah  
run_observer.bat siptah
```

### Direct Python Usage
```bash
# Monitor Exiled Lands with automatic config loading
python3 grim_observer.py scan-monitor /path/to/log.log --map exiled --discord

# Monitor Isle of Siptah with automatic config loading
python3 grim_observer.py scan-monitor /path/to/log.log --map siptah --discord
```

## ⚙️ Configuration Files

### Map-Specific Configuration
Each map's `config.json` can contain:

- **Output file names** (e.g., `grim_events_exiled.json`)
- **Map-specific settings** (check intervals, log levels)
- **Event patterns** (custom regex for different maps)
- **Notification settings** (Discord webhook configuration)
- **Performance tuning** (memory limits, retention policies)

### Example Configuration Structure
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

## 🔐 Secrets Integration

### Map-Specific Secrets
Map-specific secrets are loaded automatically from:

- **Windows**: `secrets/secrets.{map}.bat` files
- **Cross-platform**: Environment variables
- **Required variables**: `DISCORD_WEBHOOK_URL`, `LOG_FILE_PATH`
- **Optional variables**: `MAP_NAME`, `MAP_DESCRIPTION`

### Windows Secrets Files
```batch
# secrets/secrets.exiled.bat
@echo off
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
set LOG_FILE_PATH=C:\ConanExiles\ConanSandbox\Saved\Logs\ConanSandbox.log
set MAP_NAME=Exiled Lands
set MAP_DESCRIPTION=The original Conan Exiles map
```

### Environment Variables
```bash
# Cross-platform secrets
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export LOG_FILE_PATH="/path/to/ConanSandbox.log"
export MAP_NAME="Exiled Lands"
export MAP_DESCRIPTION="The original Conan Exiles map"
```

## 🔄 Fallback Behavior

The system follows this configuration loading order:

1. **Map-specific config**: `configs/{map}/config.json`
2. **Default config**: `config.json` (root directory)
3. **Hardcoded defaults**: Built-in fallback values

### Configuration Merging
- **Map-specific settings** override default values
- **Environment variables** take precedence over config files
- **Missing values** fall back to defaults
- **Validation** ensures required fields are present

## 🆕 Adding New Maps

### Step 1: Create Configuration Directory
```bash
mkdir configs/newmap
```

### Step 2: Create Configuration File
```json
# configs/newmap/config.json
{
  "output_file": "grim_events_newmap.json",
  "map_name": "New Map",
  "map_description": "Description of the new map",
  "check_interval": 1.0,
  "verbose": true,
  "log_level": "INFO"
}
```

### Step 3: Create Secrets File (Windows)
```batch
# secrets/secrets.newmap.bat
@echo off
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
set LOG_FILE_PATH=C:\ConanExiles\ConanSandbox\Saved\Logs\ConanSandbox.log
set MAP_NAME=New Map
set MAP_DESCRIPTION=Description of the new map
```

### Step 4: Update Batch Files (Optional)
Add the new map to `run_observer.bat`:
```batch
if "%1"=="newmap" (
    call secrets\secrets.newmap.bat
    python3 grim_observer.py scan-monitor "%LOG_FILE_PATH%" --map newmap --discord --verbose
    goto :eof
)
```

### Step 5: Test Configuration
```bash
# Test the new map configuration
python3 grim_observer.py scan /path/to/log.log --map newmap --verbose
```

## 🔧 Advanced Configuration

### Custom Event Patterns
Different maps may have different log formats. Customize patterns:

```json
{
  "patterns": {
    "player_connected": "Custom pattern for player connections",
    "player_disconnected": "Custom pattern for player disconnections",
    "server_event": "Custom pattern for server events"
  }
}
```

### Performance Tuning
```json
{
  "performance": {
    "check_interval": 1.0,
    "max_events_in_memory": 10000,
    "event_retention_hours": 24,
    "player_count_update_interval": 30,
    "batch_size": 100
  }
}
```

### Output Configuration
```json
{
  "output": {
    "formats": ["json", "csv"],
    "compression": true,
    "rotation": {
      "max_size_mb": 100,
      "backup_count": 5
    }
  }
}
```

## 🧪 Testing Configuration

### Validate Configuration Files
```bash
# Test configuration loading
python3 -c "
from grim_observer import GrimObserver
observer = GrimObserver('/tmp/test.log', map_name='exiled')
print('Configuration loaded successfully')
"
```

### Test Map-Specific Settings
```bash
# Test with specific map
python3 grim_observer.py scan /path/to/log.log --map exiled --verbose

# Test with different map
python3 grim_observer.py scan /path/to/log.log --map siptah --verbose
```

### Configuration Validation
The system automatically validates:
- **Required fields** are present
- **Data types** are correct
- **Value ranges** are within acceptable limits
- **File paths** are accessible
- **Webhook URLs** are valid

## 🔒 Security Considerations

### Secrets Management
- **Never commit secrets** to version control
- **Use environment variables** for cross-platform compatibility
- **Rotate webhook URLs** regularly
- **Limit webhook permissions** to necessary channels

### Configuration Security
- **Validate all inputs** to prevent injection attacks
- **Use HTTPS** for all external connections
- **Implement rate limiting** for Discord webhooks
- **Log configuration changes** for audit purposes

## 🚨 Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Check the map name spelling
   - Verify the configs directory structure
   - Ensure file permissions are correct

2. **"Secrets not loaded"**
   - Check secrets file naming convention
   - Verify environment variables are set
   - Ensure batch files are in the correct location

3. **"Invalid configuration format"**
   - Validate JSON syntax
   - Check required field names
   - Verify data types are correct

4. **"Map not supported"**
   - Add the map to the configuration system
   - Update batch files if using Windows wrappers
   - Test with the `--map` parameter

### Debug Mode
Use `--verbose` for detailed configuration information:
```bash
python3 grim_observer.py scan /path/to/log.log --map exiled --verbose
```

## 🔗 Integration with Other Systems

### With MoonTide Wrath Manager
- **Shared map configuration** for consistent naming
- **Coordinated event management** between systems
- **Unified Discord integration** for comprehensive notifications
- **Synchronized configuration updates**

### With External Monitoring
- **Webhook endpoints** for custom integrations
- **JSON output** for data processing
- **Log file monitoring** for external analysis
- **API endpoints** for status queries

## 📊 Configuration Analytics

### Usage Tracking
- **Map popularity** and usage patterns
- **Configuration change frequency** and impact
- **Performance correlation** with different settings
- **Error rates** by configuration type

### Optimization Opportunities
- **Resource usage** analysis by configuration
- **Performance bottlenecks** identification
- **Configuration efficiency** improvements
- **User experience** optimization

## 📚 Documentation and Support

### Configuration Guides
- **This file**: Map-based configuration system overview
- **Main README**: Grim Observer comprehensive guide
- **Project README**: System integration and setup
- **Component READMEs**: Detailed functionality guides

### Support Resources
- **Troubleshooting sections** in each README
- **Test suite documentation** for validation
- **Integration guides** for system coordination
- **Community resources** for advanced usage

---

**"The configuration is the foundation. Build it well, and the system will serve you faithfully."**

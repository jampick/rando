# Grim Observer - Conan Exiles Server Monitor

**Version:** 1.0.0  
**Date:** 2025-08-09

A Python-based real-time monitoring system for Conan Exiles servers that tracks player activity, server status, and automatically sends Discord notifications. Part of the **Rando Server Management Suite**.

## ⚠️ **CRITICAL: Default Images Need Updating**

🚨 **The system currently uses placeholder images that MUST be replaced for production use.**

### 🎯 **What Needs Updating**
- **Discord embed images** are currently placeholder skulls and generic text
- **GitHub raw URLs** are used as defaults (not suitable for production)
- **No server branding** or custom theming

### 🔧 **Quick Fix Options**
1. **Use custom URLs in commands** (recommended):
   ```bash
   python3 grim_observer.py scan-monitor log.log --map exiled --discord \
     --thumbnail-url "https://your-domain.com/your-thumb.png" \
     --main-image-url "https://your-domain.com/your-main.png"
   ```

2. **Update default URLs in code**:
   Edit `grim_observer.py` and replace the placeholder URLs

3. **Generate new placeholder images**:
   ```bash
   # Windows
   generate_placeholders.bat
   # Mac/Linux
   ./generate_placeholders.sh
   ```

📖 **Full image setup guide**: [Placeholder Images README](placeholder_images/README.md)

---

## 🎯 Overview

Grim Observer provides comprehensive server monitoring with:
- **Real-time log parsing** and event detection
- **Player tracking** (connections, disconnections, activity patterns)
- **Discord integration** for automated notifications
- **Map-specific configurations** (Exiled Lands, Isle of Siptah)
- **Empty server detection** with configurable messaging intervals
- **Comprehensive testing** with automated validation

## 🚀 Quick Start

### Windows (Recommended)
```batch
# Monitor Exiled Lands map
run_observer.bat exiled

# Monitor Isle of Siptah map
run_observer.bat siptah
```

### Direct Python Usage
```bash
# Scan entire log and continue monitoring (default)
python3 grim_observer.py scan-monitor /path/to/ConanSandbox.log --map exiled --discord

# Process entire log once and exit
python3 grim_observer.py scan /path/to/ConanSandbox.log --map exiled

# Start monitoring from current position only
python3 grim_observer.py monitor /path/to/ConanSandbox.log --map exiled --discord
```

### Testing
```bash
# Run all tests with clear pass/fail results
python3 run_tests.py

# Windows test runner
run_tests.bat
```

## 🌟 Core Features

### Real-time Monitoring
- **Live log parsing** with configurable check intervals (default: 1 second)
- **Event detection** for player connections, disconnections, and server events
- **Memory-efficient** event storage with configurable retention
- **Automatic recovery** from log file rotation and server restarts

### Player Tracking
- **Connection events** with IP address and timestamp logging
- **Disconnection detection** supporting multiple log formats
- **Player count monitoring** with real-time updates
- **Activity patterns** for server population analysis

### Discord Integration
- **Rich embeds** with server information and player details
- **Configurable notifications** for different event types
- **Empty server messaging** with customizable intervals (default: 4 hours)
- **Map-specific theming** and branding

### Map Support
- **Exiled Lands**: The original Conan Exiles map
- **Isle of Siptah**: The expansion map with unique mechanics
- **Automatic configuration** loading based on map selection
- **Customizable settings** per map

## 🔧 Operation Modes

### 1. **scan** - Historical Analysis
Processes the entire log file once and exits.
```bash
python3 grim_observer.py scan /path/to/log.log --map exiled
```
**Use cases:**
- Historical player activity analysis
- Batch processing of existing logs
- Configuration testing and validation

### 2. **monitor** - Live Monitoring Only
Starts monitoring from the current log position.
```bash
python3 grim_observer.py monitor /path/to/log.log --map exiled --discord
```
**Use cases:**
- Live server monitoring
- Avoiding historical data processing
- Resource-constrained environments

### 3. **scan-monitor** - Complete Coverage (Default)
First processes the entire log file, then continues monitoring.
```bash
python3 grim_observer.py scan-monitor /path/to/log.log --map exiled --discord
```
**Use cases:**
- Complete server history + live updates
- Server restarts with full event tracking
- Production monitoring scenarios

## ⚙️ Configuration

### Map-Based Configuration
The system automatically loads configuration based on the specified map:

- **Exiled Lands** (`exiled`): Uses `configs/exiled/config.json`
- **Isle of Siptah** (`siptah`): Uses `configs/siptah/config.json`

### Secrets Management
Map-specific secrets are loaded automatically:
- **Windows**: `secrets/secrets.{map}.bat` files
- **Cross-platform**: Environment variables
- **Required**: `DISCORD_WEBHOOK_URL`, `LOG_FILE_PATH`
- **Optional**: `MAP_NAME`, `MAP_DESCRIPTION`

### Environment Variables
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export LOG_FILE_PATH="/path/to/ConanSandbox.log"
export MAP_NAME="Exiled Lands"
export MAP_DESCRIPTION="The original Conan Exiles map"
```

## 📁 File Structure

```
grim_observer/
├── grim_observer.py              # Main monitoring engine
├── run_observer.bat              # Windows batch wrapper
├── run_tests.py                  # Test runner with clear outcomes
├── run_tests.bat                 # Windows test wrapper
├── config.json                   # Default configuration
├── configs/                      # Map-specific configurations
│   ├── exiled/
│   │   └── config.json          # Exiled Lands config
│   ├── siptah/
│   │   └── config.json          # Isle of Siptah config
│   └── README.md                 # Configuration guide
├── secrets/                      # Map-specific secrets
│   ├── secrets.exiled.bat       # Windows secrets (Exiled)
│   └── secrets.siptah.bat       # Windows secrets (Siptah)
├── placeholder_images/           # Discord embed images
│   ├── README.md                 # Image usage guide
│   └── *.png                     # Generated placeholder images
├── tests/                        # Test suite
│   ├── README.md                 # Testing guide
│   ├── test_parser.py            # Parser validation
│   ├── test_scan_monitor.py     # Comprehensive monitoring tests
│   └── test_empty_message.py    # Discord message tests
└── README.md                     # This file
```

## 🎨 Discord Integration

### Automatic Notifications
When configured with a Discord webhook, the system sends:

- **🟢 Player Connections**: Player joined the server
- **🔴 Player Disconnections**: Player left the server
- **⚔️ Empty Server Messages**: Configurable interval notifications

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
    ],
    "thumbnail": {"url": "https://your-domain.com/thumb.png"},
    "footer": {"text": "Grim Observer", "icon_url": "https://your-domain.com/icon.png"}
  }]
}
```

### Empty Server Messages
- **Configurable interval** (default: 4 hours)
- **Map-specific theming** and branding
- **Rich embeds** with server status information
- **Automatic timing** based on last player activity

## 🧪 Testing

### Automated Test Suite
```bash
# Run all tests with clear pass/fail results
python3 run_tests.py

# Windows test runner
run_tests.bat
```

### Test Coverage
- **Log Parser**: Event detection and parsing accuracy
- **Scan Monitor**: End-to-end monitoring functionality
- **Empty Messages**: Discord webhook generation
- **Configuration**: Secrets and config file loading

### Individual Tests
```bash
# Parser validation
python3 tests/test_parser.py

# Monitoring functionality
python3 tests/test_scan_monitor_simple.py

# Discord integration
python3 tests/test_empty_message.py
```

## 🔧 Advanced Configuration

### Custom Event Patterns
Modify regex patterns in `grim_observer.py` to detect additional event types:
```python
self.patterns = {
    "player_connected": "BattlEyeServer: Print Message: Player #(\\d+) (\\S+) \\((\\S+):(\\d+)\\) connected",
    "player_disconnected": "BattlEyeServer: Print Message: Player #(\\d+) (\\S+) disconnected",
    "custom_event": "Your custom pattern here"
}
```

### Performance Tuning
```json
{
  "check_interval": 1.0,
  "max_events_in_memory": 10000,
  "event_retention_hours": 24,
  "player_count_update_interval": 30
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"No DISCORD_WEBHOOK_URL found"**
   - Check your secrets file has the correct webhook URL
   - Verify the secrets file is being loaded for your map

2. **"Missing log file path"**
   - Ensure LOG_FILE_PATH is set in your secrets file
   - Check file permissions and accessibility

3. **"Secrets file not found"**
   - Create the appropriate secrets file for your map
   - Use `run_observer.bat exiled` or `run_observer.bat siptah`

4. **Python not found**
   - Install Python 3.6+ and ensure it's in your PATH
   - Use `python3` instead of `python` on some systems

### Debug Mode
Use `--verbose` for detailed logging:
```bash
python3 grim_observer.py scan-monitor /path/to/log --map exiled --verbose
```

### Log Levels
- **INFO**: Standard operation information
- **DEBUG**: Detailed debugging information (with `--verbose`)
- **ERROR**: Error conditions and failures

## 🔄 Development

### Adding New Maps
1. Create `configs/{newmap}/config.json`
2. Create `secrets/secrets.{newmap}.bat` (Windows)
3. Update batch files to support the new map
4. Add map-specific placeholder images if desired

### Custom Event Types
1. Add new regex patterns to the patterns dictionary
2. Implement event processing logic
3. Add Discord webhook formatting
4. Update tests to validate new functionality

### Extending Notifications
1. Modify the webhook payload generation
2. Add new notification types
3. Implement custom Discord embed formatting
4. Update configuration options

## 📊 Monitoring & Analytics

### Event Tracking
- **Player session duration** analysis
- **Server population patterns** over time
- **Peak activity hours** identification
- **Player retention** metrics

### Performance Metrics
- **Event processing speed** monitoring
- **Memory usage** optimization
- **Log parsing efficiency** tracking
- **Discord API response times**

## 🔒 Security & Privacy

- **No sensitive data** stored in code or logs
- **IP address logging** for security monitoring
- **Configurable data retention** policies
- **Secure webhook handling** with validation

## 🤝 Integration

### With MoonTide Wrath Manager
- **Coordinated server management** with automated tuning
- **Event synchronization** between systems
- **Unified configuration** management
- **Shared Discord integration** for comprehensive notifications

### With External Systems
- **Webhook endpoints** for custom integrations
- **JSON output** for data processing
- **Log file monitoring** for external analysis
- **API endpoints** for status queries

## 📄 License

This project is part of the Rando Conan Exiles server management suite.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review test outputs for validation
3. Check the main project README for integration guidance
4. Ensure all dependencies are properly installed

---

**"The Grim Observer watches, and CROM judges."**

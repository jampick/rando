# Rando - Conan Exiles Server Management Suite

A comprehensive toolkit for managing Conan Exiles dedicated servers with automated tuning, real-time monitoring, and intelligent event management.

## 🎯 Project Overview

This repository contains a complete server management solution that combines:

- **🌙 MoonTide Wrath Manager**: Automated server tuning based on real-world lunar cycles and calendar events
- **👁️ Grim Observer**: Real-time log monitoring with Discord integration and player event tracking
- **🧪 Comprehensive Testing**: Full test suites for both components with automated validation

## 🚀 Quick Start

### 1. Server Tuning (MoonTide)
```bash
# Windows
cd MoonTide/wrath_manager
start_wrath_manager.bat exiled

# Linux/Mac
cd MoonTide/wrath_manager
python3 wrath_manager.py --ini-path /path/to/ServerSettings.ini --event-file events.json
```

### 2. Server Monitoring (Grim Observer)
```bash
# Windows
cd MoonTide/grim_observer
run_observer.bat exiled

# Linux/Mac
cd MoonTide/grim_observer
python3 grim_observer.py scan-monitor /path/to/ConanSandbox.log --map exiled --discord
```

### 3. Run Tests
```bash
# All tests
cd MoonTide/grim_observer
python3 run_tests.py

# Windows
run_tests.bat
```

## 🖼️ **IMPORTANT: Default Images Need Updating**

⚠️ **The system currently uses placeholder images that MUST be replaced for production use.**

### 🎯 **Images That Need Updating**

#### **Discord Embed Images (Grim Observer)**
- **`thumbnail.png`** (96x96) - Currently placeholder skull icon
- **`main_image.png`** (400x300) - Currently placeholder "CROM SLEEPS" message  
- **`footer_icon.png`** (16x16) - Currently placeholder sword icon
- **Map-specific variants** for Exiled Lands and Isle of Siptah

#### **Current Status**
- ❌ **Using GitHub raw URLs** (not suitable for production)
- ❌ **Placeholder content** (generic skulls and text)
- ❌ **No branding** (generic CROM aesthetic)

### 🔧 **How to Update Images**

#### **Option 1: Upload Custom Images (Recommended)**
1. **Create/obtain your custom images**:
   - Server logo or branding
   - Themed artwork for your server
   - Professional graphics for Discord embeds

2. **Upload to image hosting service**:
   - [Imgur](https://imgur.com/) (free, reliable)
   - [Discord](https://discord.com/) (upload to your server)
   - Your own web server (HTTPS required)

3. **Use custom URLs in commands**:
   ```bash
   python3 grim_observer.py scan-monitor log.log --map exiled --discord \
     --thumbnail-url "https://your-domain.com/your-thumb.png" \
     --main-image-url "https://your-domain.com/your-main.png" \
     --footer-icon-url "https://your-domain.com/your-icon.png"
   ```

#### **Option 2: Update Default URLs in Code**
Edit `MoonTide/grim_observer/grim_observer.py` and replace the default image URLs:
```python
# Replace these placeholder URLs with your custom images
self.empty_server_images = {
    'thumbnail': 'https://your-domain.com/your-thumb.png',
    'main_image': 'https://your-domain.com/your-main.png', 
    'footer_icon': 'https://your-domain.com/your-icon.png'
}
```

#### **Option 3: Use Generated Placeholder Images**
The system includes a placeholder image generator for testing:
```bash
cd MoonTide/grim_observer
# Windows
generate_placeholders.bat
# Mac/Linux  
./generate_placeholders.sh
```

### 📋 **Image Requirements**
- **Format**: PNG (transparent background support)
- **Dimensions**: 
  - Thumbnail: 96x96px
  - Main Image: 400x300px max
  - Footer Icon: 16x16px
- **Access**: Must be publicly accessible via HTTPS
- **Size**: Under 8MB for Discord compatibility

### 🎨 **Customization Ideas**
- **Server branding** and logos
- **Map-specific themes** (Exiled Lands vs Siptah)
- **Seasonal variations** for different events
- **Professional graphics** for community engagement

---

## 📁 Project Structure

```
rando/
├── MoonTide/                    # Main server management components
│   ├── wrath_manager/          # Automated server tuning system
│   │   ├── wrath_manager.py    # Core tuning engine
│   │   ├── events.json         # Event configuration
│   │   ├── EVENTS_DESIGN.md    # Event system documentation
│   │   └── tests/              # Tuning system tests
│   └── grim_observer/          # Real-time server monitoring
│       ├── grim_observer.py    # Core monitoring engine
│       ├── run_observer.bat    # Windows wrapper
│       ├── run_tests.py        # Test runner
│       ├── configs/            # Map-specific configurations
│       ├── placeholder_images/ # ⚠️ PLACEHOLDER IMAGES (UPDATE REQUIRED)
│       └── tests/              # Monitoring system tests
├── README.md                    # This file
└── .gitignore                  # Git exclusions
```

## 🌟 Key Features

### MoonTide Wrath Manager
- **Lunar Cycle Integration**: Server settings automatically adjust based on real-world moon phases
- **Event System**: Calendar events, seasonal changes, and custom triggers
- **Safe Automation**: Automatic backups, idempotent writes, and rollback capability
- **MOTD Management**: Dynamic message-of-the-day updates with event context

### Grim Observer
- **Real-time Monitoring**: Live log parsing with configurable intervals
- **Player Tracking**: Connection/disconnection events with detailed logging
- **Discord Integration**: Automated notifications for server events
- **Map Support**: Exiled Lands and Isle of Siptah configurations
- **Empty Server Detection**: Intelligent empty server messaging with configurable intervals

## 🎮 Supported Maps

- **Exiled Lands**: The original Conan Exiles map
- **Isle of Siptah**: The expansion map with unique mechanics

## 🛠️ Requirements

- **Python 3.6+** for all components
- **Conan Exiles Dedicated Server** (Windows/Linux)
- **Discord Webhook** (optional, for notifications)
- **Windows**: Batch file support for easy execution
- **Linux**: Systemd integration for automated startup
- **Custom Images**: Replace placeholder images for production use

## 📚 Documentation

- **MoonTide Overview**: [Wrath Manager README](MoonTide/wrath_manager/README.md)
- **Event System**: [Events Design Guide](MoonTide/wrath_manager/EVENTS_DESIGN.md)
- **Monitoring**: [Grim Observer README](MoonTide/grim_observer/README.md)
- **Configuration**: [Config System Guide](MoonTide/grim_observer/configs/README.md)
- **Image Setup**: [Placeholder Images Guide](MoonTide/grim_observer/placeholder_images/README.md)

## 🔧 Configuration

### Environment Setup
1. **Clone the repository** to your server
2. **Configure map-specific secrets** in the respective directories
3. **Set up Discord webhooks** (optional)
4. **Configure log file paths** for your server setup

### Map Configuration
Each map has its own configuration files:
- `configs/{map}/config.json` - Map-specific settings
- `secrets/secrets.{map}.bat` - Windows secrets (Windows only)
- Environment variables for cross-platform compatibility

## 🧪 Testing

### Automated Test Suite
```bash
# Run all tests
python3 run_tests.py

# Individual component tests
cd MoonTide/wrath_manager/tests
./run_all_tests.sh

cd MoonTide/grim_observer/tests
python3 test_scan_monitor_simple.py
```

### Test Coverage
- **Configuration Loading**: Secrets, config files, and environment variables
- **Event Detection**: Player connections, disconnections, and edge cases
- **Discord Integration**: Webhook payload generation and formatting
- **System Integration**: End-to-end functionality validation

## 🚨 Monitoring & Alerts

### Real-time Notifications
- **Player Events**: Join/leave notifications with player details
- **Empty Server**: Configurable empty server messages (default: 4 hours)
- **System Status**: Server health and configuration updates
- **Event Triggers**: Moon phase changes and calendar events

### Discord Integration
- Rich embeds with server information
- Player event tracking and history
- Configurable notification intervals
- Map-specific theming and branding

## 🔒 Security & Safety

- **No Secrets in Code**: All sensitive data stored in external files
- **Automatic Backups**: One backup per run with rotation
- **Idempotent Operations**: Safe to run multiple times
- **Validation**: Comprehensive input validation and error handling

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Run the test suite**
5. **Submit a pull request**

## 📄 License

This project is part of the MoonTide Conan Exiles server management suite.

## 🆘 Support

For issues and questions:
1. Check the documentation in each component directory
2. Review the test outputs for common problems
3. Check the troubleshooting sections in each README
4. Ensure all dependencies are properly installed

---

**"CROM does not coddle. The moon turns, the world hardens, and you either sharpen your blade or become bones under the sand."**

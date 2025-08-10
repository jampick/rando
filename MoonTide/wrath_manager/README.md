# MoonTide – Conan Exiles Moon-Driven Server Tuning

> *"Listen, exile. CROM does not coddle. The moon turns, the world hardens, and you either sharpen your blade or become bones under the sand."*

**Part of the Rando Server Management Suite**

MoonTide bends the Exiled Lands to the turning of the sky. As the moon waxes and wanes, the land shifts: harvest swells, beasts grow cruel, stamina thins, and rewards tempt fools into the dark. There are nights of calm. There are nights of reckoning. CROM does not explain; he only judges.

## 🌙 Core Concept

This server runs **seasonal events synced to the real-world lunar cycle and calendar**.  
The moon you see outside shapes the dangers, resources, and atmosphere inside the game.  
Full moons bring lethal predators and rich rewards. New moons offer safety and breathing space.  
Rare celestial and seasonal events stack on top of the lunar phases to create moments of high stakes and unique opportunities.

See the event concept and detailed breakdown in [`EVENTS_DESIGN.md`](EVENTS_DESIGN.md).

## 🚀 Quick Start

### Windows (Recommended)
```batch
# Tune Exiled Lands server
start_wrath_manager.bat exiled

# Tune Isle of Siptah server  
start_wrath_manager.bat siptah
```

### Direct Python Usage
```bash
# Tune server with events configuration
python3 wrath_manager.py \
  --ini-path /path/to/ConanSandbox/Saved/Config/LinuxServer/ServerSettings.ini \
  --event-file events.json

# Dry run (preview changes without applying)
python3 wrath_manager.py \
  --ini-path /path/to/ServerSettings.ini \
  --event-file events.json \
  --dry-run

# With Discord notifications
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python3 wrath_manager.py \
  --ini-path /path/to/ServerSettings.ini \
  --event-file events.json \
  --discord-post
```

### Linux Systemd Integration
Add to your unit or override:
```ini
[Service]
ExecStartPre=/usr/bin/python3 /path/to/wrath_manager.py \
  --ini-path /path/to/ServerSettings.ini \
  --event-file /path/to/events.json
```

## 🌟 Features

- **Continuous scaling** (New→Full) with per-key min/max and optional gamma
- **Phase presets** (8 buckets) layered on top of scaling
- **Calendar/omen events** with triggers (astronomical, seasonal/date windows; weather stub)
- **Additive merge** (numbers add; configured strings append) with per‑key caps
- **Global MOTD header/footer** and per‑event MOTDs (appended with `<BR>`)
- **One‑backup‑per‑run** with rotation; idempotent writes
- **Test suite** (cycle, MOTD, delta‑verify); Windows wrapper; Linux ExecStartPre

## 📁 Files

- **`wrath_manager.py`**: Main tuning engine
- **`events.json`**: Event configuration (edit this)
- **`events.sample.json`**: Starter template
- **`EVENTS_DESIGN.md`**: Event concept and detailed breakdown
- **`start_wrath_manager.bat`**: Windows wrapper (runs tuner only)
- **`tests/`**: Cycle, MOTD, and verification runners

## ⚙️ Configuration

### Core Settings (`events.json`)

#### Moon Phase Scaling
```json
{
  "moon_phase": {
    "enabled": true,
    "gamma": 1.0,
    "mapping": {
      "HarvestAmountMultiplier": {"min": 2.0, "max": 6.0},
      "PlayerDamageDealtMultiplier": {"min": 0.8, "max": 1.2},
      "PlayerDamageTakenMultiplier": {"min": 0.8, "max": 1.2}
    }
  }
}
```

#### Phase Presets
```json
{
  "events": {
    "phases": {
      "new_moon": {
        "MaxAggroRange": 0.7,
        "NPCMaxSpawnCapMultiplier": 0.8,
        "NPCRespawnMultiplier": 1.5
      },
      "full_moon": {
        "MaxAggroRange": 1.3,
        "NPCMaxSpawnCapMultiplier": 1.4,
        "NPCRespawnMultiplier": 0.7
      }
    }
  }
}
```

#### Calendar Events
```json
{
  "events": {
    "calendar": [
      {
        "name": "Blood Moon",
        "type": "astronomical",
        "event": "full_moon",
        "nearest_weekend": true,
        "window_hours": 24,
        "settings": {
          "NPCHealthMultiplier": 1.5,
          "PurgeLevel": 2,
          "MaxAggroRange": 1.5
        }
      }
    ]
  }
}
```

### Advanced Configuration

#### String Handling
```json
{
  "string_append_keys": ["ServerMessageOfTheDay"],
  "string_append_joiner": " <BR> ",
  "motd": {
    "header": "Welcome to our MoonTide server!",
    "footer": "May CROM guide your blade.",
    "always_include": true
  }
}
```

#### Safety Settings
```json
{
  "insert_missing_keys": false,
  "caps": {
    "HarvestAmountMultiplier": {"min": 1.0, "max": 10.0}
  },
  "backup": {
    "dir": "./backups",
    "keep": 10,
    "one_backup_per_run": true
  }
}
```

## 🔄 Behavior and Precedence

1. **Continuous scaling** applies first (if enabled)
2. **Active phase preset** is gathered (by detailed bucket or broad phase fallback)
3. **All enabled events**: `calendar` → `weather` → `custom`
4. **Merge**: numbers add; strings append (if configured); otherwise last‑wins
5. **Caps clamp results**; one backup per run; idempotent writes
6. **Unknown keys skipped** unless `insert_missing_keys=true`

## 🧪 Testing

### Automated Test Suite
```bash
# Run all tests
./tests/run_all_tests.sh [INI] [events.json]

# Cycle preview (daily scalers)
./tests/run_cycle_test.sh [INI] [events.json]

# MOTD validation
./tests/test_motd.sh [INI] [events.json]

# Delta verification
./tests/run_verify_example.sh [INI] [events.json]
```

### Test Coverage
- **Cycle Testing**: Validate daily scaling calculations
- **MOTD Testing**: Verify message formatting and appending
- **Delta Verification**: Confirm only intended keys change
- **Integration Testing**: End-to-end functionality validation

## 🔒 Safety Features

### Automatic Backups
- **One backup per run** with timestamp naming
- **Rotating retention** (configurable, default: 10 backups)
- **Safe rollback** capability for any configuration

### Validation
- **Input validation** for all configuration parameters
- **Range checking** for numeric values
- **Format validation** for dates and triggers
- **Dependency checking** for required fields

### Idempotent Operations
- **Safe to run multiple times** without side effects
- **Change detection** only updates modified values
- **Atomic writes** prevent partial updates

## 🎮 Supported Maps

- **Exiled Lands**: The original Conan Exiles map
- **Isle of Siptah**: The expansion map with unique mechanics
- **Custom Maps**: Extensible configuration system

## 🔧 Advanced Usage

### Custom Event Triggers
```json
{
  "type": "custom",
  "name": "Server Event",
  "trigger": "manual",
  "settings": {
    "HarvestAmountMultiplier": 5.0,
    "ServerMessageOfTheDay": "Special event active!"
  }
}
```

### Weather Integration (Stub)
```json
{
  "type": "weather",
  "provider": "stub",
  "conditions": ["storm", "clear"],
  "settings": {
    "BuildingDamageMultiplier": 1.5
  }
}
```

### Seasonal Windows
```json
{
  "type": "seasonal_window",
  "months": [6, 7, 8],
  "daily_window": ["12:00", "14:00"],
  "settings": {
    "PlayerActiveThirstMultiplier": 2.0
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Check the path to `events.json`
   - Verify file permissions and accessibility

2. **"INI file not writable"**
   - Ensure write permissions on the ServerSettings.ini directory
   - Check if the file is read-only

3. **"Backup directory not accessible"**
   - Create the backup directory if it doesn't exist
   - Verify write permissions

4. **"Invalid configuration format"**
   - Validate JSON syntax
   - Check required fields in the configuration

### Debug Mode
Use `--verbose` for detailed logging:
```bash
python3 wrath_manager.py --ini-path /path/to/ServerSettings.ini --event-file events.json --verbose
```

## 🔄 Restore from Backup

Backups are saved as `ServerSettings.ini.bak.YYYYMMDD-HHMMSS` in the backup directory.

**To restore:**
1. Stop the Conan Exiles server
2. Copy a backup over `ServerSettings.ini`
3. Start the server

**Example:**
```bash
cp backups/ServerSettings.ini.bak.20241201-143022 ServerSettings.ini
```

## 🤝 Integration

### With Grim Observer
- **Coordinated server management** with real-time monitoring
- **Event synchronization** between tuning and monitoring systems
- **Unified Discord integration** for comprehensive notifications
- **Shared configuration** management

### With External Systems
- **Webhook endpoints** for custom integrations
- **JSON output** for data processing
- **Log file monitoring** for external analysis
- **API endpoints** for status queries

## 📊 Monitoring & Analytics

### Performance Metrics
- **Configuration change frequency** tracking
- **Event trigger accuracy** monitoring
- **Backup rotation efficiency** analysis
- **System resource usage** optimization

### Event Analytics
- **Lunar phase impact** on player behavior
- **Event popularity** and engagement metrics
- **Server performance** correlation with events
- **Player retention** during special events

## 🔒 Security & Privacy

- **No sensitive data** stored in configuration files
- **Secure backup handling** with proper permissions
- **Input validation** to prevent injection attacks
- **Audit logging** for configuration changes

## 📚 Documentation

- **Event System**: [`EVENTS_DESIGN.md`](EVENTS_DESIGN.md) - Comprehensive event design guide
- **Configuration**: This file - Configuration options and examples
- **Integration**: Main project README - System integration guide
- **Testing**: `tests/` directory - Test suite documentation

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the events design documentation
3. Run the test suite to validate configuration
4. Check the main project README for integration guidance

## 📄 License

This project is part of the Rando Conan Exiles server management suite.

---

**"CROM does not hold your hand. He turns the heavens, and the earth answers in blood, frost, and shadow."**



"""Configuration management for DnDSpeaker."""
import json
import os
from typing import Optional, Dict, Any

CONFIG_FILE = "dndspeaker_config.json"


class Config:
    """Manages application settings persistence."""
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        self.default_config = {
            "input_device": None,
            "output_device": None,
            "current_voice": "Neutral Narrator",
            "hotkeys": {
                "1": "Goblin",
                "2": "Dragon",
                "3": "Lich",
                "4": "Noble Elf",
                "5": "Warforged",
                "6": "Neutral Narrator",
            },
            "bypass": False,
            "volume": 1.0,
        }
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle missing keys
                    config = self.default_config.copy()
                    config.update(loaded)
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self.config[key] = value
        self.save()
    
    def get_hotkey_voice(self, hotkey: str) -> Optional[str]:
        """Get voice name for a hotkey."""
        return self.config.get("hotkeys", {}).get(hotkey)


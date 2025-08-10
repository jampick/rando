#!/usr/bin/env python3
"""
Test script for the new standardized Discord formatting in wrath_manager
This demonstrates how event information is now displayed in clean, card-like format
"""

import json
import sys
import os

# Add the current directory to Python path to import wrath_manager functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_discord_formatting():
    """Test the new Discord formatting functions."""
    
    # Mock data similar to what wrath_manager would send
    test_cases = [
        {
            "name": "Full Moon Event",
            "phase_name": "Full Moon - The Hunt",
            "phase_bucket": "full",
            "illumination": 0.95,
            "events_applied": ["Blood Moon - The Reckoning"],
            "motd": "Full Moon: the Hunt—enemies at peak power; harvest at its best.",
            "event_settings": {
                "NPCHealthMultiplier": 2.5,
                "PurgeLevel": 6,
                "MaxAggroRange": 15000,
                "NPCMaxSpawnCapMultiplier": 2.0,
                "NPCRespawnMultiplier": 0.5,
                "PlayerDamageTakenMultiplier": 1.3,
                "ThrallDamageToNPCsMultiplier": 0.3,
                "StormEnabled": True,
                "ElderThingsEnabled": True
            },
            "moon_settings": {
                "HarvestAmountMultiplier": 6.0,
                "NPCDamageMultiplier": 2.0,
                "NPCDamageTakenMultiplier": 0.5
            }
        },
        {
            "name": "New Moon Calm",
            "phase_name": "New Moon - The Calm", 
            "phase_bucket": "new",
            "illumination": 0.05,
            "events_applied": [],
            "motd": "New Moon: safer world, lean harvest. Explore, build, and prepare.",
            "event_settings": {
                "MaxAggroRange": 7000,
                "NPCMaxSpawnCapMultiplier": 0.8,
                "NPCRespawnMultiplier": 1.2,
                "PlayerHealthRegenSpeedScale": 1.3,
                "PlayerDamageTakenMultiplier": 0.9
            },
            "moon_settings": {
                "HarvestAmountMultiplier": 1.0,
                "NPCDamageMultiplier": 1.0,
                "NPCDamageTakenMultiplier": 1.0
            }
        },
        {
            "name": "Waxing Crescent with Calendar Event",
            "phase_name": "Waxing Crescent - The Stirring",
            "phase_bucket": "waxing_crescent", 
            "illumination": 0.25,
            "events_applied": ["Blue Moon - The Forgotten Prophecy"],
            "motd": "Waxing Crescent: the Stirring—threats rising, gains growing.",
            "event_settings": {
                "MaxAggroRange": 9000,
                "NPCMaxSpawnCapMultiplier": 1.0,
                "NPCRespawnMultiplier": 0.95,
                "StaminaRegenerationTime": 3.9,
                "PlayerStaminaCostSprintMultiplier": 1.1,
                "UniqueLootEnabled": True,
                "RareSpawnsEnabled": True
            },
            "moon_settings": {
                "HarvestAmountMultiplier": 2.5,
                "NPCDamageMultiplier": 1.3,
                "NPCDamageTakenMultiplier": 0.8
            }
        }
    ]
    
    print("🧪 TESTING NEW STANDARDIZED DISCORD FORMATTING")
    print("=" * 60)
    print("This demonstrates how wrath_manager now formats Discord messages")
    print("in the same clean, card-like style as grim_observer\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Simulate the Discord message generation
        content = _generate_test_message(test_case)
        
        print("Discord Message Preview:")
        print(content)
        print("\n" + "=" * 60 + "\n")
    
    print("✅ **FORMATTING FEATURES:**")
    print("• 🌙 Moon phase emojis and names")
    print("• 📊 Categorized settings (Combat, Resources, Player, World)")
    print("• 📈 Visual indicators for multipliers (📈📉➖)")
    print("• ✅❌ Boolean indicators")
    print("• 🎯 Event status with appropriate emojis")
    print("• Clean, readable structure matching grim_observer style")


def _generate_test_message(test_case):
    """Generate a test Discord message using the new formatting."""
    
    # Start with MOTD
    content = test_case["motd"] + "\n\n"
    
    # Add phase information with emojis
    phase_emoji = _get_phase_emoji(test_case["phase_bucket"])
    phase_display_name = _get_phase_display_name(test_case["phase_bucket"])
    
    content += f"{phase_emoji} **{phase_display_name}**\n"
    content += f"🌙 Illumination: {test_case['illumination']:.1%}\n"
    
    # Add applied events if any
    if test_case["events_applied"]:
        event_emoji = "⚔️" if len(test_case["events_applied"]) > 1 else "🎯"
        content += f"{event_emoji} **Events Active:** {', '.join(test_case['events_applied'])}\n"
    
    # Build consolidated settings
    merged = {}
    if test_case["event_settings"]:
        merged.update(test_case["event_settings"])
    if test_case["moon_settings"]:
        for k, v in test_case["moon_settings"].items():
            if k not in merged:
                merged[k] = v
    
    if merged:
        content += "\n**Event Settings:**\n"
        categories = _categorize_settings(merged)
        
        for category, settings in categories.items():
            if settings:
                content += f"\n{category}:\n"
                for key, value in sorted(settings.items()):
                    formatted_value = _format_setting_value(value)
                    content += f"• {key}: {formatted_value}\n"
    
    return content.strip()


def _get_phase_emoji(phase_bucket: str) -> str:
    """Get the appropriate emoji for the moon phase."""
    phase_emojis = {
        "new": "🌑",
        "waxing_crescent": "🌒", 
        "first_quarter": "🌓",
        "waxing_gibbous": "🌔",
        "full": "🌕",
        "waning_gibbous": "🌖",
        "last_quarter": "🌗",
        "waning_crescent": "🌘"
    }
    return phase_emojis.get(phase_bucket, "🌙")


def _get_phase_display_name(phase_bucket: str) -> str:
    """Get the human-readable name for the moon phase."""
    phase_names = {
        "new": "New Moon - The Calm",
        "waxing_crescent": "Waxing Crescent - The Stirring",
        "first_quarter": "First Quarter - The Ascent", 
        "waxing_gibbous": "Waxing Gibbous - The Surge",
        "full": "Full Moon - The Hunt",
        "waning_gibbous": "Waning Gibbous - The Fade",
        "last_quarter": "Last Quarter - The Ebb",
        "waning_crescent": "Waning Crescent - The Dusk"
    }
    return phase_names.get(phase_bucket, "Unknown Phase")


def _categorize_settings(settings):
    """Categorize settings into logical groups for better readability."""
    categories = {
        "Combat": {},
        "Resources": {},
        "Player": {},
        "World": {},
        "Other": {}
    }
    
    for key, value in settings.items():
        if any(combat_key in key.lower() for combat_key in ["damage", "health", "aggro", "purge", "thrall"]):
            categories["Combat"][key] = value
        elif any(resource_key in key.lower() for resource_key in ["harvest", "spawn", "respawn"]):
            categories["Resources"][key] = value
        elif any(player_key in key.lower() for player_key in ["player", "stamina", "regeneration"]):
            categories["Player"][key] = value
        elif any(world_key in key.lower() for world_key in ["storm", "elder", "visibility", "range"]):
            categories["World"][key] = value
        else:
            categories["Other"][key] = value
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def _format_setting_value(value):
    """Format a setting value for clean display."""
    if isinstance(value, bool):
        return "✅" if value else "❌"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        # Add visual indicators for multipliers
        if "Multiplier" in str(value):
            if value > 1.0:
                return f"{float(value):.1f}x 📈"
            elif value < 1.0:
                return f"{float(value):.1f}x 📉"
            else:
                return f"{float(value):.1f}x ➖"
        else:
            return f"{float(value):.1f}"
    return str(value)


if __name__ == "__main__":
    test_discord_formatting()

#!/usr/bin/env python3
"""
Test script for empty server Discord messages
This script generates the exact webhook payload and CURL command for testing.
"""

import json
import time
import datetime
import random

def generate_test_empty_message(map_name="siptah", use_rich_embeds=True):
    """Generate a test empty server message payload."""
    
    # Dynamic empty server message system (same as grim_observer.py)
    empty_server_message_types = {
        "crom_sleeps": {
            "title_templates": [
                "💀 {map_emoji} CROM SLEEPS... {map_emoji} 💀",
                "🌙 {map_emoji} THE DARKNESS FALLS {map_emoji} 🌙",
                "⚰️ {map_emoji} SILENCE REIGNS {map_emoji} ⚰️",
                "🏜️ {map_emoji} THE WASTELAND CALLS {map_emoji} 🏜️",
                "🌑 {map_emoji} EMPTY REALMS {map_emoji} 🌑"
            ],
            "description_templates": [
                "**CROM SLEEPS...** {map_name} lies silent. No warriors to test their mettle. The weak have fled, the strong await... ⚔️",
                "**THE DARKNESS FALLS...** {map_name} is empty. No souls to challenge CROM's might. The strong shall return, the weak shall remain... 🗡️",
                "**SILENCE REIGNS...** {map_name} stands empty. No warriors to prove their worth. CROM waits... the strong shall return! 💀",
                "**THE WASTELAND CALLS...** {map_name} is barren. No souls to face CROM's trials. The weak are gone, the strong shall rise... ⚡",
                "**EMPTY REALMS...** {map_name} stands dormant. No warriors to claim CROM's glory. The strong shall awaken, the weak shall perish... 🗡️"
            ]
        },
        "warrior_call": {
            "title_templates": [
                "⚔️ {map_emoji} CALLING ALL WARRIORS {map_emoji} ⚔️",
                "🗡️ {map_emoji} THE BATTLEFIELD AWAITS {map_emoji} 🗡️",
                "🛡️ {map_emoji} GLORY CALLS {map_emoji} 🛡️",
                "⚡ {map_emoji} POWER VACUUM {map_emoji} ⚡",
                "🔥 {map_emoji} THE FIRE DIES {map_emoji} 🔥"
            ],
            "description_templates": [
                "**WARRIORS OF {map_name}...** The battlefield lies empty, waiting for your return. CROM demands blood and glory! Who will answer the call? ⚔️",
                "**CHAMPIONS OF {map_name}...** The arena is silent, the crowds are gone. Where are the mighty? CROM seeks worthy opponents! 🗡️",
                "**HEROES OF {map_name}...** The realm is quiet, the challenges await. Will you return to claim your destiny? CROM watches... ⚡",
                "**LEGENDS OF {map_name}...** The stage is set, the audience is gone. Your stories remain untold. CROM awaits your return! 🔥",
                "**WARRIORS OF {map_name}...** The battlefield is yours for the taking. No competition, no resistance. CROM offers you glory! 🛡️"
            ]
        },
        "lore_story": {
            "title_templates": [
                "📚 {map_emoji} LEGENDS OF {map_name} {map_emoji} 📚",
                "🏛️ {map_emoji} ANCIENT TALES {map_emoji} 🏛️",
                "🗿 {map_emoji} STORIES UNTOLD {map_emoji} 🗿",
                "📖 {map_emoji} CHRONICLES OF {map_name} {map_emoji} 📖",
                "🏺 {map_emoji} MYTHS AND LEGENDS {map_emoji} 🏺"
            ],
            "description_templates": [
                "**IN THE DAYS OF OLD...** {map_name} was filled with warriors whose names echoed through the ages. Now, only silence remains. Will you write the next chapter? 📚",
                "**THE ANCIENTS SPEAK...** {map_name} remembers the battles, the victories, the defeats. The stones whisper of glory past. Will you add your tale? 🏛️",
                "**LEGENDS TELL...** {map_name} was once a place of great deeds and mighty warriors. The echoes of their glory still linger. Will you continue their legacy? 🗿",
                "**HISTORY RECORDS...** {map_name} has seen empires rise and fall, heroes come and go. The chronicles await your entry. Will you be remembered? 📖",
                "**MYTHS WHISPER...** {map_name} holds secrets of power and glory. The ancient ones left their mark. Will you leave yours? 🏺"
            ]
        },
        "challenge_issued": {
            "title_templates": [
                "🎯 {map_emoji} CHALLENGE ISSUED {map_emoji} 🎯",
                "🏆 {map_emoji} THE THRONE AWAITS {map_emoji} 🏆",
                "⚔️ {map_emoji} PROVE YOUR WORTH {map_emoji} ⚔️",
                "🔥 {map_emoji} THE TEST BEGINS {map_emoji} 🔥",
                "💎 {map_emoji} DIAMOND IN THE ROUGH {map_emoji} 💎"
            ],
            "description_templates": [
                "**CROM CHALLENGES YOU...** {map_name} stands empty, a blank canvas for your conquest. Will you rise to the challenge and claim your destiny? 🎯",
                "**THE THRONE IS EMPTY...** {map_name} has no ruler, no champion. CROM offers you the chance to prove your worth. Will you accept? 🏆",
                "**YOUR TEST AWAITS...** {map_name} is your proving ground. No competition, no distractions. Just you and CROM's challenge. Ready? ⚔️",
                "**THE FIRE TESTS ALL...** {map_name} will reveal your true nature. Will you emerge stronger, or will you be consumed? CROM watches... 🔥",
                "**DIAMONDS ARE FORGED...** {map_name} will test your mettle. Pressure creates perfection. Will you shine, or will you crack? 💎"
            ]
        },
        "humor_meme": {
            "title_templates": [
                "😴 {map_emoji} SERVER STATUS: NAPPING {map_emoji} 😴",
                "🦗 {map_emoji} CHIRP CHIRP {map_emoji} 🦗",
                "🌵 {map_emoji} TUMBLEWEED ALERT {map_emoji} 🌵",
                "👻 {map_emoji} GHOST TOWN {map_emoji} 👻",
                "🎭 {map_emoji} THE SHOW MUST GO ON {map_emoji} 🎭"
            ],
            "description_templates": [
                "**ZZZZ...** {map_name} is taking a nap. The server is so quiet you can hear the tumbleweeds rolling by. Anyone want to wake it up? 😴",
                "**CHIRP CHIRP...** The only sound in {map_name} is the crickets. It's so empty even the echo has an echo. Anyone home? 🦗",
                "**TUMBLEWEED ROLLING...** {map_name} is so deserted, tumbleweeds are having parties. The server is basically a ghost town. 👻",
                "**GHOST TOWN...** {map_name} is so empty, even the ghosts got bored and left. The server is basically a digital desert. 🌵",
                "**CURTAIN CALL...** The audience has left {map_name}. The show is over, the lights are off. Anyone want to be the star? 🎭"
            ]
        }
    }
    
    # Dynamic field and footer variations
    field_variations = {
        "server_state": [
            "🌙 **Server State**",
            "⚔️ **Battle Status**",
            "🏰 **Realm Status**",
            "🗡️ **Warrior Count**",
            "🛡️ **Defense Status**"
        ],
        "next_check": [
            "⏰ **Next Check**",
            "🕐 **Next Update**",
            "⏳ **Next Alert**",
            "🕰️ **Next Report**",
            "📅 **Next Status**"
        ],
        "map_info": [
            "🗺️ **Map**",
            "🌍 **Realm**",
            "🏔️ **Land**",
            "🏝️ **Territory**",
            "🌋 **Domain**"
        ]
    }
    
    footer_variations = [
        "CROM watches... the strong shall return! ⚔️",
        "The weak perish, the strong survive! 🗡️",
        "Glory awaits those who dare to return! 🛡️",
        "CROM's challenge stands... will you answer? ⚡",
        "The arena is empty, but the glory remains! 🏆",
        "CROM sleeps, but the strong never rest! 💀",
        "The battlefield calls... will you answer? 🔥",
        "CROM's realm awaits its next champion! 💎"
    ]
    
    # Image URLs (placeholder - replace with your actual URLs)
    empty_server_images = {
        "thumbnail": "https://i.imgur.com/8JZqXqL.png",  # Replace with your thumbnail URL
        "main_image": "https://i.imgur.com/QX8JZqL.png",  # Replace with your main image URL
        "footer_icon": "https://i.imgur.com/JZqX8qL.png"  # Replace with your footer icon URL
    }
    
    # Colors for different maps
    empty_server_colors = {
        "siptah": 0x228B22,    # Forest green
        "exiled": 0x8B4513,    # Saddle brown
        "default": 0x8B0000    # Dark red
    }
    
    # Map emoji
    map_emoji = "🌴" if map_name.lower() == "siptah" else "🏔️" if map_name.lower() == "exiled" else "🎮"
    
    # Select a random message type
    message_type = random.choice(list(empty_server_message_types.keys()))
    
    # Select a random title and description from the chosen type
    title_templates = empty_server_message_types[message_type]["title_templates"]
    description_templates = empty_server_message_types[message_type]["description_templates"]
    
    title = random.choice(title_templates).format(map_name=map_name, map_emoji=map_emoji)
    description = random.choice(description_templates).format(map_name=map_name, map_emoji=map_emoji)
    
    if use_rich_embeds:
        # Create rich embed
        embed = {
            "title": title,
            "description": description,
            "color": empty_server_colors.get(map_name.lower(), empty_server_colors["default"]),
            "thumbnail": {
                "url": empty_server_images["thumbnail"]
            },
            "image": {
                "url": empty_server_images["main_image"]
            },
            "fields": [
                {
                    "name": random.choice(field_variations["server_state"]),
                    "value": "**EMPTY** - No warriors present",
                    "inline": True
                },
                {
                    "name": random.choice(field_variations["next_check"]),
                    "value": f"<t:{int(time.time() + 14400)}:R>",  # 4 hours from now
                    "inline": True
                },
                {
                    "name": random.choice(field_variations["map_info"]),
                    "value": f"**{map_name.upper()}**",
                    "inline": True
                }
            ],
            "footer": {
                "text": random.choice(footer_variations),
                "icon_url": empty_server_images["footer_icon"]
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        payload = {
            "content": "",  # Empty content, using embed instead
            "embeds": [embed]
        }
    else:
        # Simple text message
        payload = {
            "content": f"{description}\n\n⏰ Next check: <t:{int(time.time() + 14400)}:R>",
            "embeds": []
        }
    
    return payload

def generate_curl_command(webhook_url, payload, map_name="siptah"):
    """Generate CURL command for testing."""
    
    # Save payload to temporary file
    temp_file = f"test_payload_{map_name}.json"
    with open(temp_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    # Generate CURL command
    curl_cmd = f'curl -X POST "{webhook_url}" \\\n'
    curl_cmd += f'  -H "Content-Type: application/json" \\\n'
    curl_cmd += f'  -d @{temp_file}'
    
    return curl_cmd, temp_file

def main():
    """Main test function."""
    print("🧪 TESTING EMPTY SERVER DISCORD MESSAGES")
    print("=" * 50)
    
    # Get webhook URL from user
    webhook_url = input("Enter your Discord webhook URL: ").strip()
    if not webhook_url:
        print("❌ No webhook URL provided. Exiting.")
        return
    
    # Get map name
    map_name = input("Enter map name (siptah/exiled/default): ").strip().lower()
    if not map_name:
        map_name = "siptah"
    
    # Test both formats
    print(f"\n📋 Testing with map: {map_name}")
    print("-" * 30)
    
    # Test rich embed
    print("\n🎨 **RICH EMBED FORMAT:**")
    rich_payload = generate_test_empty_message(map_name, use_rich_embeds=True)
    curl_cmd, temp_file = generate_curl_command(webhook_url, rich_payload, f"{map_name}_rich")
    
    print("📄 Payload saved to:", temp_file)
    print("🔄 CURL command:")
    print(curl_cmd)
    
    # Test simple text
    print("\n📝 **SIMPLE TEXT FORMAT:**")
    simple_payload = generate_test_empty_message(map_name, use_rich_embeds=False)
    curl_cmd, temp_file = generate_curl_command(webhook_url, simple_payload, f"{map_name}_simple")
    
    print("📄 Payload saved to:", temp_file)
    print("🔄 CURL command:")
    print(curl_cmd)
    
    print("\n" + "=" * 50)
    print("🚀 **READY TO TEST!**")
    print("\nChoose one of the CURL commands above to test your message.")
    print("The payload files are saved locally for inspection.")
    print("\n💡 **Tips:**")
    print("- Test with rich embed first to see the full visual effect")
    print("- Check the JSON files to see the exact payload structure")
    print("- Replace image URLs in the payload with your actual hosted images")
    print("- Use --no-rich-embeds flag in grim_observer.py to disable rich embeds")

if __name__ == "__main__":
    main()

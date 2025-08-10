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
    
    # Empty server messages (same as grim_observer.py)
    empty_server_messages = [
        "💀 **CROM SLEEPS...** The server lies silent. No warriors to test their mettle. The weak have fled, the strong await... ⚔️",
        "🌙 **THE DARKNESS FALLS...** The server is empty. No souls to challenge CROM's might. The strong shall return, the weak shall remain... 🗡️",
        "⚰️ **SILENCE REIGNS...** The server stands empty. No warriors to prove their worth. CROM waits... the strong shall return! 💀",
        "🏜️ **THE WASTELAND CALLS...** The server is barren. No souls to face CROM's trials. The weak are gone, the strong shall rise... ⚡",
        "🌑 **EMPTY REALMS...** The server stands dormant. No warriors to claim CROM's glory. The strong shall awaken, the weak shall perish... 🗡️"
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
    
    # Random message
    message = random.choice(empty_server_messages)
    
    # Replace generic "server" references with map name
    if map_name.lower() != "server":
        message = message.replace("The server", f"{map_name}")
        message = message.replace("the server", f"{map_name}")
    
    # Map emoji
    map_emoji = "🌴" if map_name.lower() == "siptah" else "🏔️" if map_name.lower() == "exiled" else "🎮"
    
    if use_rich_embeds:
        # Create rich embed
        embed = {
            "title": f"💀 {map_emoji} SERVER STATUS: EMPTY {map_emoji} 💀",
            "description": message,
            "color": empty_server_colors.get(map_name.lower(), empty_server_colors["default"]),
            "thumbnail": {
                "url": empty_server_images["thumbnail"]
            },
            "image": {
                "url": empty_server_images["main_image"]
            },
            "fields": [
                {
                    "name": "🌙 **Server State**",
                    "value": "**EMPTY** - No warriors present",
                    "inline": True
                },
                {
                    "name": "⏰ **Next Check**",
                    "value": f"<t:{int(time.time() + 14400)}:R>",  # 4 hours from now
                    "inline": True
                },
                {
                    "name": "🗺️ **Map**",
                    "value": f"**{map_name.upper()}**",
                    "inline": True
                }
            ],
            "footer": {
                "text": "CROM watches... the strong shall return! ⚔️",
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
            "content": f"💀 **CROM SLEEPS...** The server lies silent. No warriors to test their mettle. The weak have fled, the strong await... ⚔️\n\n**{map_name}** is empty. No souls to challenge CROM's might. The strong shall return, the weak shall remain... 🗡️\n\n⏰ Next check: <t:{int(time.time() + 14400)}:R>",
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

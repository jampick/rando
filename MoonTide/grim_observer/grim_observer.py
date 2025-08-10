#!/usr/bin/env python3
"""
Grim Observer - Conan Exiles Log Monitor
Monitors Conan Exiles server logs and emits events for Discord webhooks.

Features:
- Monitors log files for player connection/disconnection events
- Generates Discord webhook payloads
- Supports multiple output formats (JSON, CSV)
- Configurable event patterns and intervals
- Map-specific configuration support

Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import logging
import random # Added for peak milestone messages

# Version information
__version__ = "1.0.0"
__version_date__ = "2025-08-09"

# Try to import requests, fall back to urllib if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    import urllib.request
    import urllib.parse

# Log library availability
if REQUESTS_AVAILABLE:
    print("[GrimObserver][INFO] Using requests library for HTTP requests (recommended)")
else:
    print("[GrimObserver][WARN] requests library not available, falling back to urllib")
    print("[GrimObserver][INFO] Install requests with: pip install requests")


class LogEvent:
    """Represents a parsed log event."""
    
    def __init__(self, timestamp: str, event_type: str, player_name: str = None, 
                 ip_address: str = None, player_id: str = None, raw_line: str = ""):
        self.timestamp = timestamp
        self.event_type = event_type
        self.player_name = player_name
        self.ip_address = ip_address
        self.player_id = player_id
        self.raw_line = raw_line
        self.parsed_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'player_name': self.player_name,
            'ip_address': self.ip_address,
            'player_id': self.player_id,
            'raw_line': self.raw_line,
            'parsed_at': self.parsed_at
        }
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.event_type}: {self.player_name or 'N/A'}"


class ConanLogParser:
    """Parses ConanSandbox log entries for player events."""
    
    def __init__(self):
        # Regex patterns for different log entry types
        self.patterns = {
            'player_connected': re.compile(
                r'BattlEyeServer: Print Message: Player #(\d+) (\S+) \((\S+):(\d+)\) connected'
            ),
            'player_disconnected_battleye': re.compile(
                r'BattlEyeServer: Print Message: Player #(\d+) (\S+) disconnected'
            ),
            'player_disconnected_lognet': re.compile(
                r'LogNet: Player disconnected: (\S+)'
            ),
            'timestamp': re.compile(r'\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\]')
        }
    
    def parse_line(self, line: str) -> Optional[LogEvent]:
        """Parse a single log line and return a LogEvent if it matches known patterns."""
        if not line.strip():
            return None
        
        # Extract timestamp
        timestamp_match = self.patterns['timestamp'].search(line)
        if not timestamp_match:
            return None
        
        timestamp = timestamp_match.group(1)
        
        # Check for player connection
        conn_match = self.patterns['player_connected'].search(line)
        if conn_match:
            player_id = conn_match.group(1)
            player_name = conn_match.group(2)
            ip_address = conn_match.group(3)
            return LogEvent(
                timestamp=timestamp,
                event_type='player_connected',
                player_name=player_name,
                ip_address=ip_address,
                player_id=player_id,
                raw_line=line.strip()
            )
        
        # Check for player disconnection (BattlEye)
        disc_battleye_match = self.patterns['player_disconnected_battleye'].search(line)
        if disc_battleye_match:
            player_id = disc_battleye_match.group(1)
            player_name = disc_battleye_match.group(2)
            return LogEvent(
                timestamp=timestamp,
                event_type='player_disconnected',
                player_name=player_name,
                player_id=player_id,
                raw_line=line.strip()
            )
        
        # Check for player disconnection (LogNet)
        disc_lognet_match = self.patterns['player_disconnected_lognet'].search(line)
        if disc_lognet_match:
            player_name = disc_lognet_match.group(1)
            
            # Filter out player names with hash followed by numbers (e.g., Sweetbread#26947)
            if re.search(r'#\d+$', player_name):
                return None
            
            return LogEvent(
                timestamp=timestamp,
                event_type='player_disconnected',
                player_name=player_name,
                raw_line=line.strip()
            )
        
        return None


class GrimObserver:
    """
    Main class for monitoring Conan Exiles server logs and sending Discord notifications.
    """
    
    def __init__(self, log_file_path: str, output_file: str = None, verbose: bool = False, discord_webhook_url: str = None, force_curl: bool = False, map_name: str = None):
        """
        Initialize Grim Observer with log file path and optional Discord webhook.
        
        Args:
            log_file_path: Path to the Conan Exiles log file
            output_file: Path to save parsed events (optional)
            verbose: Enable verbose logging
            discord_webhook_url: Discord webhook URL for notifications
            force_curl: Force use of curl for webhook sending
            map_name: Map name for map-specific configurations
        """
        # ============================================================================
        # 🖼️ CUSTOM IMAGE CONFIGURATION
        # ============================================================================
        # 
        # ⚠️  IMPORTANT: Replace these placeholder URLs with your custom images!
        # 
        # To customize your Discord embeds, update the URLs below:
        # 
        # Option 1: Simple replacement (recommended for most users)
        # Replace the URLs in 'empty_server_image_options' below with your image URLs
        # 
        # Option 2: Map-specific customization
        # You can create different images for different maps by modifying the arrays
        # 
        # Option 3: Command-line override
        # Use --thumbnail-url, --main-image-url, --footer-icon-url when running
        # 
        # Image Requirements:
        # - Format: PNG (transparent background support)
        # - Thumbnail: 96x96px
        # - Main Image: 400x300px max  
        # - Footer Icon: 16x16px
        # - Access: Must be publicly accessible via HTTPS
        # - Size: Under 8MB for Discord compatibility
        #
        # Example custom URLs:
        # "https://your-domain.com/your-server-logo.png"
        # "https://imgur.com/your-image-id.png"
        # "https://cdn.discordapp.com/attachments/your-image.png"
        # ============================================================================
        
        # Version information
        self.version = "1.0.0"
        self.version_date = "2025-08-09"
        
        # Core configuration
        self.log_file_path = log_file_path
        self.output_file = output_file
        self.verbose = verbose
        self.discord_webhook_url = discord_webhook_url
        self.force_curl = force_curl
        self.map_name = map_name
        
        # Initialize state
        self.events = []
        self.players_online = set()
        self.peak_players = 0
        self.peak_timestamp = None
        self.milestone_thresholds = [5, 10, 25, 50, 100]
        self.reached_milestones = set()
        self.last_empty_server_message = None
        self.empty_server_message_interval = 4 * 60 * 60  # 4 hours in seconds
        self.last_message_type = None  # Track last message type for variety
        self.running = False
        self.use_rich_embeds = True  # Enable rich embeds by default
        
        # ============================================================================
        # 🖼️ UPDATE THESE URLs WITH YOUR CUSTOM IMAGES
        # ============================================================================
        
        # Multiple image options for randomization
        self.empty_server_image_options = {
            "thumbnail": [
                # ⚠️  REPLACE THESE PLACEHOLDER URLs WITH YOUR CUSTOM IMAGES
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/thumbnail.png",
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/thumbnail_siptah.png",
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/thumbnail_exiled.png"
                # 
                # 🎨  EXAMPLE CUSTOM URLs (uncomment and replace with your images):
                # "https://your-domain.com/your-server-logo.png",
                # "https://imgur.com/your-thumbnail.png",
                # "https://cdn.discordapp.com/attachments/your-thumbnail.png"
            ],
            "main_image": [
                # ⚠️  REPLACE THESE PLACEHOLDER URLs WITH YOUR CUSTOM IMAGES
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/main_image.png",
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/main_image_siptah.png",
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/main_image_exiled.png"
                # 
                # 🎨  EXAMPLE CUSTOM URLs (uncomment and replace with your images):
                # "https://your-domain.com/your-server-banner.png",
                # "https://imgur.com/your-main-image.png",
                # "https://cdn.discordapp.com/attachments/your-main-image.png"
            ],
            "footer_icon": [
                # ⚠️  REPLACE THIS PLACEHOLDER URL WITH YOUR CUSTOM IMAGE
                "https://raw.githubusercontent.com/jampick/rando/main/MoonTide/grim_observer/placeholder_images/footer_icon.png"
                # 
                # 🎨  EXAMPLE CUSTOM URL (uncomment and replace with your image):
                # "https://your-domain.com/your-footer-icon.png"
            ]
        }
        
        # ============================================================================
        # 🎯  QUICK CUSTOMIZATION: For simple setup, just replace the URLs above
        # ============================================================================
        # 
        # If you want to quickly customize without complex configuration:
        # 1. Upload your images to Imgur, Discord, or your own server
        # 2. Replace the placeholder URLs above with your image URLs
        # 3. Keep the same structure (arrays for multiple options)
        # 4. Save the file and restart Grim Observer
        #
        # Your custom images will now be used automatically!
        # ============================================================================
        
        # Current selected images (will be randomized)
        self.empty_server_images = {
            "thumbnail": self.empty_server_image_options["thumbnail"][0],
            "main_image": self.empty_server_image_options["main_image"][0],
            "footer_icon": self.empty_server_image_options["footer_icon"][0]
        }
        self.empty_server_colors = {
            "siptah": 0x228B22,    # Forest green
            "exiled": 0x8B4513,    # Saddle brown
            "default": 0x8B0000    # Dark red
        }
        
        # Dynamic field and footer variations
        self.empty_server_field_variations = {
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
        
        self.empty_server_footer_variations = [
            "CROM watches... the strong shall return! ⚔️",
            "The weak perish, the strong survive! 🗡️",
            "Glory awaits those who dare to return! 🛡️",
            "CROM's challenge stands... will you answer? ⚡",
            "The arena is empty, but the glory remains! 🏆",
            "CROM sleeps, but the strong never rest! 💀",
            "The battlefield calls... will you answer? 🔥",
            "CROM's realm awaits its next champion! 💎"
        ]
        
        # Seasonal and time-based variations
        self.seasonal_variations = {
            "morning": ["🌅", "🌞", "☀️"],
            "afternoon": ["🌤️", "☀️", "🌞"],
            "evening": ["🌆", "🌅", "🌇"],
            "night": ["🌙", "🌃", "⭐"],
            "weekend": ["🎉", "🎊", "🎈"],
            "weekday": ["💼", "📅", "⏰"]
        }
        
        # Empty server message types and variations
        self.empty_server_message_types = {
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
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Create map-specific log file if no output file specified
        if not self.output_file:
            map_suffix = f".{self.map_name}" if self.map_name else ".unknown"
            self.output_file = Path(f"grim_events{map_suffix}.json")
        
        # Setup logging with map-specific log file
        self._setup_logging()
        
        # Initialize parser and state
        self.parser = ConanLogParser()
        self.current_position = 0
        
        # Log version information
        self.logger.info(f"Grim Observer v{self.version} ({self.version_date}) initialized")
        self.logger.info(f"Log file: {self.log_file_path}")
        self.logger.info(f"Output file: {self.output_file}")
        if self.discord_webhook_url:
            self.logger.info(f"Discord webhook configured: {self.discord_webhook_url[:50]}...")
        if self.map_name:
            self.logger.info(f"Map: {self.map_name}")
    
    def _setup_logging(self):
        """Setup logging with map-specific log file."""
        # Create map-specific log file name
        if self.map_name:
            log_filename = f"grim_observer.{self.map_name}.log"
        else:
            log_filename = "grim_observer.unknown.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stderr)
            ]
        )
        
        # Validate log file
        log_path = Path(self.log_file_path)
        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

    def setup_logging(self):
        """Legacy method - now calls _setup_logging."""
        self._setup_logging()
        
    def get_current_position(self) -> int:
        """Get current position in the log file."""
        try:
            log_path = Path(self.log_file_path)
            return log_path.stat().st_size
        except OSError:
            return 0
    
    def read_new_lines(self) -> List[str]:
        """Read new lines from the log file since last check."""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(self.current_position)
                new_lines = f.readlines()
                self.current_position = f.tell()
                return new_lines
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            return []
    
    def process_line(self, line: str):
        """Process a single log line."""
        event = self.parser.parse_line(line)
        if event:
            self.events.append(event)
            self.logger.info(f"Event detected: {event}")
            
            # Send Discord webhook for new events if webhook URL is available
            if self.discord_webhook_url and event.event_type in ['player_connected', 'player_disconnected']:
                # Generate and send Discord webhook for this single event
                payloads = self.generate_discord_webhook_payloads([event])
                
                if payloads:
                    success = self.send_discord_webhook(payloads[0])
                    if success:
                        self.logger.info(f"Discord webhook sent successfully for {event.event_type}")
                    else:
                        self.logger.error(f"Failed to send Discord webhook for {event.event_type}")
                else:
                    self.logger.warning(f"No payloads generated for event: {event.event_type}")
                
                # Check for peak milestones after player connections
                if event.event_type == 'player_connected' and self.discord_webhook_url:
                    current_players = self.get_player_count()
                    peak_message = self._check_peak_milestone(current_players)
                    if peak_message:
                        self.logger.info(f"Peak milestone reached: {current_players} players")
                        success = self.send_discord_webhook(peak_message)
                        if success:
                            self.logger.info(f"Peak milestone message sent successfully")
                        else:
                            self.logger.error(f"Failed to send peak milestone message")
                
                # Check if server went empty after disconnections
                elif event.event_type == 'player_disconnected' and self.discord_webhook_url:
                    current_players = self.get_player_count()
                    if current_players == 0:
                        self._reset_peak_tracking()
                        empty_message = self._check_empty_server_message(current_players)
                        if empty_message:
                            self.logger.info(f"Empty server message sent: {current_players} players")
                            success = self.send_discord_webhook(empty_message)
                            if success:
                                self.logger.info(f"Empty server message sent successfully")
                            else:
                                self.logger.error(f"Failed to send empty server message")
            else:
                # Discord webhook conditions not met - no logging needed
                pass
            
            # Save to output file if specified
            if self.output_file:
                self.save_event(event)
    
    def save_event(self, event: LogEvent):
        """Save event to output file."""
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                json.dump(event.to_dict(), f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Error saving event: {e}")
    
    def scan_entire_log(self) -> List[LogEvent]:
        """Scan the entire log file and return all events."""
        self.logger.info(f"Scanning entire log file: {self.log_file_path}")
        events = []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = 0
                for line_num, line in enumerate(f, 1):
                    total_lines += 1
                    
                    # Show progress every 1000 lines
                    if line_num % 1000 == 0:
                        self.logger.info(f"Processed {line_num} lines...")
                    
                    event = self.parser.parse_line(line)
                    if event:
                        events.append(event)
                        if self.verbose:
                            self.logger.info(f"Line {line_num}: {event}")
            
            self.logger.info(f"Scan completed. Total lines: {total_lines}, Events found: {len(events)}")
            return events
            
        except Exception as e:
            self.logger.error(f"Error scanning log file: {e}")
            return []
    
    def generate_discord_webhook_payloads(self, events: List[LogEvent] = None) -> List[Dict]:
        """Generate Discord webhook payloads for events."""
        if events is None:
            events = self.events
        
        payloads = []
        
        # Get map name for title (default to "Server" if not specified)
        map_name = self.map_name or "Server"
        map_emoji = "🌴" if map_name.lower() == "siptah" else "🏔️" if map_name.lower() == "exiled" else "🎮"
        
        for event in events:
            if event.event_type == 'player_connected':
                # Get current player count for enhanced info
                # The current event is already in self.events, so get_player_count() includes it
                current_players = self.get_player_count()
                
                payload = {
                    "content": f"🟢 **{event.player_name}** joined {map_name}\n⏰ {event.timestamp} • 👥 Player #{current_players}",
                    "embeds": []  # No embeds for cleaner look
                }
                payloads.append(payload)
                
            elif event.event_type == 'player_disconnected':
                # Calculate session duration if we have connection time
                session_duration = self._get_session_duration(event.player_name)
                duration_text = f"⏱️ Session: {session_duration}" if session_duration else ""
                
                payload = {
                    "content": f"🔴 **{event.player_name}** left {map_name}\n⏰ {event.timestamp} • {duration_text}",
                    "embeds": []  # No embeds for cleaner look
                }
                payloads.append(payload)
        
        return payloads
    
    def send_discord_webhook(self, payload: Dict) -> bool:
        """Send a Discord webhook payload using CURL as primary method.
        
        Args:
            payload: The Discord webhook payload to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.discord_webhook_url:
            self.logger.warning("No Discord webhook URL configured")
            return False
        
        # Log webhook execution
        self.logger.info(f"Discord webhook execution started")
        
        try:
            if self.force_curl:
                # Force CURL usage only
                return self._send_with_curl(payload)
            
            # Try CURL first (since it works manually)
            if self._send_with_curl(payload):
                return True
            
            # Fallback to Python libraries if CURL fails
            self.logger.info("CURL method failed, trying Python libraries...")
            
            if REQUESTS_AVAILABLE:
                return self._send_with_requests(payload)
            else:
                return self._send_with_urllib(payload)
                    
        except Exception as e:
            self.logger.error(f"Error sending Discord webhook: {e}")
            self.logger.error(f"[DEBUG] Exception type: {type(e).__name__}")
            self.logger.error(f"[DEBUG] Exception details: {str(e)}")
            return False
    
    def _send_with_curl(self, payload: Dict) -> bool:
        """Send Discord webhook using CURL command."""
        try:
            import subprocess
            import tempfile
            import os
            
            # Convert payload to JSON string
            json_data = json.dumps(payload, ensure_ascii=False)
            
            # Create temporary file for JSON data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(json_data)
                temp_file_path = temp_file.name
            
            try:
                # Build CURL command
                curl_cmd = [
                    'curl', '-s', '-w', '%{http_code}',  # Silent mode, return HTTP status code
                    '-X', 'POST',
                    '-H', 'Content-Type: application/json',
                    '-d', f'@{temp_file_path}',  # Read data from file
                    self.discord_webhook_url
                ]
                
                # Execute CURL command
                result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                # Parse response
                if result.returncode == 0:
                    # CURL succeeded, check HTTP status code
                    try:
                        http_status = int(result.stdout.strip())
                        if http_status == 204:  # Discord returns 204 on success
                            self.logger.info(f"CURL Discord webhook sent successfully: {payload.get('content', 'No content')}")
                            return True
                        else:
                            self.logger.error(f"CURL Discord webhook failed with status {http_status}")
                            self.logger.error(f"[DEBUG] CURL stderr: {result.stderr}")
                            return False
                    except ValueError:
                        self.logger.error(f"CURL returned invalid status code: {result.stdout}")
                        return False
                else:
                    self.logger.error(f"CURL command failed with return code {result.returncode}")
                    self.logger.error(f"[DEBUG] CURL stderr: {result.stderr}")
                    return False
                    
            except Exception as e:
                # Clean up temp file on any error
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                raise e
                
        except Exception as e:
            self.logger.error(f"Error in CURL method: {e}")
            return False
    
    def _send_with_requests(self, payload: Dict) -> bool:
        """Send Discord webhook using requests library."""
        try:
            # Convert payload to JSON
            data = json.dumps(payload)
            self.logger.info(f"[DEBUG] Requests method: JSON data length: {len(data)} bytes")
            self.logger.info(f"[DEBUG] Requests method: JSON data (first 200 chars): {data[:200]}")
            
            # Send request using requests library
            headers = {'Content-Type': 'application/json'}
            self.logger.info(f"[DEBUG] Requests method: Request method: POST")
            self.logger.info(f"[DEBUG] Requests method: Request headers: {headers}")
            self.logger.info(f"[DEBUG] Requests method: Request data length: {len(data)}")
            
            self.logger.info(f"[DEBUG] Requests method: About to send HTTP request to Discord...")
            response = requests.post(
                self.discord_webhook_url,
                json=payload,  # Use json parameter for automatic JSON encoding
                headers=headers
            )
            
            self.logger.info(f"[DEBUG] Requests method: HTTP response received")
            self.logger.info(f"[DEBUG] Requests method: Response status: {response.status_code}")
            self.logger.info(f"[DEBUG] Requests method: Response headers: {dict(response.headers)}")
            
            if response.status_code == 204:  # Discord returns 204 on success
                self.logger.info(f"Requests Discord webhook sent successfully: {payload.get('content', 'No content')}")
                return True
            else:
                self.logger.error(f"Requests Discord webhook failed with status {response.status_code}")
                self.logger.error(f"[DEBUG] Requests method: Response content: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in requests method: {e}")
            return False
    
    def _send_with_urllib(self, payload: Dict) -> bool:
        """Send Discord webhook using urllib library."""
        try:
            # Convert payload to JSON
            data = json.dumps(payload).encode('utf-8')
            self.logger.info(f"[DEBUG] Urllib method: JSON data length: {len(data)} bytes")
            self.logger.info(f"[DEBUG] Urllib method: JSON data (first 200 chars): {data[:200]}")
            
            # Create request
            req = urllib.request.Request(
                self.discord_webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            self.logger.info(f"[DEBUG] Urllib method: Request method: {req.get_method()}")
            self.logger.info(f"[DEBUG] Urllib method: Request headers: {dict(req.headers)}")
            self.logger.info(f"[DEBUG] Urllib method: Request data length: {len(req.data) if req.data else 0}")
            
            # Send request
            self.logger.info(f"[DEBUG] Urllib method: About to send HTTP request to Discord...")
            with urllib.request.urlopen(req) as response:
                self.logger.info(f"[DEBUG] Urllib method: HTTP response received")
                self.logger.info(f"[DEBUG] Urllib method: Response status: {response.status}")
                self.logger.info(f"[DEBUG] Urllib method: Response headers: {dict(response.headers)}")
                
                if response.status == 204:  # Discord returns 204 on success
                    self.logger.info(f"Urllib Discord webhook sent successfully: {payload.get('content', 'No content')}")
                    return True
                else:
                    self.logger.error(f"Urllib Discord webhook failed with status {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error in urllib method: {e}")
            return False

    def emit_discord_webhook_events(self, events: List[LogEvent] = None):
        """Emit events in Discord webhook format."""
        if events is None:
            events = self.events
        
        if not events:
            print("No events to emit.")
            return
        
        # Generate Discord webhook payloads
        payloads = self.generate_discord_webhook_payloads(events)
        
        print(f"\n=== Discord Webhook Payloads ({len(payloads)} events) ===")
        
        for i, payload in enumerate(payloads, 1):
            print(f"\n--- Event {i} ---")
            print(f"Content: {payload['content']}")
            if 'embeds' in payload:
                embed = payload['embeds'][0]
                print(f"Title: {embed.get('title', 'N/A')}")
                print(f"Description: {embed.get('description', 'N/A')}")
                print(f"Color: {embed.get('color', 'N/A')}")
                if 'fields' in embed:
                    for field in embed['fields']:
                        print(f"  {field['name']}: {field['value']}")
                print(f"Timestamp: {embed.get('timestamp', 'N/A')}")
            
            # Send webhook if URL is configured
            if self.discord_webhook_url:
                self.send_discord_webhook(payload)
        
        print(f"\n=== End Discord Webhook Payloads ===")
    
    def emit_all_events(self, events: List[LogEvent] = None):
        """Emit all events in Discord webhook-friendly format."""
        if events is None:
            events = self.events
        
        if not events:
            print("No events found.")
            return
        
        print(f"\n{'='*80}")
        print(f"GRIM OBSERVER - DISCORD WEBHOOK EVENTS")
        print(f"{'='*80}")
        print(f"Total events: {len(events)}")
        print(f"Log file: {self.log_file_path}")
        print(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Group events by type
        event_types = {}
        for event in events:
            if event.event_type not in event_types:
                event_types[event.event_type] = []
            event_types[event.event_type].append(event)
        
        # Emit Discord webhook messages
        for event_type, type_events in event_types.items():
            print(f"\n{event_type.upper()} EVENTS ({len(type_events)}):")
            print(f"{'-' * (len(event_type) + 8)}")
            
            for i, event in enumerate(type_events, 1):
                if event.event_type == 'player_connected':
                    print(f"{i:3d}. 🟢 **{event.player_name}** joined the server")
                    print(f"     📍 IP: {event.ip_address}")
                    print(f"     🕐 {event.timestamp}")
                    print(f"     📝 Discord Message: \"🟢 **{event.player_name}** joined the server\"")
                elif event.event_type == 'player_disconnected':
                    print(f"{i:3d}. 🔴 **{event.player_name}** left the server")
                    print(f"     🕐 {event.timestamp}")
                    print(f"     📝 Discord Message: \"🔴 **{event.player_name}** left the server\"")
                print()
        
        # Summary for Discord context
        print(f"{'='*80}")
        print(f"DISCORD WEBHOOK SUMMARY:")
        print(f"{'='*80}")
        
        players = set()
        for event in events:
            if event.player_name:
                players.add(event.player_name)
        
        print(f"Unique players: {len(players)}")
        if players:
            print(f"Player list: {', '.join(sorted(players))}")
        
        # Calculate final player count
        connected = sum(1 for e in events if e.event_type == 'player_connected')
        disconnected = sum(1 for e in events if e.event_type == 'player_disconnected')
        final_count = max(0, connected - disconnected)
        
        print(f"\nConnection events: {connected}")
        print(f"Disconnection events: {disconnected}")
        print(f"Final player count: {final_count}")
        
        # Discord webhook message examples
        print(f"\n{'='*80}")
        print(f"DISCORD WEBHOOK MESSAGE EXAMPLES:")
        print(f"{'='*80}")
        
        for event in events:
            if event.event_type == 'player_connected':
                print(f"🟢 **{event.player_name}** joined the server")
            elif event.event_type == 'player_disconnected':
                print(f"🔴 **{event.player_name}** left the server")
        
        print(f"\n{'='*80}")
        print(f"Ready to send to Discord webhook!")
        print(f"{'='*80}")
    
    def get_player_count(self) -> int:
        """Calculate current player count based on events for the current map."""
        # Track players who are currently online for this map only
        online_players = set()
        
        for event in self.events:
            # Only count events from the current map instance
            # Since we're running separate instances per map, all events should be from the same map
            # But we can add a safety check if needed
            if event.event_type == 'player_connected':
                online_players.add(event.player_name)
            elif event.event_type == 'player_disconnected':
                # Remove from online players when they disconnect
                online_players.discard(event.player_name)
        
        return len(online_players)
    
    def _get_session_duration(self, player_name: str) -> str:
        """Calculate session duration for a player who just disconnected."""
        # Find the most recent connection event for this player
        # Note: Since we're running separate instances per map, all events are map-specific
        connection_time = None
        for event in reversed(self.events):
            if event.event_type == 'player_connected' and event.player_name == player_name:
                connection_time = self.parse_timestamp(event.timestamp)
                break
        
        if connection_time:
            # Calculate duration from connection to now (approximate)
            current_time = time.time()
            duration_seconds = current_time - connection_time
            
            if duration_seconds < 60:
                return "< 1m"
            elif duration_seconds < 3600:
                minutes = int(duration_seconds // 60)
                return f"{minutes}m"
            else:
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                if minutes == 0:
                    return f"{hours}h"
                else:
                    return f"{hours}h {minutes}m"
        
        return None
    
    def _check_peak_milestone(self, current_players: int) -> Optional[Dict]:
        """Check if we've reached a new peak or milestone and generate celebration message."""
        # Check for new peak
        if current_players > self.peak_players:
            self.peak_players = current_players
            peak_message = self._generate_peak_message(current_players)
            
            # Check for milestone thresholds
            milestone_message = None
            for threshold in self.milestone_thresholds:
                if current_players >= threshold and threshold not in self.reached_milestones:
                    self.reached_milestones.add(threshold)
                    milestone_message = self._generate_milestone_message(threshold)
                    break
            
            # Return peak message (prioritize peak over milestone)
            return peak_message or milestone_message
        
        # Check for milestone thresholds (even if not a new peak)
        for threshold in self.milestone_thresholds:
            if current_players >= threshold and threshold not in self.reached_milestones:
                self.reached_milestones.add(threshold)
                return self._generate_milestone_message(threshold)
        
        return None
    
    def _generate_peak_message(self, player_count: int) -> Dict:
        """Generate a Discord message for a new peak player count in CROM's voice."""
        map_name = self.map_name or "Server"
        map_emoji = "🌴" if map_name.lower() == "siptah" else "🏔️" if map_name.lower() == "exiled" else "🎮"
        
        peak_messages = [
            f"⚔️ **CROM'S TRIUMPH!** {map_name} has reached **{player_count} warriors**! A new peak of strength! The weak tremble! 🗡️",
            f"🔥 **BY CROM'S MIGHT!** {map_name} now commands **{player_count} souls**! The strong multiply, the weak perish! 💀",
            f"🌟 **CROM PROCLAIMS!** {map_name} has achieved **{player_count} warriors**! The server is LEGENDARY! The strong rule! 🏆",
            f"🚀 **CROM'S GLORY!** {map_name} reaches **{player_count} souls**! The weak are nothing, the strong are EVERYTHING! ⚡",
            f"💎 **CROM DECREES!** {map_name} has **{player_count} warriors**! The server is IMMORTAL! The strong survive! 🌟"
        ]
        
        return {
            "content": random.choice(peak_messages),
            "embeds": []
        }
    
    def _generate_milestone_message(self, threshold: int) -> Dict:
        """Generate a Discord message for reaching a milestone threshold in CROM's voice."""
        map_name = self.map_name or "Server"
        map_emoji = "🌴" if map_name.lower() == "siptah" else "🏔️" if map_name.lower() == "exiled" else "🎮"
        
        milestone_messages = {
            5: [
                f"⚔️ **BY CROM!** The weaklings gather! {map_name} now holds **{threshold} souls**! Let them prove their worth! 💀",
                f"🗡️ **CROM SPEAKS!** {map_name} has drawn **{threshold} warriors** from the wastelands! The strong shall survive! ⚡"
            ],
            10: [
                f"🔥 **CROM'S FURY!** {map_name} swells with **{threshold} warriors**! The weak shall perish, the strong shall rule! 🏆",
                f"⚔️ **BY THE SWORD OF CROM!** {map_name} now hosts **{threshold} souls**! Let the blood flow! The strong survive! 💪"
            ],
            15: [
                f"🌟 **CROM'S GLORY!** {map_name} has become a fortress of **{threshold} warriors**! The weak tremble, the strong rejoice! 🚀",
                f"🗡️ **CROM COMMANDS!** {map_name} holds **{threshold} souls**! The strong multiply, the weak fade! The server thrives! 🌟"
            ],
            20: [
                f"🏆 **CROM'S MIGHT!** {map_name} is a citadel of **{threshold} warriors**! The weak are crushed, the strong are LEGENDARY! 🗡️",
                f"⚔️ **BY CROM'S HAND!** {map_name} has **{threshold} souls**! The weak are nothing, the strong are EVERYTHING! 🚀"
            ],
            25: [
                f"💎 **CROM'S POWER!** {map_name} commands **{threshold} warriors**! The weak are dust, the strong are IMMORTAL! 🔥",
                f"🗡️ **CROM DECREES!** {map_name} has **{threshold} souls**! The weak are forgotten, the strong are REMEMBERED! ⚡"
            ],
            30: [
                f"🚀 **CROM'S DOMINION!** {map_name} rules over **{threshold} warriors**! The weak are nothing, the strong are LEGENDS! 🌟",
                f"⚔️ **BY CROM'S WILL!** {map_name} has **{threshold} souls**! The weak are gone, the strong are ETERNAL! 💎"
            ],
            40: [
                f"⚡ **CROM'S SUPREMACY!** {map_name} commands **{threshold} warriors**! The weak are dead, the strong are GODS! 🏆",
                f"🗡️ **CROM PROCLAIMS!** {map_name} has **{threshold} souls**! The weak are nothing, the strong are EVERYTHING! 🚀"
            ],
            50: [
                f"🏆 **CROM'S ABSOLUTE RULE!** {map_name} is a realm of **{threshold} warriors**! The weak are extinct, the strong are LEGENDARY! 💎",
                f"⚔️ **BY CROM'S MIGHT!** {map_name} has **{threshold} souls**! The weak are forgotten, the strong are IMMORTAL! 🌟"
            ]
        }
        
        messages = milestone_messages.get(threshold, [f"⚔️ **CROM SPEAKS!** {map_name} has reached **{threshold} warriors**! The strong multiply! 🗡️"])
        return {
            "content": random.choice(messages),
            "embeds": []
        }
    
    def _reset_peak_tracking(self):
        """Reset peak tracking when server goes empty (useful for daily resets)."""
        self.peak_players = 0
        self.reached_milestones.clear()
        self.logger.info("Peak tracking reset - server went empty")
    
    def _check_empty_server_message(self, current_players: int) -> Optional[Dict]:
        """Check if we should send a recurring empty server message."""
        if current_players == 0:
            current_time = time.time()
            
            # Check if enough time has passed since last empty server message
            if current_time - self.last_empty_server_message >= self.empty_server_message_interval:
                self.last_empty_server_message = current_time
                return self._generate_empty_server_message()
        
        return None
    
    def _select_message_type(self) -> str:
        """Select a message type, avoiding repetition when possible."""
        available_types = list(self.empty_server_message_types.keys())
        
        # If we have a last message type and there are other options, avoid repeating
        if self.last_message_type and len(available_types) > 1:
            available_types = [t for t in available_types if t != self.last_message_type]
        
        # Select new message type
        selected_type = random.choice(available_types)
        self.last_message_type = selected_type
        
        return selected_type
    
    def _get_time_context(self) -> dict:
        """Get time-based context for seasonal variations."""
        now = datetime.now()
        hour = now.hour
        
        # Determine time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Determine if it's weekend
        is_weekend = now.weekday() >= 5
        
        return {
            "time_of_day": time_of_day,
            "is_weekend": is_weekend,
            "hour": hour
        }
    
    def _generate_empty_server_message(self) -> Dict:
        """Generate a Discord message for when the server is empty."""
        map_name = self.map_name or "Server"
        map_emoji = "🌴" if map_name.lower() == "siptah" else "🏔️" if map_name.lower() == "exiled" else "🎮"
        
        # Randomize images for variety
        self.randomize_empty_server_images()
        
        # Select a random message type
        message_type = self._select_message_type()
        
        # Select a random title and description from the chosen type
        title_templates = self.empty_server_message_types[message_type]["title_templates"]
        description_templates = self.empty_server_message_types[message_type]["description_templates"]
        
        title = random.choice(title_templates).format(map_name=map_name, map_emoji=map_emoji)
        description = random.choice(description_templates).format(map_name=map_name, map_emoji=map_emoji)
        
        # Add time-based context variations
        time_context = self._get_time_context()
        time_emoji = random.choice(self.seasonal_variations[time_context["time_of_day"]])
        
        # Sometimes add time-based context to the message
        if random.random() < 0.3:  # 30% chance
            if time_context["time_of_day"] == "night":
                description += f"\n\n{time_emoji} **The night grows long...** CROM's realm sleeps, but the strong never rest."
            elif time_context["time_of_day"] == "morning":
                description += f"\n\n{time_emoji} **A new day dawns...** The battlefield awaits fresh warriors."
            elif time_context["is_weekend"]:
                description += f"\n\n{time_emoji} **Weekend warriors...** Even CROM takes a break, but the arena never sleeps."
        
        if self.use_rich_embeds:
            # Create rich embed with visual elements
            embed = {
                "title": title,
                "description": description,
                "color": self.empty_server_colors.get(map_name.lower(), self.empty_server_colors["default"]),
                "thumbnail": {
                    "url": self.empty_server_images["thumbnail"]
                },
                "image": {
                    "url": self.empty_server_images["main_image"]
                },
                "fields": [
                    {
                        "name": random.choice(self.empty_server_field_variations["server_state"]),
                        "value": "**EMPTY** - No warriors present",
                        "inline": True
                    },
                    {
                        "name": random.choice(self.empty_server_field_variations["next_check"]),
                        "value": f"<t:{int(time.time() + self.empty_server_message_interval)}:R>",
                        "inline": True
                    },
                    {
                        "name": random.choice(self.empty_server_field_variations["map_info"]),
                        "value": f"**{map_name.upper()}**",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": random.choice(self.empty_server_footer_variations),
                    "icon_url": self.empty_server_images["footer_icon"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "content": "",  # Empty content, using embed instead
                "embeds": [embed]
            }
        else:
            # Fallback to simple text message
            return {
                "content": f"{description}\n\n⏰ Next check: <t:{int(time.time() + self.empty_server_message_interval)}:R>",
                "embeds": []
            }
    
    def set_empty_server_interval(self, hours: int):
        """Configure the empty server message interval in hours."""
        self.empty_server_interval = hours * 3600
        self.logger.info(f"Empty server message interval set to {hours} hours")
    
    def toggle_rich_embeds(self, enabled: bool = None):
        """Toggle rich embeds for empty server messages."""
        if enabled is None:
            self.use_rich_embeds = not self.use_rich_embeds
        else:
            self.use_rich_embeds = enabled
        
        status = "enabled" if self.use_rich_embeds else "disabled"
        self.logger.info(f"Rich embeds {status} for empty server messages")
    
    def set_empty_server_images(self, thumbnail: str = None, main_image: str = None, footer_icon: str = None):
        """Configure custom images for empty server messages."""
        if thumbnail:
            self.empty_server_images["thumbnail"] = thumbnail
        if main_image:
            self.empty_server_images["main_image"] = main_image
        if footer_icon:
            self.empty_server_images["footer_icon"] = footer_icon
        
        self.logger.info("Empty server message images updated")
    
    def randomize_empty_server_images(self):
        """Randomly select new images for empty server messages."""
        import random
        
        # Randomly select thumbnail
        if len(self.empty_server_image_options["thumbnail"]) > 1:
            self.empty_server_images["thumbnail"] = random.choice(self.empty_server_image_options["thumbnail"])
        
        # Randomly select main image
        if len(self.empty_server_image_options["main_image"]) > 1:
            self.empty_server_images["main_image"] = random.choice(self.empty_server_image_options["main_image"])
        
        # Randomly select footer icon (only one option currently)
        if len(self.empty_server_image_options["footer_icon"]) > 1:
            self.empty_server_images["footer_icon"] = random.choice(self.empty_server_image_options["footer_icon"])
        
        self.logger.info(f"Randomized empty server images: {self.empty_server_images}")
    
    def disable_image_randomization(self):
        """Disable image randomization and use default images."""
        self.empty_server_images = {
            "thumbnail": self.empty_server_image_options["thumbnail"][0],
            "main_image": self.empty_server_image_options["main_image"][0],
            "footer_icon": self.empty_server_image_options["footer_icon"][0]
        }
        self.logger.info("Image randomization disabled, using default images")
    
    def get_recent_events(self, minutes: int = 10) -> List[LogEvent]:
        """Get events from the last N minutes."""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        return [e for e in self.events if self.parse_timestamp(e.timestamp) > cutoff_time]
    
    def parse_timestamp(self, timestamp: str) -> float:
        """Parse timestamp string to Unix timestamp."""
        try:
            # Convert [2025.08.09-22.09.34:324] to datetime
            dt_str = timestamp.replace('[', '').replace(']', '')
            dt = datetime.strptime(dt_str, '%Y.%m.%d-%H.%M.%S:%f')
            return dt.timestamp()
        except Exception:
            return 0
    
    def run(self, interval: float = 1.0):
        """Main monitoring loop."""
        self.logger.info(f"Starting Grim Observer - monitoring {self.log_file_path}")
        self.logger.info(f"Output file: {self.output_file or 'None'}")
        
        self.running = True
        self.current_position = self.get_current_position()
        
        try:
            while self.running:
                new_lines = self.read_new_lines()
                
                for line in new_lines:
                    self.process_line(line)
                
                # Print status every 30 seconds
                if len(self.events) > 0 and int(time.time()) % 30 == 0:
                    player_count = self.get_player_count()
                    self.logger.info(f"Current player count: {player_count}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the monitoring."""
        self.running = False

    def save_discord_webhook_payloads(self, events: List[LogEvent] = None, output_file: str = None):
        """Save Discord webhook payloads to a file."""
        if events is None:
            events = self.events
        
        if not output_file:
            output_file = "discord_webhook_payloads.json"
        
        payloads = self.generate_discord_webhook_payloads(events)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(payloads, f, indent=2)
            self.logger.info(f"Saved {len(payloads)} Discord webhook payloads to {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Error saving Discord webhook payloads: {e}")
            return None

    def emit_webhook_content_only(self, events: List[LogEvent] = None):
        """Emit only the Discord webhook content without any extra formatting."""
        if events is None:
            events = self.events
        
        if not events:
            return
        
        # Generate Discord webhook payloads
        payloads = self.generate_discord_webhook_payloads(events)
        
        # Only show player join/leave events (green and red messages)
        for event, payload in zip(events, payloads):
            if event.event_type in ['player_connected', 'player_disconnected']:
                print(payload['content'])


def load_secrets(map_name: Optional[str] = None) -> Dict[str, str]:
    """Load secrets from environment variables set by the batch wrapper.
    
    Args:
        map_name: The map name (e.g., 'exiled', 'siptah'). Used for logging only.
        
    Returns:
        Dictionary containing secrets (e.g., discord_webhook_url)
    """
    secrets = {}
    
    # DEBUG: Log all environment variables for troubleshooting
    print(f"[DEBUG] Environment variables check:", file=sys.stderr)
    print(f"[DEBUG] - DISCORD_WEBHOOK_URL: {os.environ.get('DISCORD_WEBHOOK_URL', 'NOT_SET')}", file=sys.stderr)
    print(f"[DEBUG] - MAP_NAME: {os.environ.get('MAP_NAME', 'NOT_SET')}", file=sys.stderr)
    print(f"[DEBUG] - LOG_FILE_PATH: {os.environ.get('LOG_FILE_PATH', 'NOT_SET')}", file=sys.stderr)
    print(f"[DEBUG] - Current working directory: {os.getcwd()}", file=sys.stderr)
    print(f"[DEBUG] - Python executable: {sys.executable}", file=sys.stderr)
    print(f"[DEBUG] - Python version: {sys.version}", file=sys.stderr)
    
    # Load Discord webhook URL from environment (set by batch wrapper)
    discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if discord_webhook_url:
        secrets['discord_webhook_url'] = discord_webhook_url
        print(f"[DEBUG] Discord webhook URL loaded: {discord_webhook_url[:50]}...", file=sys.stderr)
        if map_name:
            print(f"[GrimObserver][INFO] Loaded Discord webhook URL for {map_name} map from environment", file=sys.stderr)
        else:
            print("[GrimObserver][INFO] Loaded Discord webhook URL from environment", file=sys.stderr)
    else:
        print("[GrimObserver][WARN] No DISCORD_WEBHOOK_URL found in environment", file=sys.stderr)
    
    # Load other map-specific environment variables if available
    map_name_env = os.environ.get('MAP_NAME')
    if map_name_env:
        secrets['map_name'] = map_name_env
        print(f"[GrimObserver][INFO] Map name: {map_name_env}", file=sys.stderr)
    
    print(f"[DEBUG] Final secrets loaded: {secrets}", file=sys.stderr)
    return secrets

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Monitor Conan Exiles server logs for player events')
    parser.add_argument('mode', choices=['scan', 'monitor', 'scan-monitor'], help='Operation mode')
    parser.add_argument('log_file', help='Path to the log file to monitor')
    parser.add_argument('--output', help='Output file for events (JSON format)')
    parser.add_argument('--interval', type=float, default=1.0, help='Check interval in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--service', action='store_true', help='Run as Windows service')
    parser.add_argument('--discord', action='store_true', help='Output in Discord webhook format')
    parser.add_argument('--discord-output', help='Output file for Discord webhook payloads (JSON format)')
    parser.add_argument('--webhook-only', action='store_true', help='Show only Discord webhook content without formatting')
    parser.add_argument('--force-curl', action='store_true', help='Force use of CURL for Discord webhooks (bypasses Python libraries)')
    parser.add_argument('--map', help='Specify the map name (e.g., exiled, siptah) for secrets loading')
    parser.add_argument('--empty-interval', type=int, default=4, help='Empty server message interval in hours (default: 4)')
    parser.add_argument('--no-rich-embeds', action='store_true', help='Disable rich embeds for empty server messages (use simple text)')
    parser.add_argument('--thumbnail-url', help='Custom thumbnail image URL for empty server messages')
    parser.add_argument('--main-image-url', help='Custom main image URL for empty server messages')
    parser.add_argument('--footer-icon-url', help='Custom footer icon URL for empty server messages')
    parser.add_argument('--no-random-images', action='store_true', help='Disable image randomization for empty server messages (use same images each time)')
    
    args = parser.parse_args()
    
    # Display version information
    print(f"[GrimObserver][INFO] Grim Observer v{__version__} ({__version_date__})", file=sys.stderr)
    print(f"[GrimObserver][INFO] Python version: {sys.version.split()[0]}", file=sys.stderr)
    
    # DEBUG: Log all parsed arguments for troubleshooting
    print(f"[DEBUG] Command line arguments parsed:", file=sys.stderr)
    print(f"[DEBUG] - mode: {args.mode}", file=sys.stderr)
    print(f"[DEBUG] - log_file: {args.log_file}", file=sys.stderr)
    print(f"[DEBUG] - output: {args.output}", file=sys.stderr)
    print(f"[DEBUG] - interval: {args.interval}", file=sys.stderr)
    print(f"[DEBUG] - verbose: {args.verbose}", file=sys.stderr)
    print(f"[DEBUG] - service: {args.service}", file=sys.stderr)
    print(f"[DEBUG] - discord: {args.discord}", file=sys.stderr)
    print(f"[DEBUG] - discord_output: {args.discord_output}", file=sys.stderr)
    print(f"[DEBUG] - webhook_only: {args.webhook_only}", file=sys.stderr)
    print(f"[DEBUG] - map: {args.map}", file=sys.stderr)
    print(f"[DEBUG] - empty-interval: {args.empty_interval}", file=sys.stderr)
    print(f"[DEBUG] - no-rich-embeds: {args.no_rich_embeds}", file=sys.stderr)
    print(f"[DEBUG] - thumbnail-url: {args.thumbnail_url}", file=sys.stderr)
    print(f"[DEBUG] - main-image-url: {args.main_image_url}", file=sys.stderr)
    print(f"[DEBUG] - footer-icon-url: {args.footer_icon_url}", file=sys.stderr)
    print(f"[DEBUG] - no-random-images: {args.no_random_images}", file=sys.stderr)
    
    # Load secrets based on map parameter
    secrets = load_secrets(args.map)
    discord_webhook_url = secrets.get('discord_webhook_url')
    
    print(f"[DEBUG] Discord webhook URL from secrets: {discord_webhook_url[:50] if discord_webhook_url else 'None'}...", file=sys.stderr)
    
    if args.discord or args.webhook_only or args.discord_output:
        if not discord_webhook_url:
            print("[GrimObserver][WARN] Discord webhook URL not found in secrets or environment", file=sys.stderr)
            print("[GrimObserver][WARN] Set DISCORD_WEBHOOK_URL environment variable or create secrets file", file=sys.stderr)
    
    try:
        observer = GrimObserver(
            log_file_path=args.log_file,
            output_file=args.output,
            verbose=args.verbose,
            discord_webhook_url=discord_webhook_url, # Pass the loaded URL
            force_curl=args.force_curl,  # Pass the force-curl flag
            map_name=args.map  # Pass the map name for Discord titles
        )
        
        # Set the empty server interval from command line argument
        observer.set_empty_server_interval(args.empty_interval)
        
        # Configure rich embeds
        if args.no_rich_embeds:
            observer.toggle_rich_embeds(False)
            print("[GrimObserver][INFO] Rich embeds disabled for empty server messages.")
        else:
            print("[GrimObserver][INFO] Rich embeds enabled for empty server messages.")

        # Set custom images if provided
        if args.thumbnail_url:
            observer.set_empty_server_images(thumbnail=args.thumbnail_url)
            print(f"[GrimObserver][INFO] Custom thumbnail image set to: {args.thumbnail_url}")
        if args.main_image_url:
            observer.set_empty_server_images(main_image=args.main_image_url)
            print(f"[GrimObserver][INFO] Custom main image set to: {args.main_image_url}")
        if args.footer_icon_url:
            observer.set_empty_server_images(footer_icon=args.footer_icon_url)
            print(f"[GrimObserver][INFO] Custom footer icon set to: {args.footer_icon_url}")
        
        # Configure image randomization
        if args.no_random_images:
            observer.disable_image_randomization()
            print("[GrimObserver][INFO] Image randomization disabled for empty server messages.")
        else:
            print("[GrimObserver][INFO] Image randomization enabled for empty server messages.")

        if args.service:
            # Windows service mode - basic implementation
            print("[GrimObserver][INFO] Windows service mode activated")
            print("[GrimObserver][INFO] Running as background service...")
            print("[GrimObserver][INFO] Note: Full Windows service integration requires pywin32")
            
            # For now, just run in the background
            observer.run(interval=args.interval)
            return
        
        if args.mode == 'scan':
            # Scan mode: process entire log and emit all events
            events = observer.scan_entire_log()
            observer.events = events  # Store events for other operations
            
            if args.webhook_only:
                # Webhook-only mode: show only the webhook content
                observer.emit_webhook_content_only(events)
            elif args.discord:
                # Discord webhook mode
                observer.emit_discord_webhook_events(events)
                
                # Save Discord webhook payloads if specified
                if args.discord_output:
                    observer.save_discord_webhook_payloads(events, args.discord_output)
                else:
                    observer.save_discord_webhook_payloads(events)
            else:
                # Normal scan mode
                observer.emit_all_events(events)
            
            # Save to output file if specified
            if args.output:
                print(f"\nSaving all events to: {args.output}")
                for event in events:
                    observer.save_event(event)
                print(f"Saved {len(events)} events to {args.output}")
        
        elif args.mode == 'scan-monitor':
            # Scan-monitor mode: scan entire log first, then continue monitoring
            print("[GrimObserver][INFO] Starting scan-monitor mode...")
            print("[GrimObserver][INFO] Phase 1: Scanning entire log file...")
            
            # First scan the entire log file
            events = observer.scan_entire_log()
            observer.events = events  # Store events for other operations
            
            if args.webhook_only:
                # Webhook-only mode: show only the webhook content
                observer.emit_webhook_content_only(events)
            elif args.discord:
                # Discord webhook mode
                observer.emit_discord_webhook_events(events)
                
                # Save Discord webhook payloads if specified
                if args.discord_output:
                    observer.save_discord_webhook_payloads(events, args.discord_output)
                else:
                    observer.save_discord_webhook_payloads(events)
            else:
                # Normal scan mode
                observer.emit_all_events(events)
            
            # Save to output file if specified
            if args.output:
                print(f"\nSaving all events to: {args.output}")
                for event in events:
                    observer.save_event(event)
                print(f"Saved {len(events)} events to {args.output}")
            
            print(f"\n[GrimObserver][INFO] Phase 2: Starting continuous monitoring for new events...")
            print("[GrimObserver][INFO] Press Ctrl+C to stop monitoring")
            
            # Now continue monitoring for new changes
            observer.run(interval=args.interval)
            
        elif args.mode == 'monitor':
            # Normal monitoring mode - but first scan to get accurate player count
            print("[GrimObserver][INFO] Starting monitor mode...")
            print("[GrimObserver][INFO] Phase 1: Scanning log file for current player state...")
            
            # Scan the entire log first to get accurate player count
            events = observer.scan_entire_log()
            observer.events = events  # Store events for accurate player counting
            
            print(f"[GrimObserver][INFO] Found {len(events)} historical events")
            current_players = observer.get_player_count()
            print(f"[GrimObserver][INFO] Current player count: {current_players}")
            
            print(f"[GrimObserver][INFO] Phase 2: Starting continuous monitoring for new events...")
            print("[GrimObserver][INFO] Press Ctrl+C to stop monitoring")
            
            # Now continue monitoring for new changes
            observer.run(interval=args.interval)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

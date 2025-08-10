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
    """Main monitoring class for ConanSandbox logs."""
    
    def __init__(self, log_file_path: str, output_file: str = None, verbose: bool = False, discord_webhook_url: str = None, force_curl: bool = False, map_name: str = None):
        self.log_file_path = Path(log_file_path)
        self.output_file = Path(output_file) if output_file else None
        self.verbose = verbose
        self.discord_webhook_url = discord_webhook_url
        self.map_name = map_name
        self.parser = ConanLogParser()
        self.events: List[LogEvent] = []
        self.current_position = 0
        self.running = False
        self.version = __version__
        self.version_date = __version_date__
        self.force_curl = force_curl
        
        # Setup logging
        self.setup_logging()
        
        # Validate log file
        if not self.log_file_path.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('grim_observer.log') if self.output_file else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Log version information
        self.logger.info(f"Grim Observer v{self.version} ({self.version_date}) initialized")
        self.logger.info(f"Log file: {self.log_file_path}")
        if self.discord_webhook_url:
            self.logger.info(f"Discord webhook configured: {self.discord_webhook_url[:50]}...")
    
    def get_current_position(self) -> int:
        """Get current position in the log file."""
        try:
            return self.log_file_path.stat().st_size
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
        """Calculate current player count based on events."""
        connected = sum(1 for e in self.events if e.event_type == 'player_connected')
        disconnected = sum(1 for e in self.events if e.event_type == 'player_disconnected')
        return max(0, connected - disconnected)
    
    def _get_session_duration(self, player_name: str) -> str:
        """Calculate session duration for a player who just disconnected."""
        # Find the most recent connection event for this player
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
                return f"{int(duration_seconds)}s"
            elif duration_seconds < 3600:
                minutes = int(duration_seconds // 60)
                return f"{minutes}m"
            else:
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        
        return None
    
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
            # Normal monitoring mode
            observer.run(interval=args.interval)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

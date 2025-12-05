"""Main entry point for DnDSpeaker application."""
import sys
import signal
import keyboard  # type: ignore
import numpy as np
from audio_engine import AudioEngine
from voice_processor import VoiceProcessor
from voice_presets import get_preset, list_presets
from config import Config
from gui import DnDSpeakerGUI


class DnDSpeakerApp:
    """Main application controller."""
    
    def __init__(self):
        self.config = Config()
        
        # Initialize audio components
        self.sample_rate = 44100
        self.chunk_size = 1024
        
        self.audio_engine = AudioEngine(
            sample_rate=self.sample_rate,
            chunk_size=self.chunk_size
        )
        
        self.voice_processor = VoiceProcessor(
            sample_rate=self.sample_rate,
            chunk_size=self.chunk_size
        )
        
        # Set up processing callback
        self.audio_engine.set_process_callback(self._process_audio)
        
        # Initialize voice preset
        current_voice = self.config.get("current_voice", "Neutral Narrator")
        preset = get_preset(current_voice)
        self.voice_processor.set_preset(preset)
        
        # Create GUI
        import voice_presets
        self.gui = DnDSpeakerGUI(
            self.audio_engine,
            self.voice_processor,
            self.config,
            voice_presets
        )
        
        # Set up GUI callbacks
        self.gui.on_voice_change = self._on_voice_change
        
        # Set up hotkeys
        self._setup_hotkeys()
        
        # Handle cleanup on exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _process_audio(self, audio: np.ndarray) -> np.ndarray:
        """Process audio chunk."""
        return self.voice_processor.process(audio)
    
    def _on_voice_change(self, voice: str):
        """Handle voice change from GUI."""
        preset = get_preset(voice)
        self.voice_processor.set_preset(preset)
    
    def _setup_hotkeys(self):
        """Set up keyboard hotkeys."""
        hotkeys = self.config.get("hotkeys", {})
        
        for key, voice in hotkeys.items():
            try:
                # Register hotkey
                keyboard.add_hotkey(key, lambda v=voice: self._switch_voice(v))
                print(f"Registered hotkey: {key} -> {voice}")
            except Exception as e:
                print(f"Failed to register hotkey {key}: {e}")
    
    def _switch_voice(self, voice: str):
        """Switch voice from hotkey."""
        if voice in list_presets():
            self.gui.set_voice_from_hotkey(voice)
            print(f"Switched to: {voice}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources."""
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        self.audio_engine.cleanup()
        self.gui.cleanup()
    
    def run(self):
        """Run the application."""
        try:
            self.gui.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    print("Starting DnD Speaker...")
    print("Note: On some systems, you may need to run with administrator/sudo privileges for hotkeys to work.")
    
    app = DnDSpeakerApp()
    app.run()


if __name__ == "__main__":
    main()


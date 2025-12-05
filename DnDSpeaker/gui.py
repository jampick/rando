"""GUI for DnDSpeaker application."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List, Tuple
import threading


class LevelMeter(tk.Canvas):
    """Visual level meter for audio."""
    
    def __init__(self, parent, width=200, height=20, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.width = width
        self.height = height
        self.level = 0.0
        
        # Draw background
        self.create_rectangle(0, 0, width, height, fill="#333333", outline="")
        
        # Draw segments
        self.segments = []
        for i in range(20):
            x1 = i * (width / 20)
            x2 = (i + 1) * (width / 20)
            color = "#00ff00" if i < 15 else "#ffff00" if i < 18 else "#ff0000"
            seg = self.create_rectangle(x1, 0, x2, height, fill="#222222", outline="")
            self.segments.append((seg, color))
    
    def update_level(self, level: float):
        """Update the level display."""
        self.level = max(0.0, min(1.0, level))
        active_segments = int(self.level * 20)
        
        for i, (seg_id, color) in enumerate(self.segments):
            if i < active_segments:
                self.itemconfig(seg_id, fill=color)
            else:
                self.itemconfig(seg_id, fill="#222222")


class DnDSpeakerGUI:
    """Main GUI window."""
    
    def __init__(self, audio_engine, voice_processor, config, voice_presets):
        self.audio_engine = audio_engine
        self.voice_processor = voice_processor
        self.config = config
        self.voice_presets = voice_presets
        
        self.root = tk.Tk()
        self.root.title("DnD Speaker - Voice Transformation")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Callbacks
        self.on_voice_change: Optional[Callable[[str], None]] = None
        self.on_start_stop: Optional[Callable[[bool], None]] = None
        self.on_bypass_toggle: Optional[Callable[[bool], None]] = None
        
        # State
        self.is_running = False
        self.current_voice = config.get("current_voice", "Neutral Narrator")
        
        self._build_ui()
        self._load_settings()
        self._start_level_monitor()
    
    def _build_ui(self):
        """Build the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="DnD Speaker", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input device selection
        ttk.Label(main_frame, text="Microphone Input:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_var = tk.StringVar()
        self.input_combo = ttk.Combobox(main_frame, textvariable=self.input_var, width=40, state="readonly")
        self.input_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.input_combo.bind("<<ComboboxSelected>>", self._on_input_device_change)
        
        # Output device selection
        ttk.Label(main_frame, text="Output Device:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        self.output_combo = ttk.Combobox(main_frame, textvariable=self.output_var, width=40, state="readonly")
        self.output_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.output_combo.bind("<<ComboboxSelected>>", self._on_output_device_change)
        
        # Refresh devices button
        refresh_btn = ttk.Button(main_frame, text="Refresh Devices", command=self._refresh_devices)
        refresh_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Voice selection
        ttk.Label(main_frame, text="Character Voices:", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=2, pady=(10, 5))
        
        # Voice buttons frame
        voice_frame = ttk.Frame(main_frame)
        voice_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.voice_buttons = {}
        from voice_presets import list_presets
        voices = list_presets()
        for i, voice in enumerate(voices):
            btn = ttk.Button(
                voice_frame,
                text=voice,
                width=15,
                command=lambda v=voice: self._on_voice_select(v)
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.voice_buttons[voice] = btn
        
        # Current voice display
        self.current_voice_label = ttk.Label(main_frame, text=f"Current: {self.current_voice}", font=("Arial", 10))
        self.current_voice_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Level meters
        levels_frame = ttk.LabelFrame(main_frame, text="Audio Levels", padding="10")
        levels_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(levels_frame, text="Input:").grid(row=0, column=0, sticky=tk.W)
        self.input_meter = LevelMeter(levels_frame, width=300, height=25)
        self.input_meter.grid(row=0, column=1, padx=10)
        
        ttk.Label(levels_frame, text="Output:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.output_meter = LevelMeter(levels_frame, width=300, height=25)
        self.output_meter.grid(row=1, column=1, padx=10, pady=(10, 0))
        
        # Controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        self.start_stop_btn = ttk.Button(
            controls_frame,
            text="Start",
            command=self._on_start_stop_click,
            width=15
        )
        self.start_stop_btn.grid(row=0, column=0, padx=5)
        
        self.bypass_var = tk.BooleanVar(value=self.config.get("bypass", False))
        bypass_check = ttk.Checkbutton(
            controls_frame,
            text="Bypass (No Processing)",
            variable=self.bypass_var,
            command=self._on_bypass_toggle
        )
        bypass_check.grid(row=0, column=1, padx=5)
        
        # Hotkeys info
        hotkeys_frame = ttk.LabelFrame(main_frame, text="Hotkeys", padding="10")
        hotkeys_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        hotkeys_text = "Press number keys 1-6 to switch voices:\n"
        hotkeys = self.config.get("hotkeys", {})
        for key, voice in sorted(hotkeys.items()):
            hotkeys_text += f"  {key}: {voice}\n"
        
        hotkeys_label = ttk.Label(hotkeys_frame, text=hotkeys_text, justify=tk.LEFT)
        hotkeys_label.grid(row=0, column=0, sticky=tk.W)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def _refresh_devices(self):
        """Refresh the device lists."""
        # Input devices
        input_devices = self.audio_engine.get_input_devices()
        input_names = [f"{name} ({idx})" for idx, name in input_devices]
        self.input_combo['values'] = input_names
        
        # Output devices
        output_devices = self.audio_engine.get_output_devices()
        output_names = [f"{name} ({idx})" for idx, name in output_devices]
        self.output_combo['values'] = output_names
    
    def _load_settings(self):
        """Load settings from config."""
        # Load devices
        self._refresh_devices()
        
        input_idx = self.config.get("input_device")
        output_idx = self.config.get("output_device")
        
        if input_idx is not None:
            input_devices = self.audio_engine.get_input_devices()
            for idx, name in input_devices:
                if idx == input_idx:
                    self.input_var.set(f"{name} ({idx})")
                    self.audio_engine.set_input_device(idx)
                    break
        
        if output_idx is not None:
            output_devices = self.audio_engine.get_output_devices()
            for idx, name in output_devices:
                if idx == output_idx:
                    self.output_var.set(f"{name} ({idx})")
                    self.audio_engine.set_output_device(idx)
                    break
        
        # Load voice
        self._on_voice_select(self.current_voice)
    
    def _on_input_device_change(self, event=None):
        """Handle input device change."""
        selection = self.input_var.get()
        if selection:
            # Extract device index from "(name) (idx)" format
            try:
                idx_str = selection.split("(")[-1].rstrip(")")
                idx = int(idx_str)
                self.audio_engine.set_input_device(idx)
                self.config.set("input_device", idx)
            except Exception:
                pass
    
    def _on_output_device_change(self, event=None):
        """Handle output device change."""
        selection = self.output_var.get()
        if selection:
            try:
                idx_str = selection.split("(")[-1].rstrip(")")
                idx = int(idx_str)
                self.audio_engine.set_output_device(idx)
                self.config.set("output_device", idx)
            except Exception:
                pass
    
    def _on_voice_select(self, voice: str):
        """Handle voice selection."""
        self.current_voice = voice
        self.current_voice_label.config(text=f"Current: {voice}")
        
        # Update button states
        for v, btn in self.voice_buttons.items():
            if v == voice:
                btn.state(['pressed'])
            else:
                btn.state(['!pressed'])
        
        # Update processor
        from voice_presets import get_preset
        preset = get_preset(voice)
        self.voice_processor.set_preset(preset)
        
        # Save to config
        self.config.set("current_voice", voice)
        
        # Notify callback
        if self.on_voice_change:
            self.on_voice_change(voice)
    
    def _on_start_stop_click(self):
        """Handle start/stop button click."""
        if not self.is_running:
            # Start
            if self.audio_engine.input_device_index is None or self.audio_engine.output_device_index is None:
                messagebox.showerror("Error", "Please select both input and output devices")
                return
            
            try:
                self.audio_engine.start()
                self.is_running = True
                self.start_stop_btn.config(text="Stop")
                if self.on_start_stop:
                    self.on_start_stop(True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start audio: {e}")
        else:
            # Stop
            self.audio_engine.stop()
            self.is_running = False
            self.start_stop_btn.config(text="Start")
            if self.on_start_stop:
                self.on_start_stop(False)
    
    def _on_bypass_toggle(self):
        """Handle bypass toggle."""
        bypass = self.bypass_var.get()
        self.audio_engine.set_bypass(bypass)
        self.config.set("bypass", bypass)
        if self.on_bypass_toggle:
            self.on_bypass_toggle(bypass)
    
    def _start_level_monitor(self):
        """Start monitoring audio levels."""
        def update_levels():
            if self.is_running:
                input_level = self.audio_engine.get_input_level()
                output_level = self.audio_engine.get_output_level()
                
                self.input_meter.update_level(input_level)
                self.output_meter.update_level(output_level)
            
            # Schedule next update
            self.root.after(50, update_levels)
        
        update_levels()
    
    def set_voice_from_hotkey(self, voice: str):
        """Set voice from hotkey (called externally)."""
        if voice in self.voice_buttons:
            self._on_voice_select(voice)
    
    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()
    
    def cleanup(self):
        """Clean up GUI resources."""
        self.audio_engine.cleanup()
        self.root.destroy()


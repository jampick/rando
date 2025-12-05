# DnD Speaker - Real-Time Voice Transformation

A desktop application that allows Dungeon Masters to transform their voice in real-time for different character personalities during tabletop roleplaying games.

## Features

- **Real-time voice transformation** with low latency
- **6 distinct character voices**:
  - Goblin (high, fast, scratchy)
  - Dragon (deep, heavy, echoing)
  - Lich (cold, unnatural, ethereal)
  - Noble Elf (smooth, bright, elegant)
  - Warforged (mechanical, resonant, metallic)
  - Neutral Narrator (clean, mild coloration)
- **Instant voice switching** via GUI buttons or hotkeys (1-6)
- **Device selection** for microphone input and audio output
- **Visual level meters** for input and output monitoring
- **Bypass mode** to disable processing
- **Settings persistence** - remembers your last configuration
- **Fully local** - no cloud connection required

## Requirements

- Python 3.8 or higher
- macOS, Windows, or Linux
- Microphone input device
- Audio output device

## Installation

### Quick Setup (Recommended)

**macOS/Linux:**
```bash
cd DnDSpeaker
./setup.sh
```

**Windows:**
```batch
cd DnDSpeaker
setup.bat
```

The setup script will:
- Create a virtual environment (if needed)
- Install all required dependencies
- Handle system-level dependencies (PortAudio on macOS)

### Manual Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

**Note for macOS users**: You may need to install PortAudio first:
```bash
brew install portaudio
```

**Note for Linux users**: You may need to install PortAudio and ALSA development libraries:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
# or
sudo yum install portaudio-devel python3-pyaudio
```

**Note for Windows users**: PyAudio should install automatically, but if you encounter issues, you may need to install a pre-built wheel or use conda.

## Usage

1. Run the application:
```bash
python main.py
```

2. **Select your devices**:
   - Choose your microphone from the "Microphone Input" dropdown
   - Choose your output device from the "Output Device" dropdown
   - Click "Refresh Devices" if your devices don't appear

3. **Start processing**:
   - Click the "Start" button to begin audio processing
   - Speak into your microphone to hear the transformed voice

4. **Switch voices**:
   - Click any character voice button in the GUI
   - Or press number keys 1-6 on your keyboard:
     - `1`: Goblin
     - `2`: Dragon
     - `3`: Lich
     - `4`: Noble Elf
     - `5`: Warforged
     - `6`: Neutral Narrator

5. **Monitor levels**:
   - Watch the input and output level meters to ensure proper audio levels
   - Adjust your microphone gain if input levels are too low or high

6. **Bypass mode**:
   - Check "Bypass (No Processing)" to hear your unprocessed voice
   - Useful for testing or when you want to speak normally

## Using with Discord or VTT

To route the transformed audio to Discord or Virtual Tabletop platforms:

1. **Windows**: Use a virtual audio cable (e.g., VB-Audio Virtual Cable) and select it as your output device in DnD Speaker. Then set Discord/VTT to use the virtual cable as input.

2. **macOS**: Use BlackHole or Loopback to create a virtual audio device. Select it as output in DnD Speaker, then route it to Discord/VTT.

3. **Linux**: Use JACK or PulseAudio loopback. Configure PulseAudio to create a null sink and route DnD Speaker output to it, then use that as input in Discord/VTT.

## Hotkeys

The application supports global hotkeys (number keys 1-6) to switch voices instantly. On some systems, you may need to run the application with administrator/sudo privileges for hotkeys to work properly.

## Configuration

Settings are automatically saved to `dndspeaker_config.json` in the application directory. This includes:
- Last used input/output devices
- Current voice selection
- Bypass state
- Hotkey mappings

## Troubleshooting

**No audio devices appear**:
- Make sure your microphone and speakers are connected
- Click "Refresh Devices"
- Check system audio settings

**High latency**:
- Try reducing the chunk size in `main.py` (currently 1024)
- Close other audio applications
- Check your audio driver settings

**Hotkeys not working**:
- On macOS/Linux, you may need to grant accessibility permissions
- On Windows, try running as administrator
- Some applications may block global hotkeys

**Audio dropouts or glitches**:
- Increase the chunk size in `main.py`
- Close other CPU-intensive applications
- Check that your audio drivers are up to date

**Distorted audio**:
- Check input levels - reduce microphone gain if too high
- Try a different voice preset
- Ensure output device volume is reasonable

## Technical Details

- **Sample Rate**: 44.1 kHz
- **Chunk Size**: 1024 samples (~23ms latency)
- **Processing**: Real-time DSP using NumPy and SciPy
- **GUI**: Tkinter
- **Audio I/O**: PyAudio

## Adding New Voices

To add new voice presets, edit `voice_presets.py` and add a new entry to `VOICE_PRESETS` dictionary. Parameters include:
- `pitch_shift`: Pitch multiplier (1.0 = normal, >1.0 = higher, <1.0 = lower)
- `formant_shift`: Formant frequency multiplier
- `speed`: Speech speed multiplier
- `low_cut` / `high_cut`: Frequency cutoffs in Hz
- `low_boost` / `high_boost`: Frequency boost multipliers
- `resonance`: Resonance amount (0.0-1.0)
- `reverb`: Reverb amount (0.0-1.0)
- `distortion`: Distortion amount (0.0-1.0)
- `tremolo`: Tremolo amount (0.0-1.0)
- `phaser`: Phaser amount (0.0-1.0)
- `ring_mod`: Ring modulation amount (0.0-1.0)

## License

This project is provided as-is for personal use.


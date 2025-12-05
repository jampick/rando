# DnD Speaker - Quick Demo Guide

## Quick Start Demo

### Step 1: Install Dependencies

```bash
cd DnDSpeaker
pip install -r requirements.txt
```

**macOS users**: You may need PortAudio first:
```bash
brew install portaudio
```

**Linux users**: 
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
# or
sudo yum install portaudio-devel python3-pyaudio
```

### Step 2: Run the Application

```bash
python main.py
```

Or use the convenience scripts:
- **macOS/Linux**: `./start.sh`
- **Windows**: `start.bat`

### Step 3: Demo Flow

1. **Select Devices** (if not auto-selected):
   - Choose your microphone from "Microphone Input" dropdown
   - Choose your speakers/headphones from "Output Device" dropdown
   - Click "Refresh Devices" if needed

2. **Start Processing**:
   - Click the "Start" button
   - You should see the input level meter react when you speak

3. **Test Each Voice**:
   - Click each character button and speak:
     - **Goblin** (1): High-pitched, fast, scratchy
     - **Dragon** (2): Deep, booming, with echo
     - **Lich** (3): Cold, unnatural, ethereal
     - **Noble Elf** (4): Smooth, bright, elegant
     - **Warforged** (5): Mechanical, metallic, resonant
     - **Neutral Narrator** (6): Clean, minimal processing

4. **Test Hotkeys**:
   - Press number keys 1-6 while speaking to switch voices instantly
   - This simulates switching characters mid-conversation

5. **Test Bypass**:
   - Check "Bypass (No Processing)" to hear your normal voice
   - Uncheck to return to processed voice

### Demo Script Example

Try this sequence to showcase the app:

1. Start with **Neutral Narrator** - speak normally: "Welcome to the adventure..."
2. Switch to **Goblin** (press 1): "Hehe, shiny things! Give me gold!"
3. Switch to **Dragon** (press 2): "You dare enter my lair? I am ancient and powerful!"
4. Switch to **Lich** (press 3): "Your mortal life means nothing to me..."
5. Switch to **Noble Elf** (press 4): "We have watched these lands for millennia..."
6. Switch to **Warforged** (press 5): "My purpose is clear. I serve the directive."

### Troubleshooting Demo Issues

**No audio devices appear**:
- Make sure microphone is connected and enabled in system settings
- Click "Refresh Devices"
- Check that your OS recognizes the devices

**No sound output**:
- Verify output device is correct
- Check system volume
- Try a different output device

**High latency/delay**:
- Close other audio applications
- Try reducing chunk size in `main.py` (line 19: change `chunk_size = 1024` to `512`)

**Hotkeys not working**:
- On macOS: Grant accessibility permissions in System Preferences
- On Linux: May need to run with `sudo` or grant permissions
- On Windows: Try running as administrator

**Audio is distorted**:
- Lower your microphone input gain in system settings
- Try the "Neutral Narrator" voice first to test
- Check that input levels aren't peaking (red on meter)

### Best Demo Setup

For the best demo experience:

1. **Use headphones** to prevent feedback
2. **Test in a quiet room** to minimize background noise
3. **Speak clearly** into the microphone
4. **Have a script ready** with lines for each character
5. **Show the level meters** - they should react when you speak
6. **Demonstrate hotkey switching** while mid-sentence to show real-time capability

### Advanced Demo: Discord/VTT Integration

To show integration with Discord or Virtual Tabletop:

1. Set up a virtual audio cable (VB-Audio, BlackHole, etc.)
2. Select virtual cable as output in DnD Speaker
3. Set Discord/VTT to use virtual cable as input
4. Run DnD Speaker and speak - others will hear transformed voice

This demonstrates the practical use case for online D&D sessions!


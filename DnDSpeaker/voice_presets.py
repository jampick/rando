"""Voice presets for different character types."""
from typing import Dict, Any

# Voice preset definitions
# Each preset contains parameters for pitch, formant, speed, filters, and effects

VOICE_PRESETS: Dict[str, Dict[str, Any]] = {
    "Goblin": {
        "pitch_shift": 1.4,  # Higher pitch
        "formant_shift": 1.3,  # Higher formants (bright, nasal)
        "speed": 1.15,  # Faster speech
        "low_cut": 200,  # Remove low frequencies
        "high_boost": 1.2,  # Boost high frequencies (scratchy)
        "resonance": 0.1,  # Light resonance
        "reverb": 0.0,  # No reverb
        "distortion": 0.05,  # Slight distortion for scratchiness
    },
    "Dragon": {
        "pitch_shift": 0.65,  # Much lower pitch
        "formant_shift": 0.75,  # Lower formants (deep, resonant)
        "speed": 0.85,  # Slower, more deliberate
        "low_boost": 1.4,  # Strong low frequency boost
        "high_cut": 4000,  # Cut high frequencies
        "resonance": 0.3,  # Strong resonance
        "reverb": 0.25,  # Heavy reverb (echoing)
        "distortion": 0.0,
    },
    "Lich": {
        "pitch_shift": 0.9,  # Slightly lower
        "formant_shift": 0.85,  # Lower formants (unnatural)
        "speed": 0.95,  # Slightly slower
        "low_cut": 150,
        "high_cut": 6000,
        "resonance": 0.2,  # Ethereal resonance
        "reverb": 0.15,  # Moderate reverb (ethereal)
        "distortion": 0.0,
        "tremolo": 0.1,  # Slight tremolo (unnatural)
        "phaser": 0.15,  # Phaser effect (cold, unnatural)
    },
    "Noble Elf": {
        "pitch_shift": 1.1,  # Slightly higher
        "formant_shift": 1.15,  # Higher formants (bright, elegant)
        "speed": 1.0,  # Normal speed
        "low_cut": 100,
        "high_boost": 1.1,  # Slight high boost (smooth, bright)
        "resonance": 0.05,  # Light resonance
        "reverb": 0.05,  # Light reverb (elegant)
        "distortion": 0.0,
    },
    "Warforged": {
        "pitch_shift": 0.95,  # Slightly lower
        "formant_shift": 0.9,  # Lower formants (metallic)
        "speed": 1.0,
        "low_cut": 200,
        "high_cut": 5000,
        "resonance": 0.25,  # Metallic resonance
        "reverb": 0.1,  # Moderate reverb (resonant)
        "distortion": 0.1,  # Mechanical distortion
        "ring_mod": 0.08,  # Ring modulation (metallic)
    },
    "Neutral Narrator": {
        "pitch_shift": 1.0,  # No pitch change
        "formant_shift": 1.0,  # No formant change
        "speed": 1.0,  # Normal speed
        "low_cut": 80,  # Light noise gate
        "high_cut": None,  # No high cut
        "resonance": 0.0,
        "reverb": 0.0,
        "distortion": 0.0,
        "clean_boost": 1.05,  # Slight clean boost
    },
}


def get_preset(name: str) -> Dict[str, Any]:
    """Get a voice preset by name."""
    return VOICE_PRESETS.get(name, VOICE_PRESETS["Neutral Narrator"])


def list_presets() -> list:
    """Get list of available voice preset names."""
    return list(VOICE_PRESETS.keys())


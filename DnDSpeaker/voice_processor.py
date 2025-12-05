"""Real-time voice transformation processor."""
import numpy as np
from scipy import signal  # type: ignore
from typing import Optional, Dict, Any
import collections


class VoiceProcessor:
    """Processes audio in real-time to transform voice characteristics."""
    
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Buffer for overlap-add processing
        self.buffer_size = chunk_size * 2
        self.overlap_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.output_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        
        # Reverb delay line
        self.reverb_buffer_size = int(sample_rate * 0.1)  # 100ms delay
        self.reverb_buffer = collections.deque(maxlen=self.reverb_buffer_size)
        for _ in range(self.reverb_buffer_size):
            self.reverb_buffer.append(0.0)
        self.reverb_pos = 0
        
        # Phaser state
        self.phaser_buffer = collections.deque(maxlen=int(sample_rate * 0.05))
        for _ in range(int(sample_rate * 0.05)):
            self.phaser_buffer.append(0.0)
        self.phaser_lfo = 0.0
        
        # Tremolo state
        self.tremolo_phase = 0.0
        
        # Current preset
        self.current_preset: Optional[Dict[str, Any]] = None
        
        # Design filters once (will be updated when preset changes)
        self.low_cut_filter = None
        self.high_cut_filter = None
        self.low_boost_filter = None
        self.high_boost_filter = None
        
    def set_preset(self, preset: Dict[str, Any]):
        """Set the current voice preset."""
        self.current_preset = preset
        self._update_filters()
    
    def _update_filters(self):
        """Update filter coefficients based on current preset."""
        if not self.current_preset:
            return
        
        # Low cut filter
        low_cut = self.current_preset.get("low_cut")
        if low_cut:
            nyquist = self.sample_rate / 2
            low_cut_norm = low_cut / nyquist
            self.low_cut_filter = signal.butter(2, low_cut_norm, btype='high', output='sos')
        else:
            self.low_cut_filter = None
        
        # High cut filter
        high_cut = self.current_preset.get("high_cut")
        if high_cut:
            nyquist = self.sample_rate / 2
            high_cut_norm = high_cut / nyquist
            self.high_cut_filter = signal.butter(2, high_cut_norm, btype='low', output='sos')
        else:
            self.high_cut_filter = None
        
        # Low boost (shelving filter)
        low_boost = self.current_preset.get("low_boost", 1.0)
        if low_boost != 1.0:
            # Simple low shelf using IIR
            freq = 200
            nyquist = self.sample_rate / 2
            freq_norm = freq / nyquist
            # Use a simple approach with biquad
            self.low_boost_filter = {"gain": low_boost, "freq": freq_norm}
        else:
            self.low_boost_filter = None
        
        # High boost
        high_boost = self.current_preset.get("high_boost", 1.0)
        if high_boost != 1.0:
            freq = 3000
            nyquist = self.sample_rate / 2
            freq_norm = freq / nyquist
            self.high_boost_filter = {"gain": high_boost, "freq": freq_norm}
        else:
            self.high_boost_filter = None
    
    def process(self, audio_chunk: np.ndarray) -> np.ndarray:
        """Process an audio chunk and return transformed audio."""
        if self.current_preset is None:
            return audio_chunk
        
        # Normalize to [-1, 1] range based on input dtype
        if audio_chunk.dtype == np.int16:
            audio_chunk = audio_chunk.astype(np.float32) / 32768.0
        elif audio_chunk.dtype == np.int32:
            audio_chunk = audio_chunk.astype(np.float32) / 2147483648.0
        elif audio_chunk.dtype != np.float32:
            # For other types, convert to float32 (assume already normalized)
            audio_chunk = audio_chunk.astype(np.float32)
        
        # Apply processing pipeline
        processed = audio_chunk.copy()
        
        # 1. Speed adjustment (resample)
        speed = self.current_preset.get("speed", 1.0)
        if speed != 1.0:
            num_samples = len(processed)
            indices = np.linspace(0, num_samples - 1, int(num_samples / speed))
            processed = np.interp(indices, np.arange(num_samples), processed)
        
        # 2. Pitch shifting (using PSOLA-like approach)
        pitch_shift = self.current_preset.get("pitch_shift", 1.0)
        if pitch_shift != 1.0:
            processed = self._pitch_shift(processed, pitch_shift)
        
        # 3. Formant shifting (spectral envelope manipulation)
        formant_shift = self.current_preset.get("formant_shift", 1.0)
        if formant_shift != 1.0:
            processed = self._formant_shift(processed, formant_shift)
        
        # 4. Apply filters
        if self.low_cut_filter is not None:
            processed = signal.sosfilt(self.low_cut_filter, processed)
        
        if self.high_cut_filter is not None:
            processed = signal.sosfilt(self.high_cut_filter, processed)
        
        if self.low_boost_filter is not None:
            processed = self._apply_shelving_filter(processed, self.low_boost_filter, "low")
        
        if self.high_boost_filter is not None:
            processed = self._apply_shelving_filter(processed, self.high_boost_filter, "high")
        
        # 5. Resonance (comb filter)
        resonance = self.current_preset.get("resonance", 0.0)
        if resonance > 0:
            processed = self._apply_resonance(processed, resonance)
        
        # 6. Distortion
        distortion = self.current_preset.get("distortion", 0.0)
        if distortion > 0:
            processed = self._apply_distortion(processed, distortion)
        
        # 7. Ring modulation (for Warforged)
        ring_mod = self.current_preset.get("ring_mod", 0.0)
        if ring_mod > 0:
            processed = self._apply_ring_modulation(processed, ring_mod)
        
        # 8. Phaser (for Lich)
        phaser = self.current_preset.get("phaser", 0.0)
        if phaser > 0:
            processed = self._apply_phaser(processed, phaser)
        
        # 9. Tremolo (for Lich)
        tremolo = self.current_preset.get("tremolo", 0.0)
        if tremolo > 0:
            processed = self._apply_tremolo(processed, tremolo)
        
        # 10. Reverb
        reverb = self.current_preset.get("reverb", 0.0)
        if reverb > 0:
            processed = self._apply_reverb(processed, reverb)
        
        # 11. Clean boost (for Neutral)
        clean_boost = self.current_preset.get("clean_boost", 1.0)
        if clean_boost != 1.0:
            processed = processed * clean_boost
        
        # Ensure output is correct length
        if len(processed) > self.chunk_size:
            processed = processed[:self.chunk_size]
        elif len(processed) < self.chunk_size:
            # Pad with zeros if needed
            padded = np.zeros(self.chunk_size, dtype=np.float32)
            padded[:len(processed)] = processed
            processed = padded
        
        # Prevent clipping
        processed = np.clip(processed, -1.0, 1.0)
        
        return processed
    
    def _pitch_shift(self, audio: np.ndarray, shift: float) -> np.ndarray:
        """Simple pitch shifting using resampling."""
        # For real-time, use a simple resampling approach
        # More sophisticated methods would use phase vocoder, but this is faster
        indices = np.linspace(0, len(audio) - 1, int(len(audio) * shift))
        shifted = np.interp(indices, np.arange(len(audio)), audio)
        
        # Resample back to original length
        if len(shifted) != len(audio):
            indices_back = np.linspace(0, len(shifted) - 1, len(audio))
            shifted = np.interp(indices_back, np.arange(len(shifted)), shifted)
        
        return shifted
    
    def _formant_shift(self, audio: np.ndarray, shift: float) -> np.ndarray:
        """Formant shifting using spectral envelope manipulation."""
        # Use FFT-based approach for formant shifting
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
        
        # Shift formants by scaling frequency axis
        new_freqs = freqs * shift
        new_freqs = np.clip(new_freqs, 0, self.sample_rate / 2)
        
        # Interpolate magnitude and phase
        magnitude = np.abs(fft)
        phase = np.angle(fft)
        
        # Simple interpolation (could be improved)
        new_magnitude = np.interp(new_freqs, freqs, magnitude)
        new_phase = np.interp(new_freqs, freqs, phase)
        
        # Reconstruct
        new_fft = new_magnitude * np.exp(1j * new_phase)
        shifted = np.fft.irfft(new_fft, len(audio))
        
        return shifted.astype(np.float32)
    
    def _apply_shelving_filter(self, audio: np.ndarray, filter_params: Dict, shelf_type: str) -> np.ndarray:
        """Apply a shelving filter (simplified)."""
        gain = filter_params["gain"]
        freq_norm = filter_params["freq"]
        
        # Simple IIR shelving filter approximation
        # This is a simplified version - a full implementation would use proper biquad
        if shelf_type == "low":
            # Boost/cut low frequencies
            # Simple approach: apply gain to frequencies below cutoff
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
            cutoff = freq_norm * self.sample_rate / 2
            
            mask = freqs < cutoff
            fft[mask] *= gain
            
            filtered = np.fft.irfft(fft, len(audio))
        else:  # high
            fft = np.fft.rfft(audio)
            freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)
            cutoff = freq_norm * self.sample_rate / 2
            
            mask = freqs > cutoff
            fft[mask] *= gain
            
            filtered = np.fft.irfft(fft, len(audio))
        
        return filtered.astype(np.float32)
    
    def _apply_resonance(self, audio: np.ndarray, resonance: float) -> np.ndarray:
        """Apply resonance using a comb filter."""
        # Simple comb filter for resonance
        delay_samples = int(self.sample_rate * 0.01)  # 10ms delay
        if delay_samples < 1:
            delay_samples = 1
        
        # Use a simple delay line
        delayed = np.zeros_like(audio)
        if delay_samples < len(audio):
            delayed[delay_samples:] = audio[:-delay_samples]
        
        # Mix original with delayed (feedback)
        return audio + delayed * resonance
    
    def _apply_distortion(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Apply soft distortion."""
        # Soft clipping
        threshold = 0.7
        distorted = np.tanh(audio * (1.0 + amount * 2.0))
        return (1.0 - amount) * audio + amount * distorted
    
    def _apply_ring_modulation(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Apply ring modulation for metallic effect."""
        # Generate carrier frequency
        carrier_freq = 200  # Hz
        t = np.arange(len(audio)) / self.sample_rate
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        
        # Ring modulation: multiply signal with carrier
        modulated = audio * carrier
        
        # Mix with original
        return (1.0 - amount) * audio + amount * modulated
    
    def _apply_phaser(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Apply phaser effect."""
        # Simple phaser using all-pass filter approximation
        # Update LFO
        lfo_rate = 0.5  # Hz
        self.phaser_lfo += 2 * np.pi * lfo_rate / self.sample_rate * len(audio)
        if self.phaser_lfo > 2 * np.pi:
            self.phaser_lfo -= 2 * np.pi
        
        # Modulate delay
        delay = 0.005 + 0.003 * np.sin(self.phaser_lfo)  # 5-8ms delay
        delay_samples = int(delay * self.sample_rate)
        
        # Simple all-pass approximation
        if delay_samples > 0 and delay_samples < len(audio):
            phased = audio.copy()
            phased[delay_samples:] += audio[:-delay_samples] * 0.5
            return (1.0 - amount) * audio + amount * phased
        
        return audio
    
    def _apply_tremolo(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Apply tremolo (amplitude modulation)."""
        tremolo_rate = 5.0  # Hz
        t = np.arange(len(audio)) / self.sample_rate
        self.tremolo_phase += 2 * np.pi * tremolo_rate / self.sample_rate * len(audio)
        if self.tremolo_phase > 2 * np.pi:
            self.tremolo_phase -= 2 * np.pi
        
        modulation = 1.0 + amount * np.sin(2 * np.pi * tremolo_rate * t + self.tremolo_phase)
        return audio * modulation
    
    def _apply_reverb(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Apply simple reverb using delay line."""
        reverb_out = np.zeros_like(audio)
        
        for i, sample in enumerate(audio):
            # Get delayed sample
            delay_pos = (self.reverb_pos - int(self.sample_rate * 0.05)) % self.reverb_buffer_size
            delayed = self.reverb_buffer[delay_pos]
            
            # Mix with current sample
            reverb_out[i] = sample + delayed * amount * 0.5
            
            # Update delay line
            self.reverb_buffer[self.reverb_pos] = reverb_out[i] * 0.7
            self.reverb_pos = (self.reverb_pos + 1) % self.reverb_buffer_size
        
        # Mix reverb with dry signal
        return (1.0 - amount * 0.3) * audio + amount * 0.3 * reverb_out


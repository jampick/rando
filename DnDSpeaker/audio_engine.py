"""Audio engine for real-time capture and playback."""
import pyaudio
import numpy as np
import threading
import queue
from typing import Optional, Callable, List, Tuple


class AudioEngine:
    """Handles real-time audio input and output."""
    
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        
        self.input_device_index: Optional[int] = None
        self.output_device_index: Optional[int] = None
        
        self.input_stream: Optional[pyaudio.Stream] = None
        self.output_stream: Optional[pyaudio.Stream] = None
        
        self.is_running = False
        self.bypass = False
        
        # Audio queues
        self.input_queue = queue.Queue(maxsize=10)
        self.output_queue = queue.Queue(maxsize=10)
        
        # Callback for processed audio
        self.process_callback: Optional[Callable[[np.ndarray], np.ndarray]] = None
        
        # Level monitoring
        self.input_level = 0.0
        self.output_level = 0.0
        
        # Threads
        self.input_thread: Optional[threading.Thread] = None
        self.output_thread: Optional[threading.Thread] = None
    
    def get_input_devices(self) -> List[Tuple[int, str]]:
        """Get list of available input devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append((i, info['name']))
        return devices
    
    def get_output_devices(self) -> List[Tuple[int, str]]:
        """Get list of available output devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                devices.append((i, info['name']))
        return devices
    
    def set_input_device(self, device_index: int):
        """Set the input device."""
        self.input_device_index = device_index
        if self.is_running:
            self.stop()
            self.start()
    
    def set_output_device(self, device_index: int):
        """Set the output device."""
        self.output_device_index = device_index
        if self.is_running:
            self.stop()
            self.start()
    
    def set_process_callback(self, callback: Callable[[np.ndarray], np.ndarray]):
        """Set the audio processing callback."""
        self.process_callback = callback
    
    def set_bypass(self, bypass: bool):
        """Set bypass mode (pass through without processing)."""
        self.bypass = bypass
    
    def _input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input."""
        if status:
            print(f"Input status: {status}")
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Calculate input level
        self.input_level = np.abs(audio_data).max()
        
        # Process audio if callback is set and not bypassed
        if self.process_callback and not self.bypass:
            try:
                processed = self.process_callback(audio_data)
            except Exception as e:
                print(f"Processing error: {e}")
                processed = audio_data
        else:
            processed = audio_data
        
        # Calculate output level
        self.output_level = np.abs(processed).max()
        
        # Convert back to int16
        output_data = (processed * 32768.0).astype(np.int16).tobytes()
        
        return (output_data, pyaudio.paContinue)
    
    def _input_thread_func(self):
        """Input thread function."""
        try:
            self.input_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._input_callback,
            )
            
            self.input_stream.start_stream()
            
            # Keep thread alive
            while self.is_running and self.input_stream.is_active():
                import time
                time.sleep(0.1)
        except Exception as e:
            print(f"Input stream error: {e}")
    
    def _output_thread_func(self):
        """Output thread function (not used with callback, but kept for future use)."""
        pass
    
    def start(self):
        """Start audio processing."""
        if self.is_running:
            return
        
        if self.input_device_index is None or self.output_device_index is None:
            print("Please select input and output devices first")
            return
        
        self.is_running = True
        
        # Start input thread
        self.input_thread = threading.Thread(target=self._input_thread_func, daemon=True)
        self.input_thread.start()
        
        # Open output stream
        try:
            self.output_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.output_device_index,
                frames_per_buffer=self.chunk_size,
            )
        except Exception as e:
            print(f"Error opening output stream: {e}")
            self.stop()
            return
        
        # We need to handle output differently since callback handles both
        # Actually, we'll use a different approach - process in callback and write to output
        # Let me revise this...
    
    def stop(self):
        """Stop audio processing."""
        self.is_running = False
        
        if self.input_stream:
            try:
                self.input_stream.stop_stream()
                self.input_stream.close()
            except Exception:
                pass
            self.input_stream = None
        
        if self.output_stream:
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception:
                pass
            self.output_stream = None
        
        if self.input_thread:
            self.input_thread.join(timeout=1.0)
            self.input_thread = None
    
    def get_input_level(self) -> float:
        """Get current input level (0.0 to 1.0)."""
        return self.input_level
    
    def get_output_level(self) -> float:
        """Get current output level (0.0 to 1.0)."""
        return self.output_level
    
    def cleanup(self):
        """Clean up audio resources."""
        self.stop()
        self.audio.terminate()


# Revised approach: Use separate input/output streams with callback chain
class AudioEngineV2:
    """Improved audio engine with proper input/output separation."""
    
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        
        self.input_device_index: Optional[int] = None
        self.output_device_index: Optional[int] = None
        
        self.input_stream: Optional[pyaudio.Stream] = None
        self.output_stream: Optional[pyaudio.Stream] = None
        
        self.is_running = False
        self.bypass = False
        
        # Audio queue for processed audio
        self.output_queue = queue.Queue(maxsize=20)
        
        # Processing callback
        self.process_callback: Optional[Callable[[np.ndarray], np.ndarray]] = None
        
        # Level monitoring
        self.input_level = 0.0
        self.output_level = 0.0
        
        # Threads
        self.output_thread: Optional[threading.Thread] = None
    
    def get_input_devices(self) -> List[Tuple[int, str]]:
        """Get list of available input devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append((i, info['name']))
        return devices
    
    def get_output_devices(self) -> List[Tuple[int, str]]:
        """Get list of available output devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                devices.append((i, info['name']))
        return devices
    
    def set_input_device(self, device_index: int):
        """Set the input device."""
        self.input_device_index = device_index
        if self.is_running:
            self.stop()
            self.start()
    
    def set_output_device(self, device_index: int):
        """Set the output device."""
        self.output_device_index = device_index
        if self.is_running:
            self.stop()
            self.start()
    
    def set_process_callback(self, callback: Callable[[np.ndarray], np.ndarray]):
        """Set the audio processing callback."""
        self.process_callback = callback
    
    def set_bypass(self, bypass: bool):
        """Set bypass mode."""
        self.bypass = bypass
    
    def _input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input."""
        if status:
            print(f"Input status: {status}")
        
        # Convert to numpy
        audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Update input level
        self.input_level = np.abs(audio_data).max()
        
        # Process if not bypassed
        if not self.bypass and self.process_callback:
            try:
                processed = self.process_callback(audio_data)
            except Exception as e:
                print(f"Processing error: {e}")
                processed = audio_data
        else:
            processed = audio_data
        
        # Update output level
        self.output_level = np.abs(processed).max()
        
        # Queue for output
        try:
            self.output_queue.put_nowait(processed)
        except queue.Full:
            # Drop oldest if queue is full
            try:
                self.output_queue.get_nowait()
                self.output_queue.put_nowait(processed)
            except Exception:
                pass
        
        return (None, pyaudio.paContinue)
    
    def _output_thread_func(self):
        """Output thread that plays processed audio."""
        while self.is_running:
            try:
                # Get processed audio from queue
                processed = self.output_queue.get(timeout=0.1)
                
                # Convert to int16
                output_data = (processed * 32768.0).astype(np.int16).tobytes()
                
                # Write to output stream
                if self.output_stream and self.output_stream.is_active():
                    self.output_stream.write(output_data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Output error: {e}")
    
    def start(self):
        """Start audio processing."""
        if self.is_running:
            return
        
        if self.input_device_index is None or self.output_device_index is None:
            print("Please select input and output devices first")
            return
        
        self.is_running = True
        
        # Open input stream
        try:
            self.input_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._input_callback,
            )
            self.input_stream.start_stream()
        except Exception as e:
            print(f"Error opening input stream: {e}")
            self.stop()
            return
        
        # Open output stream
        try:
            self.output_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.output_device_index,
                frames_per_buffer=self.chunk_size,
            )
        except Exception as e:
            print(f"Error opening output stream: {e}")
            self.stop()
            return
        
        # Start output thread
        self.output_thread = threading.Thread(target=self._output_thread_func, daemon=True)
        self.output_thread.start()
    
    def stop(self):
        """Stop audio processing."""
        self.is_running = False
        
        if self.input_stream:
            try:
                self.input_stream.stop_stream()
                self.input_stream.close()
            except Exception:
                pass
            self.input_stream = None
        
        if self.output_stream:
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception:
                pass
            self.output_stream = None
        
        if self.output_thread:
            self.output_thread.join(timeout=1.0)
            self.output_thread = None
        
        # Clear queue
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except Exception:
                break
    
    def get_input_level(self) -> float:
        """Get current input level."""
        return self.input_level
    
    def get_output_level(self) -> float:
        """Get current output level."""
        return self.output_level
    
    def cleanup(self):
        """Clean up resources."""
        self.stop()
        self.audio.terminate()


# Use the improved version
AudioEngine = AudioEngineV2


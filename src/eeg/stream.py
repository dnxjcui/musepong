import numpy as np
from pylsl import StreamInlet, resolve_byprop
from typing import Optional, Tuple, List


def connect_to_muse() -> tuple[StreamInlet, int]:
    """Connect to Muse EEG stream via LSL."""
    print("Looking for an EEG stream...")
    streams = resolve_byprop('type', 'EEG', timeout=5)
    
    if not streams:
        raise RuntimeError("No EEG stream found. Make sure MuseLSL is running.")
    
    inlet = StreamInlet(streams[0])
    fs = int(inlet.info().nominal_srate())
    print(f"Connected to EEG stream with sampling rate: {fs} Hz")
    
    return inlet, fs


def get_eeg_chunk(inlet: StreamInlet, timeout: float = 1.0, 
                  max_samples: int = 128) -> Tuple[Optional[np.ndarray], Optional[List[float]]]:
    """Pull a chunk of EEG data from the stream."""
    eeg_data, timestamp = inlet.pull_chunk(timeout=timeout, max_samples=max_samples)
    
    if not eeg_data:
        return None, None
    
    return np.array(eeg_data), timestamp


def get_sampling_rate(inlet: StreamInlet) -> int:
    """Get the sampling rate of the EEG stream."""
    return int(inlet.info().nominal_srate())
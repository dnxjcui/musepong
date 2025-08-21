import numpy as np
from scipy import signal
from typing import Tuple, Dict


def bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, 
                   fs: int, order: int = 4) -> np.ndarray:
    """Apply bandpass filter to EEG data."""
    # Skip filtering if data is too short
    if len(data) < 30:  # Minimum length for filter
        return data
        
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    
    b, a = signal.butter(order, [low, high], btype='band')
    
    # Use filtfilt if data is long enough, otherwise use lfilter
    try:
        filtered_data = signal.filtfilt(b, a, data, axis=0)
    except ValueError:
        # Fallback to simple filter if filtfilt fails
        filtered_data = signal.lfilter(b, a, data, axis=0)
    
    return filtered_data


def compute_band_powers(data: np.ndarray, fs: int, 
                       window_length: float = 1.0) -> Dict[str, float]:
    """Compute EEG band powers using FFT."""
    if len(data) == 0:
        return {'delta': 0.0, 'theta': 0.0, 'alpha': 0.0, 'beta': 0.0}
    
    # Use the frontal channels (AF7, AF8) which are most sensitive to blinks
    if data.ndim > 1 and data.shape[1] >= 2:
        frontal_data = np.mean(data[:, 1:3], axis=1)  # AF7, AF8
    else:
        frontal_data = data.flatten()
    
    # Compute power spectral density
    freqs, psd = signal.welch(frontal_data, fs, nperseg=min(len(frontal_data), int(fs * window_length)))
    
    # Define frequency bands
    delta_mask = (freqs >= 1) & (freqs <= 4)
    theta_mask = (freqs >= 4) & (freqs <= 8)
    alpha_mask = (freqs >= 8) & (freqs <= 13)
    beta_mask = (freqs >= 13) & (freqs <= 30)
    
    # Calculate band powers
    band_powers = {
        'delta': np.mean(psd[delta_mask]) if np.any(delta_mask) else 0.0,
        'theta': np.mean(psd[theta_mask]) if np.any(theta_mask) else 0.0,
        'alpha': np.mean(psd[alpha_mask]) if np.any(alpha_mask) else 0.0,
        'beta': np.mean(psd[beta_mask]) if np.any(beta_mask) else 0.0
    }
    
    return band_powers


def preprocess_eeg(data: np.ndarray, fs: int) -> np.ndarray:
    """Basic EEG preprocessing: bandpass filter."""
    if len(data) == 0:
        return data
    
    # Bandpass filter 1-40 Hz to remove DC and high-frequency noise
    filtered_data = bandpass_filter(data, 1.0, 40.0, fs)
    
    return filtered_data
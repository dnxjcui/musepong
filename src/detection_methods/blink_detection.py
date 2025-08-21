import numpy as np
from typing import Dict, Optional
import time


class BlinkDetector:
    def __init__(self, delta_threshold: float = 2.0, alpha_threshold: float = 1.0, 
                 debounce_time: float = 0.3):
        self.delta_threshold = delta_threshold
        self.alpha_threshold = alpha_threshold
        self.debounce_time = debounce_time
        self.last_blink_time = 0
        
    def detect_blink(self, band_powers: Dict[str, float]) -> bool:
        """
        Detect blink using simple thresholding on band powers.
        Blink condition: delta > threshold AND alpha < threshold
        """
        current_time = time.time()
        
        # Check if enough time has passed since last blink (debouncing)
        if current_time - self.last_blink_time < self.debounce_time:
            return False
        
        delta = band_powers.get('delta', 0.0)
        alpha = band_powers.get('alpha', 0.0)
        
        # Simple blink detection: high delta (artifact) and low alpha (eyes closed)
        is_blink = delta > self.delta_threshold and alpha < self.alpha_threshold
        
        if is_blink:
            self.last_blink_time = current_time
            
        return is_blink


def detect_blink_simple(band_powers: Dict[str, float], 
                       delta_threshold: float = 2.0, 
                       alpha_threshold: float = 1.0) -> bool:
    """Simple stateless blink detection function."""
    delta = band_powers.get('delta', 0.0)
    alpha = band_powers.get('alpha', 0.0)
    
    return delta > delta_threshold and alpha < alpha_threshold
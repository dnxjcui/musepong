import numpy as np
from typing import Dict, Optional
import time


class BlinkDetector:
    def __init__(self, delta_threshold: float = 100.0, alpha_threshold: float = 150.0, 
                 debounce_time: float = 0.3):
        self.delta_threshold = delta_threshold
        self.alpha_threshold = alpha_threshold
        self.debounce_time = debounce_time
        self.last_blink_time = 0
        self.alpha = np.zeros(10)
        self.delta = np.zeros(10)
        self.counter = 0
        self.blinked = False
        
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
        # is blink should depend on a running mean of the last 10 samples
        self.alpha[self.counter] = alpha
        self.delta[self.counter] = delta
        self.counter += 1
        if self.counter == len(self.alpha):
            self.counter = 0
        is_blink = (np.mean(self.alpha) > self.alpha_threshold) #and np.mean(self.delta) > self.delta_threshold)

        # self.blinked means we just blinked. It flips to False when we don't detect an active blink. We need self.blinked to be False and is_blink to be True for is_blink to work
        # if is_blink and not self.blinked:
        #     is_blink = True
        # else:
        #     is_blink = False
        is_blink = is_blink and current_time - self.last_blink_time > 2.0

        # print(f"Alpha: {np.mean(self.alpha)}, Delta: {np.mean(self.delta)}")
        if is_blink:
            self.last_blink_time = current_time
            self.blinked = True

        # is_blink = False
        
        return is_blink


def detect_blink_simple(band_powers: Dict[str, float], 
                       delta_threshold: float = 2.0, 
                       alpha_threshold: float = 1.0) -> bool:
    """Simple stateless blink detection function."""
    delta = band_powers.get('delta', 0.0)
    alpha = band_powers.get('alpha', 0.0)
    
    return delta > delta_threshold and alpha < alpha_threshold
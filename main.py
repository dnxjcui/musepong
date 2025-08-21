#!/usr/bin/env python3

import sys
import time
import argparse
import numpy as np
from typing import Optional

# Add src to path
sys.path.append('src')

from eeg.stream import connect_to_muse, get_eeg_chunk, get_sampling_rate
from eeg.processing import preprocess_eeg, compute_band_powers
from detection_methods.blink_detection import BlinkDetector
from game_environments.pong import PongGame


def main():
    parser = argparse.ArgumentParser(description='Muse-Pong: EEG-controlled Pong game')
    parser.add_argument('--simulation', action='store_true', 
                       help='Run in simulation mode (spacebar = blink)')
    parser.add_argument('--npc', action='store_true', 
                       help='Play against AI opponent instead of human player')
    args = parser.parse_args()
    
    simulation_mode = args.simulation
    npc_mode = args.npc
    
    # Initialize game
    game = PongGame(npc_mode=npc_mode)
    
    # Initialize EEG components (only if not in simulation mode)
    inlet = None
    blink_detector = None
    eeg_buffer = []
    buffer_size = 256  # 1 second of data at 256 Hz
    
    if not simulation_mode:
        try:
            print("Connecting to Muse EEG stream...")
            inlet, fs = connect_to_muse()
            blink_detector = BlinkDetector()
            print("EEG connection established!")
        except RuntimeError as e:
            print(f"Failed to connect to EEG stream: {e}")
            print("You can run in simulation mode with --simulation flag")
            game.cleanup()
            return
    else:
        print("Running in simulation mode - press SPACEBAR to blink")
    
    print("Starting Muse-Pong! Blink to move the paddle.")
    if npc_mode:
        print("Playing against AI opponent.")
    else:
        print("Playing against human opponent - use UP/DOWN arrows for right paddle.")
    print("Close the window to quit.")
    
    # Main game loop
    try:
        while game.running:
            blink_detected = False
            
            # Get EEG data and detect blinks (only if not in simulation mode)
            if not simulation_mode and inlet is not None:
                eeg_data, timestamp = get_eeg_chunk(inlet, timeout=0.05, max_samples=128)
                
                if eeg_data is not None and len(eeg_data) > 0:
                    # Add new data to buffer
                    eeg_buffer.extend(eeg_data)
                    
                    # Keep buffer at fixed size
                    if len(eeg_buffer) > buffer_size:
                        eeg_buffer = eeg_buffer[-buffer_size:]
                    
                    # Only process if we have enough data
                    if len(eeg_buffer) >= 64:  # Minimum for processing
                        # Process EEG data
                        processed_data = preprocess_eeg(np.array(eeg_buffer), fs)
                        band_powers = compute_band_powers(processed_data, fs)
                        
                        # Detect blink
                        blink_detected = blink_detector.detect_blink(band_powers)
                        
                        if blink_detected:
                            print("Blink detected!")
            
            # Run one frame of the game
            if not game.run_frame(blink_detected, simulation_mode):
                break
                
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error during game loop: {e}")
    finally:
        game.cleanup()
        print("Game ended")


if __name__ == "__main__":
    main()
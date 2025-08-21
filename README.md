# Muse-Pong

Control a Pong paddle with your blinks using the Muse 2 EEG headband. Features threshold-based blink detection, real-time gameplay, and multiplayer modes.

## Setup

```bash
pip install -r requirements.txt
```

Ensure MuseLSL is running to stream EEG data from your Muse 2 headband.

## Usage

**Basic game modes:**
```bash
python main.py                    # EEG vs Human (UP/DOWN arrows)
python main.py --npc              # EEG vs AI opponent
python main.py --simulation       # Spacebar vs Human (testing mode)
python main.py --simulation --npc # Spacebar vs AI (testing mode)
```

**With EEG calibration:**
```bash
python main.py --calibration      # Calibrate personal blink thresholds
python main.py --calibration --npc # Calibrated EEG vs AI
```

## How it Works

- EEG signals are processed in real-time from the Muse 2's frontal electrodes
- Blinks are detected using simple thresholding on alpha band powers
- Optional calibration records baseline EEG for personalized thresholds
- Each blink alternates paddle direction (up/down)
- Built with pygame for smooth 2D rendering

## Game Mechanics

- **Blink to start**: Each round begins when you blink
- **Paddle control**: Subsequent blinks change paddle direction
- **Multiplayer**: Play against human (keyboard) or AI opponent
- **Scoring**: Immediate round reset after each goal

## Controls

- **Left paddle**: Blink (or Spacebar in simulation mode)
- **Right paddle**: UP/DOWN arrow keys (human mode) or AI-controlled (--npc mode)

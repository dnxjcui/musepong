# Muse-Pong

Control a Pong paddle with your blinks using the Muse 2 EEG headband. Features threshold-based blink detection and real-time gameplay.

## Setup

```bash
pip install -r requirements.txt
```

Ensure MuseLSL is running to stream EEG data from your Muse 2 headband.

## Usage

**With Muse headband:**
```bash
python main.py
```

**Testing/simulation mode:**
```bash
python main.py --simulation
```

## How it Works

- EEG signals are processed in real-time from the Muse 2's frontal electrodes
- Blinks are detected using simple thresholding on delta/alpha band powers
- Each blink alternates paddle direction (up/down)
- Built with PyImGui for lightweight 2D rendering

## Controls

- **Blink** (or **Spacebar** in simulation): Move paddle up/down (alternating)

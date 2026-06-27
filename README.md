# Wizard101 Dance Game Helper

Automatically detects arrow directions in the Wizard101 pet dance minigame and either displays them in an overlay or presses the keys for you.

## How It Works

1. Captures a region of your screen at ~20 FPS
2. Uses OpenCV template matching to detect arrow directions (up/down/left/right)
3. Tracks arrows as they scroll across the screen
4. When an arrow reaches the hit zone, either shows it in an overlay or auto-presses the key

## Requirements

- Python 3.10+
- Windows (Wizard101 is a Windows game)
- Wizard101 running in **windowed mode**

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run calibration (first time only)
python -m src.main --calibrate
```

### Calibration

The calibration wizard walks you through:

1. **Screenshot** — take a screenshot while arrows are visible on screen
2. **Scroll region** — draw a box around where arrows move
3. **Hit zone** — click where arrows need to be pressed
4. **Templates** — draw a box around one of each arrow direction (up, down, left, right)

This saves a `config.json` and template images in the `templates/` folder.

## Usage

### Display Mode (read the arrows yourself)
```bash
python -m src.main --mode display
```
Shows upcoming arrows in a small always-on-top overlay window.

### Auto-Play Mode (presses keys for you)
```bash
python -m src.main --mode auto
```
Automatically presses arrow keys when they reach the hit zone.

### Debug Mode
```bash
python -m src.main --mode display --debug
```
Shows a window with detection rectangles overlaid on the captured screen region.

### Options
```
--calibrate          Run calibration wizard
--mode {display,auto} Output mode (default: display)
--config PATH        Custom config file path
--debug              Show debug detection window
--threshold FLOAT    Override detection confidence (0.0-1.0)
```

## Hotkeys

| Key | Action |
|-----|--------|
| F9  | Toggle auto-play on/off (auto mode only) |
| F10 | Quit the program |

## Troubleshooting

- **No arrows detected**: Try lowering the threshold with `--threshold 0.6`. Run in `--debug` mode to see what's being captured.
- **False detections**: Raise the threshold with `--threshold 0.85`.
- **Wrong region captured**: Re-run `--calibrate` to redefine the screen region.
- **Game window moved**: Re-run `--calibrate` since the capture region is based on absolute screen coordinates.

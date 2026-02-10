# SL - Steam Locomotive

A Python implementation of the classic `sl` terminal animation with transparent background support for Wezterm.

Based on the original [mtoyoda/sl](https://github.com/mtoyoda/sl) written in C.

## Features

- **Faithful Animation**: Perfectly matches the original `sl.c` behavior
  - 6-frame wheel animation
  - 16-stage smoke patterns with parabolic trajectory
  - Smoke updates every 4 frames for smooth continuous animation
  - 40ms per frame (matching original usleep(40000))

- **Transparent Background Support**: Works seamlessly with Wezterm's transparency
  - Tested on Windows 11 with Wezterm + Nushell + Starship
  - ANSI color codes with transparent rendering
  - Perfect for terminal aesthetic enhancement

- **Loop Animation**: Repeat the animation multiple times
  - `-loop` : Infinite loop
  - `-loop N` : Loop N times (e.g., `-loop 3`)

## Installation

### Requirements
- Python 3.6+
- Terminal with ANSI escape sequence support (tested with Wezterm)

### Setup

1. Clone or download this repository
```bash
git clone https://github.com/yourusername/sl.git
cd sl
```

2. Make it executable and accessible
```bash
# On Windows
python sl.py

# Or create an alias in your shell profile
```

## Usage

### Basic Usage
```bash
python sl.py
```

### Loop Animation
```bash
# Infinite loop
python sl.py -loop

# Loop 3 times
python sl.py -loop 3
```

### Help
```bash
python sl.py -h
```

## Wezterm Configuration

To enable transparent background as shown in the original design, add the following to your `wezterm.lua`:

```lua
config.window_background_opacity = 0.65

config.colors = {
    background = "rgba(0,0,0,0.65)",
}
```

## Technical Details

### Python Implementation
This version is a complete Python rewrite of the original C implementation, maintaining pixel-perfect animation compatibility:

- **Locomotive Graphics**: 7 lines of ASCII art for the D51 locomotive
- **Coal Car**: 8-line ASCII art coal car with wheels
- **Wheel Animation**: 6-frame animation cycling
- **Smoke System**:
  - 16 animation stages
  - Dynamic movement with dy/dx tables for parabolic trajectory
  - Smoke particles update every 4 frames
  - Continuous rendering every frame for smooth appearance
  - Automatic cleanup when animation completes

### Frame Timing
- 40ms per frame (40,000 microseconds in original C code)
- Smoke updates occur on frames where `x % 4 == 0`
- Smoke renders every frame for continuous visual effect

### Differences from Original
- Python-based instead of C with curses
- ANSI escape sequences instead of ncurses
- Transparent background support designed for modern terminal emulators
- Command-line argument parsing with argparse

## Code Structure

```
sl.py
├── Configuration (patterns, colors)
├── Drawing Functions (ANSI escape codes)
├── Smoke Class (animation state management)
└── Main Loop (locomotive movement and rendering)
```

## License

Based on the original `sl` by Toyoda Masashi.
See [LICENSE](LICENSE) file for details.

## Credits

- Original author: Toyoda Masashi (mtoyoda@acm.org)
- Python implementation: Inspired by [mtoyoda/sl](https://github.com/mtoyoda/sl)
- Wezterm transparent background adaptation

## Troubleshooting

### Smoke appears flickering
- Ensure your terminal supports ANSI escape sequences
- Try adjusting Wezterm's opacity settings

### Animation appears jittery
- Check that Python is not running in any compatibility mode
- Ensure no other processes are heavily using the CPU

### Transparent background not working
- Verify Wezterm configuration includes the opacity settings
- Restart Wezterm after configuration changes
- Check that terminal background is actually transparent in your OS settings

## Contributing

Feel free to fork this repository and submit pull requests for any improvements!

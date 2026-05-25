# Snake

A classic Snake game built with Python + Pygame, featuring smooth visuals, golden food power-ups, and selectable difficulty.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Pygame](https://img.shields.io/badge/pygame-2.5+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Gameplay

Eat food to grow longer. Avoid hitting walls or yourself. Golden food grants temporary double speed and double growth.

### Difficulty

| Level | Speed | Key |
|-------|-------|-----|
| Slow  | 6     | `1` |
| Normal| 8     | `2` |
| Fast  | 12    | `3` |

Select difficulty on the menu screen before starting.

### Special Mechanic: Golden Food

- Appears randomly every 10–25 seconds (replaces normal food while active)
- Glows and pulses with a star-shaped animation
- Eating it: **+50 points** + **10-second boost** (speed ×2, growth ×2)
- Boost timer shown as a gold bar at top-right

## Controls

| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` / `W` `A` `S` `D` | Move |
| `Space` / `P` | Pause / Resume |
| `R` | Restart (after game over) |
| `Esc` | Quit |
| `1` `2` `3` | Select difficulty (menu) |

## Quick Start

### Option 1: Download Executable (Windows)

Download `Snake.exe` from the [Releases](../../releases) page — no Python required.

### Option 2: Run from Source

```bash
pip install -r requirements.txt
python main.py
```

## Build

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name "Snake" --clean \
    --exclude-module numpy --exclude-module scipy \
    --exclude-module pandas --exclude-module matplotlib \
    --exclude-module PIL --exclude-module tkinter \
    main.py
```

The executable will be at `dist/Snake.exe` (~17 MB).

## Project Structure

```
snake/
├── main.py           # Entry point: init, event loop, IME-safe input
├── config.py         # Constants, enums, colors, key bindings
├── snake.py          # Snake entity: body, direction, growth
├── food.py           # Food + GoldenFood entities
├── score.py          # Score persistence (JSON)
├── game.py           # State machine, collision, timers, particles
├── renderer.py       # All drawing: gradient body, eyes, glow, HUD
├── requirements.txt  # pygame>=2.5.0
└── CLAUDE.md         # Coding standards for AI-assisted development
```

### Architecture

- **Entity-data separation** — `snake.py` and `food.py` contain only data and behavior, no pygame imports
- **Single renderer** — all `pygame.draw` calls live in `renderer.py`
- **Config-driven** — all tunable values in `config.py`
- **State machine** — `MENU → PLAYING → PAUSED / GAME_OVER`
- **Decoupled tick** — renders at 60 FPS, game logic ticks at variable speed

## Tech Stack

- Python 3.10+
- Pygame 2.5+
- PyInstaller (for packaging)

## License

MIT

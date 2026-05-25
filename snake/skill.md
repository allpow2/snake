---
name: pygame-snake-dev
description: This skill should be used when the user asks to create a snake game, make a 贪吃蛇, build a classic retro snake, or develop a snake game variant in Python with Pygame. Covers modular architecture: config → snake entity → food/golden food system → state machine → renderer with gradient body, eyes, particles → main loop with IME-safe input. Reference implementation at snack/ project.
---

# Pygame Snake Game Development

Build a polished snake game in Python + Pygame. Follows the workflow: plan.md → CLAUDE.md → step-by-step implementation.

## Reference Implementation

The `snack/` project is the canonical implementation:

```
snack/
├── plan.md           # Requirements + architecture plan
├── CLAUDE.md         # Coding standards (read before writing code)
├── config.py         # All constants, enums, colors, key bindings
├── snake.py          # Snake entity: body list, direction, growth, visual state
├── food.py           # Food + GoldenFood: position, spawn logic
├── score.py          # Score persistence to JSON
├── game.py           # State machine, collision, golden food timer, particles
├── renderer.py       # ALL drawing: gradient body, eyes, glow, particles, HUD
├── main.py           # Init, event loop, IME-safe input, tick accumulator
└── requirements.txt
```

## Snake Game Architecture

### 1. Snake Entity (snake.py)

The snake is a list of grid coordinates, head-first:

```python
class Snake:
    body: list[tuple[int, int]]       # body[0] = head
    direction: Direction
    _pending_growth: int              # deferred growth counter
    prev_tail: tuple[int, int] | None # for smooth interpolation
    has_eaten: bool                   # triggers eating animation

    def set_direction(self, new: Direction) -> None:
        if new != DIRECTION_OPPOSITES[self.direction]:
            self.direction = new

    def move(self) -> None:
        self.prev_tail = self.body[-1]
        self.has_eaten = False
        new_head = (head[0] + dx, head[1] + dy)
        self.body.insert(0, new_head)
        if self._pending_growth > 0:
            self._pending_growth -= 1  # keep tail → grow
        else:
            self.body.pop()            # remove tail → constant length

    def grow(self, amount: int = 1) -> None:
        self._pending_growth += amount
        self.has_eaten = True
```

Key pattern: **growth via deferred counter** — `grow()` increments counter, `move()` consults it. Enables multi-segment growth (golden food = 2 segments).

### 2. Food System (food.py)

Two food types, **only one visible at a time**:

```python
class Food:
    position: tuple[int, int]
    def respawn(self, snake_body, extra_occupied=None) -> None:
        occupied = set(snake_body) | (extra_occupied or set())
        available = [(c,r) for c in range(COLS) for r in range(ROWS)
                     if (c,r) not in occupied]
        self.position = random.choice(available)

class GoldenFood:
    position: tuple[int, int]
    active: bool
    def spawn(self, snake_body, normal_food_pos) -> None:
        # Avoid snake body AND normal food position
    def deactivate(self) -> None:
        self.active = False
```

**Golden food timing logic** (in game.py):
- Timer counts each game tick (paused during boost)
- Spawns when timer ≥ random interval (10–25s), no boost, no active golden food
- On spawn: golden food appears, normal food hidden (renderer skips it)
- On eat: +50 points, 10s boost (speed ×2 + growth ×2), particles, timer reset
- After eat: normal food respawns, golden food deactivated

### 3. State Machine

```
MENU ──(direction key)──→ PLAYING ──(death)──→ GAME_OVER
                              │                     │
                              └──(Space/P)──→ PAUSE │
                                                    │
                              ←──(R)── restart ──────┘
```

State transitions centrally in `Game.handle_input()`. Each state only responds to its own key subset.

### 4. Renderer — Snake Visuals

**Body**: rounded rectangles (`border_radius=CELL_SIZE//2`). Color gradient from head (bright) to tail (dark) via lerp. Boost mode: brighter palette + red pupils.

**Eyes**: two small circles offset perpendicular to movement direction + forward offset. White circle + dark pupil. Boost mode: red pupil.

**Smooth movement**: `_interpolate_body()` shifts each segment toward the next one by `interp` (0–1). Tail interpolates to `prev_tail` (unless snake just ate → tail didn't move).

**Golden food**: animated star polygon (10 points, alternating radii) with pulsing glow (sin-based radius + alpha oscillation). Rotates over time.

### 5. Particle System

```python
@dataclass
class Particle:
    x: float; y: float       # grid coordinates
    vx: float; vy: float     # velocity in grid units/tick
    lifetime: float           # seconds
    color: tuple[int,int,int]

# Triggered on eating food — circular burst of 10 particles
```

### 6. Main Loop & Chinese IME Fix

```python
def main():
    pygame.init()
    pygame.key.stop_text_input()  # CRITICAL: prevents IME key interception

    while not game.should_quit:
        dt = clock.tick(60)       # render at 60 FPS

        for event in pygame.event.get():
            game.handle_input(event)  # KEYDOWN events

        keys = pygame.key.get_pressed()
        game.handle_held_keys(keys)   # fallback for IME (WASD/R)

        # Tick accumulator: game.update() at game.speed Hz
        tick_accumulator += dt
        while tick_accumulator >= 1000/game.speed:
            game.update()
            tick_accumulator -= 1000/game.speed

        interp = tick_accumulator / (1000/game.speed)
        renderer.render(game, interp)  # smooth interpolation
        pygame.display.flip()
```

**Why dual input**: Chinese IME on Windows can consume `KEYDOWN` events. `pygame.key.get_pressed()` bypasses IME. Use both: KEYDOWN for pause/quit precision, `get_pressed` as fallback for WASD/R in menu/game-over.

### 7. Difficulty Progression

- `base_speed` starts at 10. Every 5 foods eaten → +1.
- Effective `speed` = `base_speed × 2` during boost, else `base_speed`.
- Boost lasts 10 real-time seconds (converted to game ticks at activation).

## Snake-Specific Patterns

### Anti-reverse direction
```python
DIRECTION_OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
# Reject new direction == DIRECTION_OPPOSITES[current]
```

### Grid neighbor positions
```python
dx, dy = direction.value
front = (head[0]+dx, head[1]+dy)
left  = (head[0]-dy, head[1]+dx)   # perpendicular
right = (head[0]+dy, head[1]-dx)   # perpendicular
```

### Food spawn: set for O(1) lookup
```python
occupied = set(snake_body)
available = [(c,r) for c in range(COLS) for r in range(ROWS) if (c,r) not in occupied]
```

### Smooth tail handling
When `has_eaten=True`, the tail didn't move this tick — skip interpolation for the last segment.

## Workflow

1. **Clarify**: any special food types? visual style? unique mechanics?
2. **Create plan.md**: follow the reference structure.
3. **Create CLAUDE.md**: adapt from snack/CLAUDE.md.
4. **Implement in order**: config → snake → food → score → game → renderer → main.
5. **Verify**: `python -m py_compile *.py` → `python main.py`.

## Key Principles

- **Body is `list[tuple[int,int]]` head-first** — insert at 0, pop from end
- **Growth is deferred** — `grow()` sets flag, `move()` acts on it
- **Entities never import pygame** — all rendering in renderer.py
- **Grid in entities, pixels in renderer**
- **`pygame.key.stop_text_input()` always**
- **Only one food visible at a time** (golden OR normal)
- **Chinese responses**

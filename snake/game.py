from __future__ import annotations

import random
import math
from dataclasses import dataclass

import pygame

from config import (
    DIFFICULTY_OPTIONS,
    DEFAULT_DIFFICULTY_INDEX,
    SPEED_INCREMENT,
    FOODS_PER_SPEEDUP,
    GOLDEN_FOOD_MIN_INTERVAL,
    GOLDEN_FOOD_MAX_INTERVAL,
    GOLDEN_FOOD_SCORE,
    GOLDEN_FOOD_BOOST_DURATION,
    GOLDEN_FOOD_SPEED_MULTIPLIER,
    GOLDEN_FOOD_GROWTH,
    PARTICLE_COUNT,
    PARTICLE_LIFETIME,
    PARTICLE_SPEED,
    COLOR_GOLDEN_PARTICLE,
    COLOR_FOOD_PARTICLE,
    GameState,
    KEY_DIRECTION_MAP,
    KEY_PAUSE,
    KEY_RESTART,
    KEY_QUIT,
)
from snake import Snake
from food import Food, GoldenFood
from score import ScoreManager


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    color: tuple[int, int, int]


class Game:
    def __init__(self) -> None:
        self.snake = Snake()
        self.food = Food()
        self.golden_food = GoldenFood()
        self.score_manager = ScoreManager()
        self.state: GameState = GameState.MENU
        self.difficulty_index: int = DEFAULT_DIFFICULTY_INDEX
        self.base_speed: int = DIFFICULTY_OPTIONS[DEFAULT_DIFFICULTY_INDEX]["speed"]
        self.foods_eaten: int = 0
        self._should_quit: bool = False

        self.boost_ticks: int = 0
        self._golden_timer: float = 0.0
        self._golden_interval: float = self._random_golden_interval()
        self._last_direction_key: int | None = None

        self.particles: list[Particle] = []
        self.golden_pulse: float = 0.0

        self.food.respawn(self.snake.body)

    @property
    def speed(self) -> int:
        if self.boost_active:
            return self.base_speed * GOLDEN_FOOD_SPEED_MULTIPLIER
        return self.base_speed

    @property
    def should_quit(self) -> bool:
        return self._should_quit

    @property
    def boost_active(self) -> bool:
        return self.boost_ticks > 0

    @property
    def boost_progress(self) -> float:
        if not self.boost_active:
            return 0.0
        total = GOLDEN_FOOD_BOOST_DURATION * self.base_speed * GOLDEN_FOOD_SPEED_MULTIPLIER
        return min(self.boost_ticks / total, 1.0) if total > 0 else 0.0

    @property
    def golden_active(self) -> bool:
        return self.golden_food.active

    def _random_golden_interval(self) -> float:
        return random.uniform(GOLDEN_FOOD_MIN_INTERVAL, GOLDEN_FOOD_MAX_INTERVAL)

    def force_quit(self) -> None:
        self._should_quit = True
        self.score_manager.save()

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        key = event.key

        if key in KEY_QUIT:
            self._should_quit = True
            return

        if self.state == GameState.MENU:
            for i, opt in enumerate(DIFFICULTY_OPTIONS):
                if key == opt["key"]:
                    self.difficulty_index = i
                    self.base_speed = opt["speed"]
                    return
            if key in KEY_DIRECTION_MAP:
                self.snake.set_direction(KEY_DIRECTION_MAP[key])
                self.state = GameState.PLAYING

        elif self.state == GameState.PLAYING:
            if key in KEY_DIRECTION_MAP:
                self.snake.set_direction(KEY_DIRECTION_MAP[key])
            elif key in KEY_PAUSE:
                self.state = GameState.PAUSED

        elif self.state == GameState.PAUSED:
            if key in KEY_PAUSE:
                self.state = GameState.PLAYING

        elif self.state == GameState.GAME_OVER:
            if key in KEY_RESTART:
                self._restart()

    def handle_held_keys(self, keys: pygame.key.ScancodeWrapper) -> None:
        if self.state == GameState.MENU:
            for scan_key, direction in KEY_DIRECTION_MAP.items():
                if keys[scan_key]:
                    self.snake.set_direction(direction)
                    self.state = GameState.PLAYING
                    return

        elif self.state == GameState.GAME_OVER:
            for scan_key in KEY_RESTART:
                if keys[scan_key]:
                    self._restart()
                    return

    def update(self) -> None:
        self.golden_pulse += 0.05

        for p in self.particles[:]:
            p.lifetime -= 1 / self.speed
            if p.lifetime <= 0:
                self.particles.remove(p)
            else:
                p.x += p.vx / self.speed
                p.y += p.vy / self.speed

        if self.state != GameState.PLAYING:
            return

        if self.boost_active:
            self.boost_ticks -= 1

        if self.golden_food.active:
            pass
        elif not self.boost_active:
            self._golden_timer += 1.0
            if self._golden_timer >= self._golden_interval:
                self.golden_food.spawn(self.snake.body, self.food.position)
                self._golden_timer = 0.0

        self.snake.move()

        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.state = GameState.GAME_OVER
            self.golden_food.deactivate()
            self.boost_ticks = 0
            self.score_manager.save()
            return

        if self.golden_food.active and self.snake.head == self.golden_food.position:
            self.snake.grow(GOLDEN_FOOD_GROWTH)
            self.score_manager.add_score(GOLDEN_FOOD_SCORE)
            self._emit_particles(self.golden_food.position, COLOR_GOLDEN_PARTICLE)
            self.boost_ticks = int(GOLDEN_FOOD_BOOST_DURATION * self.base_speed * GOLDEN_FOOD_SPEED_MULTIPLIER)
            self.golden_food.deactivate()
            self._golden_timer = 0.0
            self._golden_interval = self._random_golden_interval()
            self.food.respawn(self.snake.body)
            return

        if not self.golden_food.active and self.snake.head == self.food.position:
            growth = GOLDEN_FOOD_GROWTH if self.boost_active else 1
            self.snake.grow(growth)
            self.score_manager.add_score(10)
            self._emit_particles(self.food.position, COLOR_FOOD_PARTICLE)
            self.foods_eaten += 1
            self.food.respawn(self.snake.body)
            if self.foods_eaten % FOODS_PER_SPEEDUP == 0:
                self.base_speed += SPEED_INCREMENT

    def _emit_particles(self, position: tuple[int, int], color: tuple[int, int, int]) -> None:
        col, row = position
        cx = col + 0.5
        cy = row + 0.5
        for i in range(PARTICLE_COUNT):
            angle = (2 * math.pi * i) / PARTICLE_COUNT
            spd = PARTICLE_SPEED * random.uniform(0.6, 1.4)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            self.particles.append(Particle(cx, cy, vx, vy, PARTICLE_LIFETIME, color))

    def _restart(self) -> None:
        self.snake = Snake()
        self.food = Food()
        self.golden_food = GoldenFood()
        self.score_manager.reset()
        self.base_speed = DIFFICULTY_OPTIONS[self.difficulty_index]["speed"]
        self.foods_eaten = 0
        self.boost_ticks = 0
        self._golden_timer = 0.0
        self._golden_interval = self._random_golden_interval()
        self.particles.clear()
        self.food.respawn(self.snake.body)
        self.state = GameState.MENU

from enum import Enum
import os
import math

import pygame


# --- 屏幕 & 网格 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 20
COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

# --- 难度 ---
DIFFICULTY_OPTIONS = [
    {"label": "Slow",   "speed": 6,  "key": pygame.K_1},
    {"label": "Normal", "speed": 8, "key": pygame.K_2},
    {"label": "Fast",   "speed": 12, "key": pygame.K_3},
]
DEFAULT_DIFFICULTY_INDEX = 1

# --- 游戏参数 ---
SPEED_INCREMENT = 1
FOODS_PER_SPEEDUP = 5
INITIAL_LENGTH = 3

# --- 金色食物 ---
GOLDEN_FOOD_MIN_INTERVAL = 15
GOLDEN_FOOD_MAX_INTERVAL = 30
GOLDEN_FOOD_SCORE = 50
GOLDEN_FOOD_BOOST_DURATION = 10
GOLDEN_FOOD_SPEED_MULTIPLIER = 2
GOLDEN_FOOD_GROWTH = 2

# --- 方向 ---
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

DIRECTION_OPPOSITES: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

# --- 游戏状态 ---
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

# --- 按键映射 ---
KEY_DIRECTION_MAP: dict[int, Direction] = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_w: Direction.UP,
    pygame.K_s: Direction.DOWN,
    pygame.K_a: Direction.LEFT,
    pygame.K_d: Direction.RIGHT,
}

KEY_PAUSE = {pygame.K_SPACE, pygame.K_p}
KEY_RESTART = {pygame.K_r}
KEY_QUIT = {pygame.K_ESCAPE}

# --- 颜色 ---
COLOR_BG = (15, 15, 28)
COLOR_GRID = (30, 30, 42)
COLOR_SNAKE_HEAD = (80, 230, 80)
COLOR_SNAKE_BODY_START = (60, 200, 60)
COLOR_SNAKE_BODY_END = (20, 110, 28)
COLOR_SNAKE_EYE_WHITE = (255, 255, 255)
COLOR_SNAKE_EYE_PUPIL = (10, 10, 10)
COLOR_SNAKE_BOOST_HEAD = (80, 255, 80)
COLOR_SNAKE_BOOST_BODY_START = (60, 230, 60)
COLOR_SNAKE_BOOST_BODY_END = (30, 150, 40)
COLOR_FOOD = (235, 65, 65)
COLOR_FOOD_GLOW = (255, 140, 140)
COLOR_GOLDEN_FOOD = (255, 215, 0)
COLOR_GOLDEN_FOOD_GLOW = (255, 255, 120)
COLOR_GOLDEN_PARTICLE = (255, 200, 50)
COLOR_FOOD_PARTICLE = (255, 180, 80)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_DIM = (160, 160, 160)
COLOR_OVERLAY_BG = (0, 0, 0, 160)
COLOR_BOOST_BAR = (255, 200, 0)
COLOR_BOOST_BAR_BG = (50, 50, 55)

# --- 字体 ---
FONT_NAME = None
FONT_SIZE_SCORE = 22
FONT_SIZE_OVERLAY = 48
FONT_SIZE_TITLE = 64
FONT_SIZE_HUD = 14

# --- 粒子 ---
PARTICLE_COUNT = 10
PARTICLE_LIFETIME = 0.4
PARTICLE_SPEED = 3.0

# --- 分数存储 ---
SCORE_FILE = os.path.join(os.path.expanduser("~"), ".snake_score.json")

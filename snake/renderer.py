from __future__ import annotations

import math

import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CELL_SIZE,
    COLS,
    ROWS,
    FONT_NAME,
    FONT_SIZE_SCORE,
    FONT_SIZE_OVERLAY,
    FONT_SIZE_TITLE,
    FONT_SIZE_HUD,
    COLOR_BG,
    COLOR_GRID,
    COLOR_SNAKE_HEAD,
    COLOR_SNAKE_BODY_START,
    COLOR_SNAKE_BODY_END,
    COLOR_SNAKE_BOOST_HEAD,
    COLOR_SNAKE_BOOST_BODY_START,
    COLOR_SNAKE_BOOST_BODY_END,
    COLOR_SNAKE_EYE_WHITE,
    COLOR_SNAKE_EYE_PUPIL,
    COLOR_FOOD,
    COLOR_FOOD_GLOW,
    COLOR_GOLDEN_FOOD,
    COLOR_GOLDEN_FOOD_GLOW,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_OVERLAY_BG,
    COLOR_BOOST_BAR,
    COLOR_BOOST_BAR_BG,
    DIFFICULTY_OPTIONS,
    GameState,
    Direction,
)


def _lerp_color(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    t = max(0, min(1, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font_score = pygame.font.Font(FONT_NAME, FONT_SIZE_SCORE)
        self.font_overlay = pygame.font.Font(FONT_NAME, FONT_SIZE_OVERLAY)
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.font_hud = pygame.font.Font(FONT_NAME, FONT_SIZE_HUD)

    def render(self, game, interp: float) -> None:
        self._draw_background()
        self._draw_grid()

        body = game.snake.body
        direction = game.snake.direction

        # 蛇身平滑插值
        interp_body = self._interpolate_body(
            body, game.snake.prev_tail, direction, game.snake.has_eaten, interp
        )

        self._draw_particles(game.particles, interp)
        self._draw_food(game.food.position, game.golden_food.active)
        self._draw_snake(interp_body, direction, game.boost_active, game.snake.has_eaten)
        self._draw_golden_food(game.golden_food, game.golden_pulse, interp_body)
        self._draw_score_panel(game.score_manager.score, game.score_manager.high_score)
        self._draw_boost_bar(game.boost_progress)
        self._draw_overlay(game)

    # ── 背景 ──

    def _draw_background(self) -> None:
        self.screen.fill(COLOR_BG)

    def _draw_grid(self) -> None:
        for col in range(COLS):
            x = col * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for row in range(ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

    # ── 粒子 ──

    def _draw_particles(self, particles, interp: float) -> None:
        for p in particles:
            alpha = int(255 * min(p.lifetime * 3, 1.0))
            px = int(p.x * CELL_SIZE)
            py = int(p.y * CELL_SIZE)
            size = max(1, int(4 * min(p.lifetime * 3, 1.0)))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p.color[:3], alpha), (size, size), size)
            self.screen.blit(surf, (px - size, py - size))

    # ── 食物 ──

    def _draw_food(self, position: tuple[int, int], golden_active: bool) -> None:
        if golden_active:
            return
        col, row = position
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 2
        pygame.draw.circle(self.screen, COLOR_FOOD_GLOW, (cx, cy), r + 2)
        pygame.draw.circle(self.screen, COLOR_FOOD, (cx, cy), r)
        pygame.draw.circle(self.screen, (255, 140, 140), (cx - 2, cy - 2), r // 3)

    # ── 金色食物 ──

    def _draw_golden_food(self, golden_food, pulse: float, snake_body) -> None:
        if not golden_food.active:
            return
        col, row = golden_food.position
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2

        glow_r = CELL_SIZE // 2 + 3 + int(math.sin(pulse * 3) * 4)
        glow_alpha = 100 + int(math.sin(pulse * 4) * 60)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLOR_GOLDEN_FOOD_GLOW[:3], glow_alpha),
                           (glow_r, glow_r), glow_r)
        self.screen.blit(glow_surf, (cx - glow_r, cy - glow_r))

        star_r = CELL_SIZE // 2 - 2
        points = []
        for i in range(10):
            angle = math.pi / 2 + (2 * math.pi * i) / 10 + pulse * 0.5
            r = star_r if i % 2 == 0 else star_r * 0.5
            px = cx + math.cos(angle) * r
            py = cy - math.sin(angle) * r
            points.append((px, py))
        pygame.draw.polygon(self.screen, COLOR_GOLDEN_FOOD, points)

        inner_r = star_r * 0.35
        bright = 255 - int(abs(math.sin(pulse * 2)) * 80)
        inner_color = (255, bright, 50)
        pygame.draw.circle(self.screen, inner_color, (cx, cy), int(inner_r))

    # ── 蛇 ──

    def _interpolate_body(
        self,
        body: list[tuple[int, int]],
        prev_tail: tuple[int, int] | None,
        direction: Direction,
        has_eaten: bool,
        interp: float,
    ) -> list[tuple[float, float]]:
        result: list[tuple[float, float]] = []
        dx, dy = direction.value

        for i, (col, row) in enumerate(body):
            if i == 0:
                fx = col + dx * interp
                fy = row + dy * interp
            else:
                prev = body[i - 1]
                fx = col + (prev[0] - col) * interp
                fy = row + (prev[1] - row) * interp
            result.append((fx, fy))

        if prev_tail is not None and len(result) > 1 and not has_eaten:
            last = result[-1]
            tx = prev_tail[0] + (last[0] - prev_tail[0]) * interp
            ty = prev_tail[1] + (last[1] - prev_tail[1]) * interp
            result[-1] = (tx, ty)

        return result

    def _draw_snake(
        self,
        body: list[tuple[float, float]],
        direction: Direction,
        boost: bool,
        has_eaten: bool,
    ) -> None:
        n = len(body)
        for i, (fx, fy) in enumerate(body):
            t = i / max(n - 1, 1)
            if boost:
                head_c = COLOR_SNAKE_BOOST_HEAD if i == 0 else COLOR_SNAKE_BOOST_BODY_START
                body_start = COLOR_SNAKE_BOOST_BODY_START
                body_end = COLOR_SNAKE_BOOST_BODY_END
            else:
                head_c = COLOR_SNAKE_HEAD
                body_start = COLOR_SNAKE_BODY_START
                body_end = COLOR_SNAKE_BODY_END

            color = head_c if i == 0 else _lerp_color(body_start, body_end, t)

            px = int(fx * CELL_SIZE)
            py = int(fy * CELL_SIZE)
            seg_r = CELL_SIZE // 2 - 1

            rect = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(self.screen, color, rect, border_radius=seg_r)

        # 眼睛
        head_fx, head_fy = body[0]
        self._draw_eyes(head_fx, head_fy, direction, boost)

    def _draw_eyes(
        self, fx: float, fy: float, direction: Direction, boost: bool
    ) -> None:
        cx = int(fx * CELL_SIZE + CELL_SIZE // 2)
        cy = int(fy * CELL_SIZE + CELL_SIZE // 2)
        eye_r = CELL_SIZE // 5
        pupil_r = max(1, eye_r // 2)
        eye_offset = CELL_SIZE // 5
        forward_offset = CELL_SIZE // 6

        dx, dy = direction.value
        perp_x, perp_y = -dy, dx

        for side in (-1, 1):
            ex = cx + dx * forward_offset + perp_x * eye_offset * side
            ey = cy + dy * forward_offset + perp_y * eye_offset * side

            pupil_x = ex + dx * (pupil_r // 2)
            pupil_y = ey + dy * (pupil_r // 2)

            pupil_color = (255, 80, 40) if boost else COLOR_SNAKE_EYE_PUPIL
            eye_white = (255, 255, 200) if boost else COLOR_SNAKE_EYE_WHITE

            pygame.draw.circle(self.screen, eye_white, (ex, ey), eye_r)
            pygame.draw.circle(self.screen, pupil_color, (pupil_x, pupil_y), pupil_r)

    # ── HUD ──

    def _draw_score_panel(self, score: int, high_score: int) -> None:
        text = self.font_score.render(
            f"Score: {score}    Best: {high_score}", True, COLOR_TEXT
        )
        self.screen.blit(text, (10, 8))

    def _draw_boost_bar(self, progress: float) -> None:
        if progress <= 0:
            return
        bar_w = 120
        bar_h = 6
        x = SCREEN_WIDTH - bar_w - 12
        y = 14

        bg_rect = pygame.Rect(x, y, bar_w, bar_h)
        pygame.draw.rect(self.screen, COLOR_BOOST_BAR_BG, bg_rect, border_radius=3)

        fill_w = int(bar_w * progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(x, y, fill_w, bar_h)
            pygame.draw.rect(self.screen, COLOR_BOOST_BAR, fill_rect, border_radius=3)

        label = self.font_hud.render("BOOST", True, COLOR_BOOST_BAR)
        self.screen.blit(label, (x - 48, y - 1))

    # ── 覆盖层 ──

    def _draw_overlay(self, game) -> None:
        state = game.state

        if state == GameState.PLAYING:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY_BG)
        self.screen.blit(overlay, (0, 0))

        if state == GameState.MENU:
            self._draw_menu(game.difficulty_index)
        elif state == GameState.PAUSED:
            self._draw_overlay_text("PAUSED", "Space: continue  |  Esc: quit")
        elif state == GameState.GAME_OVER:
            score = game.score_manager.score
            high = game.score_manager.high_score
            new_best = "  !! NEW BEST!" if score >= high and score > 0 else ""
            self._draw_overlay_text(
                "GAME OVER",
                f"Score: {score}{new_best}    R: restart",
            )

    def _draw_menu(self, selected_index: int) -> None:
        title_surf = self.font_title.render("S N A K E", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        )
        self.screen.blit(title_surf, title_rect)

        option_surfs: list[pygame.Surface] = []
        total_w = 0
        for i, opt in enumerate(DIFFICULTY_OPTIONS):
            color = COLOR_BOOST_BAR if i == selected_index else COLOR_TEXT_DIM
            text = f"[{opt['label']}]" if i == selected_index else f" {opt['label']} "
            surf = self.font_score.render(text, True, color)
            option_surfs.append(surf)
            total_w += surf.get_width()

        gap = 20
        total_w += gap * (len(option_surfs) - 1)
        x = (SCREEN_WIDTH - total_w) // 2
        y = SCREEN_HEIGHT // 2 - 8
        for surf in option_surfs:
            self.screen.blit(surf, (x, y))
            x += surf.get_width() + gap

        speed = DIFFICULTY_OPTIONS[selected_index]["speed"]
        speed_text = f"Speed: {speed}"
        speed_surf = self.font_hud.render(speed_text, True, COLOR_TEXT_DIM)
        speed_rect = speed_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 18)
        )
        self.screen.blit(speed_surf, speed_rect)

        hint_surf = self.font_hud.render(
            "Press 1 / 2 / 3 to change", True, COLOR_TEXT_DIM
        )
        hint_rect = hint_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 36)
        )
        self.screen.blit(hint_surf, hint_rect)

        prompt_surf = self.font_overlay.render(
            "Arrows / WASD  |  Space: pause", True, COLOR_TEXT_DIM
        )
        prompt_rect = prompt_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 68)
        )
        self.screen.blit(prompt_surf, prompt_rect)

    def _draw_overlay_text(self, title: str, subtitle: str) -> None:
        title_surf = self.font_title.render(title, True, COLOR_TEXT)
        subtitle_surf = self.font_overlay.render(subtitle, True, COLOR_TEXT_DIM)

        title_rect = title_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 44)
        )
        subtitle_rect = subtitle_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
        )

        self.screen.blit(title_surf, title_rect)
        self.screen.blit(subtitle_surf, subtitle_rect)

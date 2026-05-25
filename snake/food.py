import random

from config import COLS, ROWS


class Food:
    def __init__(self) -> None:
        self.position: tuple[int, int] = (0, 0)

    def respawn(
        self,
        snake_body: list[tuple[int, int]],
        extra_occupied: set[tuple[int, int]] | None = None,
    ) -> None:
        occupied = set(snake_body)
        if extra_occupied:
            occupied |= extra_occupied
        available = [
            (c, r)
            for c in range(COLS)
            for r in range(ROWS)
            if (c, r) not in occupied
        ]
        self.position = random.choice(available) if available else (0, 0)


class GoldenFood:
    def __init__(self) -> None:
        self.position: tuple[int, int] = (0, 0)
        self.active: bool = False

    def spawn(
        self,
        snake_body: list[tuple[int, int]],
        normal_food_pos: tuple[int, int],
    ) -> None:
        extra = {normal_food_pos}
        occupied = set(snake_body) | extra
        available = [
            (c, r)
            for c in range(COLS)
            for r in range(ROWS)
            if (c, r) not in occupied
        ]
        self.position = random.choice(available) if available else (0, 0)
        self.active = True

    def deactivate(self) -> None:
        self.active = False

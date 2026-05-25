from __future__ import annotations

from config import COLS, ROWS, INITIAL_LENGTH, Direction, DIRECTION_OPPOSITES


class Snake:
    def __init__(self) -> None:
        start_col = COLS // 2
        start_row = ROWS // 2
        self.body: list[tuple[int, int]] = [
            (start_col - i, start_row) for i in range(INITIAL_LENGTH)
        ]
        self.direction: Direction = Direction.RIGHT
        self._pending_growth: int = 0
        self.prev_tail: tuple[int, int] | None = None
        self.has_eaten: bool = False

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    def set_direction(self, new_direction: Direction) -> None:
        if new_direction != DIRECTION_OPPOSITES[self.direction]:
            self.direction = new_direction

    def move(self) -> None:
        self.prev_tail = self.body[-1] if self.body else None
        self.has_eaten = False
        dx, dy = self.direction.value
        new_head = (self.head[0] + dx, self.head[1] + dy)
        self.body.insert(0, new_head)
        if self._pending_growth > 0:
            self._pending_growth -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self._pending_growth += amount
        self.has_eaten = True

    def check_wall_collision(self) -> bool:
        col, row = self.head
        return col < 0 or col >= COLS or row < 0 or row >= ROWS

    def check_self_collision(self) -> bool:
        return self.head in self.body[1:]

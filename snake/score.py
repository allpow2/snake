import json
import os

from config import SCORE_FILE


class ScoreManager:
    def __init__(self) -> None:
        self.score: int = 0
        self.high_score: int = self._load_high_score()

    def add_score(self, points: int) -> None:
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score

    def reset(self) -> None:
        self.score = 0

    def save(self) -> None:
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except OSError:
            pass

    def _load_high_score(self) -> int:
        if not os.path.exists(SCORE_FILE):
            return 0
        try:
            with open(SCORE_FILE) as f:
                data = json.load(f)
            return data.get("high_score", 0)
        except (OSError, json.JSONDecodeError):
            return 0

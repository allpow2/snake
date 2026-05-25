import sys

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game
from renderer import Renderer


def main() -> None:
    pygame.init()
    pygame.key.stop_text_input()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")

    clock = pygame.time.Clock()
    game = Game()
    renderer = Renderer(screen)

    tick_accumulator: float = 0

    while not game.should_quit:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.force_quit()
            else:
                game.handle_input(event)

        keys = pygame.key.get_pressed()
        game.handle_held_keys(keys)

        tick_accumulator += dt
        tick_interval = 1000 / game.speed
        while tick_accumulator >= tick_interval:
            game.update()
            tick_accumulator -= tick_interval

        interp = tick_accumulator / tick_interval if tick_interval > 0 else 0.0
        renderer.render(game, min(interp, 1.0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

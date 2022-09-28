import pygame
import sys
from settings import *
from level import Level
from input import Input


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zelda-like RPG")
        self.clock = pygame.time.Clock()
        self.input = Input()

        self.level = Level(self.input)

        try: main_sound = pygame.mixer.Sound("audio/main.ogg")
        except: main_sound = pygame.mixer.Sound("../audio/main.ogg")
        main_sound.set_volume(0.1 * volume)
        main_sound.play(loops = -1, fade_ms=3500)

    def run(self):
        while True:
            self.input.update()
            if self.input.quit:
                pygame.quit()
                sys.exit()
            if self.input.upgrade_menu and not self.level.game_paused:
                self.level.pause()
            elif self.input.exit_menu and self.level.game_paused:
                self.level.unpause()

            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()

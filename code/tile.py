import pygame
from copy import deepcopy

from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface

        # 1:54:50
        y_offset = self.image.get_height() - 64
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1] - y_offset))


        self.hitbox = deepcopy(self.rect)
        self.hitbox.y += self.hitbox.height - TILESIZE
        self.hitbox.height = TILESIZE
        self.hitbox = self.hitbox.inflate(0, -20)

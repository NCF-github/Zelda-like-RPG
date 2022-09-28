import pygame
from settings import *

class Ui:
    def __init__(self):
        # General
        self.display_surface = pygame.display.get_surface()
        try: self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        except: self.font = pygame.font.Font("../" + UI_FONT, UI_FONT_SIZE)

        # Bar setup
        self.health_bar_pos = pygame.math.Vector2(10, 10)
        self.energy_bar_pos = pygame.math.Vector2(10, 35)
        self.resistance_bar_pos = pygame.math.Vector2(10, 60)

        # Convert weapon dictionary
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon["graphic"]
            try:
                weapon = pygame.image.load(path).convert_alpha()
            except:
                weapon = pygame.image.load("../" + path).convert_alpha()
            self.weapon_graphics.append(weapon)

        # Convert magic dictionary
        self.magic_graphics = []
        for magic in magic_data.values():
            path = magic["graphic"]
            try:
                magic = pygame.image.load(path).convert_alpha()
            except:
                magic = pygame.image.load("../" + path).convert_alpha()
            self.magic_graphics.append(magic)

    def show_bar(self, current_amount, max_amount, bg_rect, color):
        # Draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # Converting stat to pixel
        ratio = current_amount / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # Drawing the bar
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)

        bottom_right = self.display_surface.get_rect().bottomright - pygame.math.Vector2(10, 10)
        text_rect = text_surf.get_rect(bottomright=bottom_right)

        text_bg_rect = text_rect.inflate(10, 10)
        text_bg_surface = pygame.Surface((text_bg_rect.width, text_bg_rect.height), flags=pygame.SRCALPHA)
        text_bg_surface.fill(UI_BG_COLOR)
        text_bg_surface.set_alpha(UI_BG_TRANSPARENCY)

        self.display_surface.blit(text_bg_surface, text_bg_rect)
        self.display_surface.blit(text_surf, text_rect)
        # pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_bg_rect, 3)
        pass

    def selection_box(self, left, top, has_switched, draw=True):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)

        if not draw:
            return bg_rect

        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), flags=pygame.SRCALPHA)
        bg_surface.fill(UI_BG_COLOR)
        bg_surface.set_alpha(UI_BG_TRANSPARENCY)

        self.display_surface.blit(bg_surface, bg_rect)

        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched, player):
        can_use = player.resistance >= list(weapon_data.values())[player.weapon_index]["resistance_cost"]
        bg_rect = self.selection_box(10, 630, has_switched, can_use)

        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(weapon_surf, weapon_rect)

        if not can_use:
            bg_rect = self.selection_box(10, 630, has_switched)

    def magic_overlay(self, magic_index, has_switched, player):
        can_cast = player.energy >= list(magic_data.values())[magic_index]["cost"]
        bg_rect = self.selection_box(100, 630, has_switched, can_cast)

        magic_surf = self.magic_graphics[magic_index]
        magic_rect = magic_surf.get_rect(center=bg_rect.center)

        self.display_surface.blit(magic_surf, magic_rect)

        if not can_cast:
            self.selection_box(100, 630, has_switched)

    def get_enemies(self, sprites):
        self.enemies = []
        for sprite in sprites:
            if sprite.sprite_type == "enemy":
                self.enemies.append(sprite)

    def draw_enemy_health_bar(self, enemy, player):
        bg_rect = pygame.Rect(0, 0, ENEMY_BAR_WIDTH, ENEMY_BAR_HEIGHT)

        # Calculate health rect
        health_ratio = enemy.health / enemy.monster_info["health"]
        health_rect = bg_rect.copy()
        health_rect.width = int(health_rect.width * health_ratio)

        # Create bar
        bar_surf = pygame.Surface(bg_rect.size)
        pygame.draw.rect(bar_surf, UI_BG_COLOR, bg_rect)
        pygame.draw.rect(bar_surf, ENEMY_HEALTH_BAR_COLOR, health_rect)
        pygame.draw.rect(bar_surf, UI_BORDER_COLOR, bg_rect, 3)

        # Calculate pos
        offset = pygame.math.Vector2()
        offset.x = player.rect.centerx - self.display_surface.get_width()//2
        offset.y = player.rect.centery - self.display_surface.get_height()//2

        bg_rect.y = enemy.rect.y - ENEMY_BAR_HEIGHT
        bg_rect.x = enemy.rect.centerx - bg_rect.width // 2
        bg_rect.center = bg_rect.center - offset

        # Display bar
        bar_surf.set_alpha(enemy.alpha_value)
        self.display_surface.blit(bar_surf, bg_rect)

    def draw_enemy_health_bars(self, player, enemy_sprites):
        for enemy in enemy_sprites.sprites():
            if enemy.alpha_value != 0:
                self.draw_enemy_health_bar(enemy, player)

    def display(self, player, enemy_sprites):
        self.draw_enemy_health_bars(player, enemy_sprites)

        health_bar_rect = pygame.Rect(self.health_bar_pos.x, self.health_bar_pos.y, player.stats["health"]*HEALTH_BAR_WIDTH_RATIO, BAR_HEIGHT)
        energy_bar_rect = pygame.Rect(self.energy_bar_pos.x, self.energy_bar_pos.y, player.stats["energy"]*ENERGY_BAR_WIDTH_RATIO, BAR_HEIGHT)
        resistance_bar_rect = pygame.Rect(self.resistance_bar_pos.x, self.resistance_bar_pos.y, player.stats["resistance"]*ENERGY_BAR_WIDTH_RATIO, BAR_HEIGHT)
        self.show_bar(player.health, player.stats["health"], health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats["energy"], energy_bar_rect, ENERGY_COLOR)
        self.show_bar(player.resistance, player.stats["resistance"], resistance_bar_rect, RESISTANCE_COLOR)

        self.show_exp(player.exp)

        self.weapon_overlay(player.weapon_index, not player.can_switch_weapons, player)
        self.magic_overlay(player.magic_index, not player.can_switch_magic, player)

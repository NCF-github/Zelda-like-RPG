import pygame
from settings import *

class Upgrade:
    def __init__(self, player, input):
        # General setup
        self.display_surface = pygame.display.get_surface()
        self.input = input
        self.player = player
        self.bg_transparency = 125

        self.attribute_number = len(self.player.stats)
        self.attribute_names = list(self.player.stats.keys())
        self.max_values = list(self.player.max_stats.values())
        try: self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        except: self.font = pygame.font.Font("../" + UI_FONT, UI_FONT_SIZE)
        try: self.upgrade_sound = pygame.mixer.Sound("audio/level_up.wav")
        except: self.upgrade_sound = pygame.mixer.Sound("../audio/level_up.wav")
        self.upgrade_sound.set_volume(0.7 * volume)

        # Item creation
        self.height = self.display_surface.get_height() * 0.8
        self.width = self.display_surface.get_width() // (self.attribute_number+1)
        self.gap_width = self.display_surface.get_width() // ((self.attribute_number+1)**2)
        self.create_items()

        # Selectin system
        self.selection_index = 0
        self.selection_time = None
        self.movement_time = None
        self.can_select = True
        self.can_move = True
        self.selection_cooldown = 300
        self.movement_cooldown = 200
    
    def get_input(self):
        if self.can_move:
            if self.input.right_menu and self.selection_index < self.attribute_number - 1:
                self.selection_index += 1
                self.can_move = False
                self.movement_time = pygame.time.get_ticks()
            elif self.input.left_menu and self.selection_index > 0:
                self.selection_index -= 1
                self.can_move = False
                self.movement_time = pygame.time.get_ticks()

        if self.input.select and self.can_select:
            self.can_select = False
            self.selection_time = pygame.time.get_ticks()
            self.item_list[self.selection_index].trigger(self.player, self.upgrade_sound)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.can_select:
            if current_time - self.selection_time >= self.selection_cooldown:
                self.can_select = True

        if not self.can_move:
            if current_time - self.movement_time >= self.movement_cooldown:
                self.can_move = True

    def create_items(self):
        self.item_list = []

        for i in range(self.attribute_number):
            left = i*self.width + (i+1)*self.gap_width
            top = (self.display_surface.get_height() - self.height) // 2

            rect = pygame.Rect(left, top, self.width, self.height)
            item = Item(rect, i, self.font)
            self.item_list.append(item)

    def draw_transparent_surface(self):
        transparent_surface = pygame.Surface((self.display_surface.get_size())).convert_alpha()
        transparent_surface.fill(UI_BG_COLOR)
        transparent_surface.set_alpha(self.bg_transparency)
        self.display_surface.blit(transparent_surface, (0,0))

    def update(self):
        self.get_input()
        self.cooldowns()

    def display(self):
        self.update()

        self.draw_transparent_surface()
        for index, item in enumerate(self.item_list):
            # Get attributes
            name = self.attribute_names[index]
            value = self.player.stats[name]
            max_value = self.max_values[index]
            cost = self.player.upgrade_cost[name]
            item.display(self.display_surface, self.selection_index, name, value, max_value, cost, self.player)


class Item:
    def __init__(self, rect, index, font):
        self.rect = rect
        self.index = index
        self.font = font

    def display_names(self, surface, name, cost, selected, player):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0,20))

        
        if player.stats[name] == player.max_stats[name]:
            cost_surf = self.font.render("maxed", False, color)
        else:
            cost_surf = self.font.render(str(int(cost)), False, color)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom + pygame.math.Vector2(0,-20))

        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)
    
    def display_bar(self, surface, value, max_value, selected):
        # Drawing setup
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom + pygame.math.Vector2(0, -60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        # Bar setup
        full_height = bottom.y - top.y
        relative_number = (value/max_value) * full_height
        width = 30
        height = 10
        value_rect = pygame.Rect(self.rect.centerx - width//2, bottom.y - relative_number - height//2, width, height)

        # Draw elements
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def trigger(self, player, sound):
        upgrade_attribute = list(player.stats.keys())[self.index]
        
        if player.exp >= player.upgrade_cost[upgrade_attribute] and player.stats[upgrade_attribute] < player.max_stats[upgrade_attribute]:
            sound.play()
            player.exp -= player.upgrade_cost[upgrade_attribute]
            player.stats[upgrade_attribute] *= 1.2
            player.upgrade_cost[upgrade_attribute] *= 1.4
            player.stats[upgrade_attribute] = min(player.stats[upgrade_attribute], player.max_stats[upgrade_attribute])

    def display(self, surface, selection_num, name, value, max_value, cost, player):
        selected = self.index == selection_num

        if selected:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, selected, player)
        self.display_bar(surface, value, max_value, selected)
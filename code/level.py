import pygame
from random import choice, randint
from debug import debug
from settings import *
from tile import Tile
from player import Player
from enemy import Enemy
from support import *
from weapon import Weapon
from ui import Ui
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade


class Level:
    def __init__(self, input):

        # General setup
        self.display_surface = pygame.display.get_surface()
        self.input = input

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Attack sprites
        self.current_attack = None

        # Sprite setup
        self.create_map()

        # User interface
        self.ui = Ui()
        self.upgrade = Upgrade(self.player, self.input)
        self.ui.get_enemies(self.visible_sprites.sprites())

        # Particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        # Pause
        self.game_paused = False
        self.pause_time = None

        # End
        self.game_over = False
        self.alpha_value = 0
        try: self.font = pygame.font.Font(GAME_OVER_UI_FONT, GAME_OVER_UI_FONT_SIZE)
        except: self.font = pygame.font.Font("../" + GAME_OVER_UI_FONT, GAME_OVER_UI_FONT_SIZE)

        try: self.death_sound = pygame.mixer.Sound("audio/game_over.wav")
        except: self.death_sound = pygame.mixer.Sound("../audio/game_over.wav")
        self.death_sound.set_volume(0.3 * volume)

    def create_map(self):
        layouts = {
            "boundary": import_csv_layout("map/map_FloorBlocks.csv"),
            "grass": import_csv_layout("map/map_Grass.csv"),
            "object": import_csv_layout("map/map_Objects.csv"),
            "entities": import_csv_layout("map/map_Entities.csv")
        }
        graphics = {
            "grass": import_folder("graphics/Grass"),
            "objects": import_folder("graphics/objects")
        }

        for style, layout in layouts.items():
            for j, row in enumerate(layout):
                for i, col in enumerate(row):
                    if col != "-1":
                        x = i * TILESIZE
                        y = j * TILESIZE
                        if style == "boundary":
                            Tile((x, y), [self.obstacle_sprites], "invisible")
                        if style == "grass":
                            random_grass_image = choice(graphics["grass"])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], "grass", random_grass_image)
                        if style == "object":
                            surf = graphics["objects"][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], "object", surf)
                        if style == "entities":
                            if col == "394":
                                self.player = Player(
                                    (x, y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic,
                                    self.input
                                    )
                            else:
                                if col == "390": monster_name = "bamboo"
                                elif col == "391": monster_name = "spirit"
                                elif col == "392": monster_name = "raccoon"
                                elif col == "393": monster_name = "squid"
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visible_sprites, self.attackable_sprites, self.enemy_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp
                                    )

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == "heal":
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        elif style == "flame":
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, dokill=False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == "grass":
                            pos = target_sprite.rect.center
                            for _ in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos, [self.visible_sprites])
                            target_sprite.kill()
                        elif target_sprite.sprite_type == "enemy":
                            target_sprite.get_damaged(self.player, attack_sprite)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.health = max(self.player.health, 0)
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()

            # Spawn particles
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

    def add_exp(self, amount):
        self.player.exp += amount

    def run(self):
        # Update and draw the game
        self.update_game_over()
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player, self.enemy_sprites)
        
        if self.game_paused:
            # Display upgrade menu
            self.upgrade.display()
        elif self.game_over:
            self.draw_end()
        else:
            # Run the game
            self.visible_sprites.enemy_update(self.player)
            self.visible_sprites.update()
            self.player_attack_logic()

    def pause(self):
        self.game_paused = True
        self.pause_time = pygame.time.get_ticks()

    def unpause(self):
        self.game_paused = False
        self.player.unpause(self.pause_time)

    def update_game_over(self):
        if self.player.health <= 0 and not self.game_over:
            self.game_over = True
            pygame.mixer.stop()
            self.death_sound.play()
    
    def draw_end(self):
        transparent_surface = pygame.Surface(self.display_surface.get_size())
        transparent_surface.fill("black")

        label = self.font.render("You Died", False, "red")
        label_rect = label.get_rect(center=transparent_surface.get_rect().center)
        transparent_surface.blit(label, label_rect)

        transparent_surface.set_alpha(int(self.alpha_value))
        self.alpha_value += 1.5

        self.display_surface.blit(transparent_surface, (0,0))

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # General setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # Creatin the floor
        try:
            self.floor_surface = pygame.image.load("graphics/tilemap/ground.png").convert()
        except:
            self.floor_surface = pygame.image.load("../graphics/tilemap/ground.png").convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0,0))
    
    def custom_draw(self, player):
        # Getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, floor_offset_pos)

        # Drawing the sprites
        for sprite in sorted(self.sprites(), key=lambda sprite: self._get_custom_y(sprite, player)):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def _get_custom_y(self, sprite, player):
        if sprite.sprite_type == "weapon":
            return player.rect.y + player.rect.height + 15
        
        return sprite.rect.y + sprite.rect.height

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if sprite.sprite_type == "enemy"]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)

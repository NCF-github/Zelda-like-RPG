import pygame
from copy import deepcopy
from settings import *
from support import import_folder
from entity import Entity


class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic, input):
        super().__init__(groups)
        try:
            self.image = pygame.image.load("graphics/test/player.png").convert_alpha()
        except:
            self.image = pygame.image.load("../graphics/test/player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -26)
        top_y_hitbox_reduction = 15
        self.hitbox.y += top_y_hitbox_reduction
        self.hitbox.height -= top_y_hitbox_reduction
        self.sprite_type = "player"
        self.input = input

        # Graphics setup
        self.import_player_assets()
        self.status = "down"

        # Weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapons = True
        self.weapon_switch_time = None
        self.switch_cooldown = 200

        # Movement and movement limitatios
        self.attacking = False
        self.can_attack = True
        self.attack_cooldown = weapon_data[self.weapon]["attackig_time"]
        self.attack_again_cooldown = weapon_data[self.weapon]["cooldown"]
        self.attack_time = None

        self.obstacle_sprites = obstacle_sprites

        # Magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # Stats
        self.stats = {"health": 110, "energy": 60, "resistance": 85, "attack": 10, "magic": 4, "speed": 5}
        self.max_stats = {"health": 270, "energy": 140, "resistance": 360, "attack": 20, "magic": 11, "speed": 10}
        self.upgrade_cost = {"health": 90, "energy": 100, "resistance": 60, "attack": 115, "magic": 100, "speed": 130}
        self.health = self.stats["health"]
        self.energy = self.stats["energy"]
        self.resistance = self.stats["resistance"]
        self.exp = 500
        self.speed = self.stats["speed"] * 0.4 + 3

        # Damage timer
        self.vulnerable = True
        self.invlunerability_duration = 500
        self.hurt_time = None

        # Resistance timer
        self.resistance_timer = pygame.time.get_ticks()
        self.base_resistance_recovery = 0.2
        self.extra_resistance_recovery_per_phase = 0.5
        self.time_to_get_to_next_phase = 800

        # Import sound
        try: self.weapon_attack_sound = pygame.mixer.Sound("audio/sword.wav")
        except: self.weapon_attack_sound = pygame.mixer.Sound("../audio/sword.wav")
        self.weapon_attack_sound.set_volume(0.1 * volume)

    def import_player_assets(self):
        try:
            character_path = 'graphics/player/'
            self.animations = {
                "up": [], "down": [], "left": [], "right": [],
                "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
                "right_attack": [], "left_attack": [], "up_attack": [], "down_attack": []
            }

            for animation in self.animations.keys():
                full_path = character_path + animation
                self.animations[animation] = import_folder(full_path)
        except:
            character_path = '../graphics/player/'
            self.animations = {
                "up": [], "down": [], "left": [], "right": [],
                "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
                "right_attack": [], "left_attack": [], "up_attack": [], "down_attack": []
            }

            for animation in self.animations.keys():
                full_path = character_path + animation
                self.animations[animation] = import_folder(full_path)

    def get_input(self):
        if self.attacking:
            return

        # Movement input
        # if self.input.up and not self.input.down:
        #     self.direction.y = -1
        # elif self.input.down and not self.input.up:
        #     self.direction.y = 1
        # else:
        #     self.direction.y = 0
        
        # if self.input.left and not self.input.right:
        #     self.direction.x = -1
        # elif self.input.right and not self.input.left:
        #     self.direction.x = 1
        # else:
        #     self.direction.x = 0
        
        # if self.direction.magnitude() != 0:
        #     self.direction = self.direction.normalize()
        self.direction = deepcopy(self.input.direction)

        # Attack input
        if self.input.attack and self.can_attack and self.resistance >= weapon_data[self.weapon]["resistance_cost"]:
            self.attacking = True
            self.can_attack = False
            self.attack_cooldown = weapon_data[self.weapon]["attackig_time"]
            self.attack_again_cooldown = weapon_data[self.weapon]["cooldown"]
            self.attack_time = pygame.time.get_ticks()
            self.get_status()
            self.create_attack()
            self.resistance -= weapon_data[self.weapon]["resistance_cost"]
            self.weapon_attack_sound.play()

        # Magic input
        if self.input.magic and self.can_attack and self.resistance >= magic_data[self.magic]["resistance_cost"]:
            self.attacking = True
            self.can_attack = False
            self.attack_cooldown = magic_data[self.magic]["cast_time"]
            self.attack_again_cooldown = magic_data[self.magic]["cast_again_time"]
            self.get_status()
            self.attack_time = pygame.time.get_ticks()
            
            # 3:50:50
            style = self.magic
            strength = magic_data[self.magic]["strength"] + self.stats["magic"]
            cost = magic_data[self.magic]["cost"]
            self.create_magic(style, strength, cost)
            self.resistance -= magic_data[self.magic]["resistance_cost"]

        # Change weapon
        if self.can_switch_weapons and (self.input.next_weapon or self.input.previous_weapon):
            if self.input.next_weapon:
                self.weapon_index += 1
            if self.input.previous_weapon:
                self.weapon_index -= 1
            self.weapon_index %= len(weapon_data)
            self.can_switch_weapons = False
            self.weapon_switch_time = pygame.time.get_ticks()
            self.weapon = list(weapon_data.keys())[self.weapon_index]

        # Change magic
        if self.can_switch_magic and self.input.change_magic:
            self.magic_index += 1
            self.magic_index %= len(magic_data)
            self.can_switch_magic = False
            self.magic_switch_time = pygame.time.get_ticks()
            self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):
        # 2:21:30

        previous_status = self.status

        # Direction (and moving if not in any other status)
        if self.direction.x > 0:
            self.status = "right"
        elif self.direction.x < 0:
            self.status = "left"
        if self.direction.y > 0 and self.direction.y > abs(self.direction.x):
            self.status = "down"
        elif self.direction.y < 0 and abs(self.direction.y) > abs(self.direction.x):
            self.status = "up"
        else:
            if "_" in self.status:
                self.status = self.status[:self.status.index("_")]

        # Attacking status
        if self.attacking:
            self.direction.x, self.direction.y = 0, 0
            self.status += "_attack"

        # Idle status
        if self.direction.x == 0 and self.direction.y == 0 and not self.attacking:
            self.status = self.status + "_idle"

        if self.status != previous_status:
            self.frame_index = 0

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown + self.attack_again_cooldown:
                self.can_attack = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_cooldown:
                self.can_switch_magic = True

        if not self.can_switch_weapons:
            if current_time - self.weapon_switch_time >= self.switch_cooldown:
                self.can_switch_weapons = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invlunerability_duration:
                self.vulnerable = True

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index -= len(animation)

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats["attack"]
        weapon_damage = weapon_data[self.weapon]["damage"]
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats["magic"]
        spell_damage = magic_data[self.magic]["strength"]
        return base_damage + spell_damage

    def energy_recovery(self):
        if self.energy < self.stats["energy"]:
            self.energy += 0.005 * (self.stats["magic"] * 0.5 + 2)
        else:
            self.energy = self.stats["energy"]

    def resistance_recovery(self):
        if self.attacking:
            self.resistance_timer = pygame.time.get_ticks()
        else:
            if self.resistance < self.stats["resistance"]:
                time_recovering = pygame.time.get_ticks() - self.resistance_timer
                phase = time_recovering // self.time_to_get_to_next_phase
                extra_resistance_recovery = phase * self.extra_resistance_recovery_per_phase
                resistance_recovery_speed = self.base_resistance_recovery + extra_resistance_recovery
                self.resistance += resistance_recovery_speed
            else:
                self.resistance = self.stats["resistance"]

    def update(self):
        self.speed = self.stats["speed"] * 0.4 + 3
        self.get_input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
        self.energy_recovery()
        self.resistance_recovery()

    def unpause(self, pause_time):
        current_time = pygame.time.get_ticks()
        increment = current_time - pause_time

        if self.attack_time:
            self.attack_time += increment
        if self.magic_switch_time:
            self.magic_switch_time += increment
        if self.weapon_switch_time:
            self.weapon_switch_time += increment
        if self.hurt_time:
            self.hurt_time += increment
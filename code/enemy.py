from matplotlib import animation
import pygame
from settings import *
from entity import Entity
from support import import_folder

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_exp):
        # General setup
        super().__init__(groups)
        self.sprite_type = "enemy"

        # Graphics setup
        self.import_graphics(monster_name)
        self.status = "idle"
        self.image = self.animations[self.status][self.frame_index]

        # Movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -16)
        self.obstacle_sprites = obstacle_sprites

        # Stats
        self.monster_name = monster_name
        self.monster_info = monster_data[self.monster_name]
        self.health = self.monster_info['health']
        self.exp = self.monster_info['exp']
        self.speed = self.monster_info['speed']
        self.attack_damage = self.monster_info['attack_damage']
        self.resistance = self.monster_info['resistance']
        self.attack_radius = self.monster_info['attack_radius']
        self.notice_radius = self.monster_info['notice_radius']
        self.attack_type = self.monster_info['attack_type']
        self.attack_cooldown = self.monster_info["attack_cooldown"]

        # Player interaction
        self.can_attack = True
        self.attack_time = None
        self.recieved_weapon_attacks = []
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp
        self.resistance_multiplicator = 1

        # Invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # Sounds
        try:
            self.death_sound = pygame.mixer.Sound("audio/death.wav")
            self.hit_sound = pygame.mixer.Sound("audio/hit.wav")
            self.attack_sound = pygame.mixer.Sound(self.monster_info["attack_sound"])
        except:
            self.death_sound = pygame.mixer.Sound("../audio/death.wav")
            self.hit_sound = pygame.mixer.Sound("../audio/hit.wav")
            self.attack_sound = pygame.mixer.Sound("../" + self.monster_info["attack_sound"])
        self.death_sound.set_volume(0.3 * volume)
        self.hit_sound.set_volume(0.1 * volume)
        self.attack_sound.set_volume(0.1 * volume)

        # Ui (health bar)
        self.alpha_value = 0

    def import_graphics(self, name):
        try:
            self.animations = {"idle": [], "move": [], "attack": []}
            main_path = f"graphics/monsters/{name}/"
            for animation in self.animations.keys():
                self.animations[animation] = import_folder(main_path + animation)
            if self.animations == {"idle": [], "move": [], "attack": []}:
                raise Exception()
        except:
            self.animations = {"idle": [], "move": [], "attack": []}
            main_path = f"../graphics/monsters/{name}/"
            for animation in self.animations.keys():
                self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_and_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.hitbox.center)
        player_vec = pygame.math.Vector2(player.hitbox.center)

        distance = (player_vec - enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def get_status(self, player):
        previous_status = self.status

        distance, self.direction = self.get_player_distance_and_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        elif previous_status == "move" and distance <= self.notice_radius * 1.5:
            self.status = "move"
        else:
            self.status = "idle"

        if self.status != previous_status:
            self.frame_index = 0

    def actions(self, player):
        if self.status == "attack":
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.status == "move":
            self.alpha_value = min(self.alpha_value + 10, 255)
        else:
            self.alpha_value = max(self.alpha_value -10, 0)
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index -= len(animation)

        try:
            self.image = animation[int(self.frame_index)]
        except:
            self.frame_index = 0
            self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damaged(self, player, attack):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_and_direction(player)[1]
            self.status = "move"
            if attack.sprite_type == "weapon":
                if attack not in self.recieved_weapon_attacks:
                    self.health -= player.get_full_weapon_damage()
                    self.recieved_weapon_attacks.append(attack)
                    self.hit_time = pygame.time.get_ticks()
                    self.vulnerable = False
                    self.resistance_multiplicator = weapon_data[player.weapon]["knockback"]
            else:
                # Magic damage
                self.health -= player.get_full_magic_damage()
                self.hit_time = pygame.time.get_ticks()
                self.vulnerable = False

    def hit_reaction(self, player):
        if not self.vulnerable:
            enemy_vec = pygame.math.Vector2(self.hitbox.center)
            player_vec = pygame.math.Vector2(player.hitbox.center)
            direction = (player_vec - enemy_vec)
            if direction.magnitude() != 0:
                direction = direction.normalize()
            self.direction *= -(self.resistance * self.resistance_multiplicator)

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.death_sound.play()

    def update(self):
        self.move(self.speed)
        # self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self, player):
        self.get_status(player)
        self.animate()
        self.actions(player)
        self.hit_reaction(player)

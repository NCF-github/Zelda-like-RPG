import pygame

# Game setup
WIDTH    = 1280	
HEIGHT   = 720
FPS      = 60
TILESIZE = 64
volume = 1
scaling_factor = 1

# Ui
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH_RATIO = 1.3
ENERGY_BAR_WIDTH_RATIO = 1.5
ITEM_BOX_SIZE = 80
UI_FONT = "graphics/font/joystix.ttf"
UI_FONT_SIZE = 18

# General colors
WATER_COLOR = "#71ddee"
UI_BG_COLOR = "#222222"
UI_BG_TRANSPARENCY = 150
UI_BORDER_COLOR = "#111111"
TEXT_COLOR = "#EEEEEE"

# Ui colors
HEALTH_COLOR = "red"
ENERGY_COLOR = "blue"
RESISTANCE_COLOR = "#008400"
UI_BORDER_COLOR_ACTIVE = "gold"

# Upgrade menu
TEXT_COLOR_SELECTED = "#111111"
BAR_COLOR = "#EEEEEE"
BAR_COLOR_SELECTED = "#111111"
UPGRADE_BG_COLOR_SELECTED = "#EEEEEE"

# Enemy info UI
ENEMY_BAR_HEIGHT = 10
ENEMY_BAR_WIDTH = 70
ENEMY_HEALTH_BAR_COLOR = "red"

# Game over
GAME_OVER_UI_FONT = "graphics/font/joystix.ttf"
GAME_OVER_UI_FONT_SIZE = 50

# Controls
button_one_time_press = {  # True if keeping down makes no difference
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "attack": False,
    "next_weapon": True,
    "previous_weapon": True,
    "magic": False,
    "change_magic": True,
    "upgrade_menu": True,
    "right_menu": True,
    "left_menu": True,
    "select": True,
    "exit_menu": True,
}
keyboard_button_mapping = {
    "up": [pygame.K_UP],
    "down": [pygame.K_DOWN],
    "left": [pygame.K_LEFT],
    "right": [pygame.K_RIGHT],
    "attack": [pygame.K_SPACE],
    "next_weapon": [pygame.K_d],
    "previous_weapon": [pygame.K_s],
    "magic": [pygame.K_f],
    "change_magic": [pygame.K_a],
    "upgrade_menu": [pygame.K_m],
    "right_menu": [pygame.K_RIGHT],
    "left_menu": [pygame.K_LEFT],
    "select": [pygame.K_SPACE, pygame.K_KP_ENTER],
    "exit_menu": [pygame.K_m, pygame.K_ESCAPE],
}
controller_button_mapping = {
    "attack": [0],
    "next_weapon": [10, 14],
    "previous_weapon": [9, 13],
    "magic": [2],
    "change_magic": [11, 12],
    "upgrade_menu": [3, 6, 15],
    "right_menu": [10, 14],
    "left_menu": [9, 13],
    "select": [0],
    "exit_menu": [1, 3, 6, 15],
}
MOVEMENT_THRESHHOLD = 0.3
MENU_MOVEMENT_THRESHHOLD = 0.5

# Weapons
weapon_data = {
    "sword": {"cooldown": 300, "attackig_time": 350, "damage": 16, "resistance_cost": 25, "knockback": 0.9, "graphic": "graphics/weapons/sword/full.png"},
    "lance": {"cooldown": 500, "attackig_time": 500, "damage": 30, "resistance_cost": 30, "knockback": 1.2, "graphic": "graphics/weapons/lance/full.png"},
    "axe": {"cooldown": 570, "attackig_time": 630, "damage": 45, "resistance_cost": 40, "knockback": 1.6, "graphic": "graphics/weapons/axe/full.png"},
    "rapier": {"cooldown": 300, "attackig_time": 125, "damage": 6, "resistance_cost": 20, "knockback": 0.5, "graphic": "graphics/weapons/rapier/full.png"},
    "sai": {"cooldown": 80, "attackig_time": 250, "damage": 3, "resistance_cost": 12, "knockback": 0.3, "graphic": "graphics/weapons/sai/full.png"},
}

# Magic
magic_data = {
    "flame": {"strength": 5, "cost": 20, "resistance_cost": 20, "cast_time": 750, "cast_again_time": 400, "graphic": "graphics/particles/flame/fire.png"},
    "heal": {"strength": 20, "cost": 10, "resistance_cost": 10, "cast_time": 350, "cast_again_time": 150, "graphic": "graphics/particles/heal/heal.png"}
}

# Enemy
monster_data = {
    "squid": {"health": 100, "exp": 100, "attack_damage": 20, "attack_type": "slash", "attack_sound": "audio/attack/slash.wav", "speed": 3, "resistance": 1, "attack_radius": 80, "notice_radius": 300, "attack_cooldown": 400},
    "raccoon": {"health": 300, "exp": 250, "attack_damage": 40, "attack_type": "claw", "attack_sound": "audio/attack/claw.wav", "speed": 2, "resistance": 0.75, "attack_radius": 120, "notice_radius": 330, "attack_cooldown": 500},
    "spirit": {"health": 100, "exp": 110, "attack_damage": 8, "attack_type": "thunder", "attack_sound": "audio/attack/fireball.wav", "speed": 4, "resistance": 1.3, "attack_radius": 60, "notice_radius": 285, "attack_cooldown": 300},
    "bamboo": {"health": 70, "exp": 120, "attack_damage": 10, "attack_type": "leaf_attack", "attack_sound": "audio/attack/slash.wav", "speed": 3, "resistance": 1, "attack_radius": 50, "notice_radius": 250, "attack_cooldown": 600}
}

# Weapon damage balancing
if __name__ == "__main__":
    for weapon, values in weapon_data.items():
        total_time = values["cooldown"] + values["attackig_time"]
        print(weapon, 100 * (10 + values["damage"]) / total_time, 100 * (20 + values["damage"]) / total_time)

# Image scaling
def scale_rect(rect):
    new_rect = pygame.Rect(
        rect.x * scaling_factor,
        rect.y * scaling_factor,
        rect.width * scaling_factor,
        rect.height * scaling_factor
        )
    return new_rect

def scale_image(img):
    return pygame.transform.scale(img, (img.width*scaling_factor, img.height*scaling_factor))

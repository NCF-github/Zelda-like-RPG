import pygame
from settings import *

class Input:
    def __init__(self):
        # Set attributes
        for input in keyboard_button_mapping.keys():
            self.setattr(input, False)

        self.direction = pygame.math.Vector2(0, 0)
        self.quit = False

        # Controller setup
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i))
        for joystick in self.joysticks:
            joystick.init()

    def setattr(self, attr, value):
        setattr(self, attr, value)

    def get_keyboard_input(self):
        for attr, value in button_one_time_press.items():
            if value == True:
                self.setattr(attr, False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.KEYDOWN:
                for attr, mapping in keyboard_button_mapping.items():
                    if event.key in mapping:
                        self.setattr(attr, True)

            if event.type == pygame.KEYUP:
                for attr, mapping in keyboard_button_mapping.items():
                    if not button_one_time_press[attr]:
                        if event.key in mapping:
                            self.setattr(attr, False)

        if self.up and not self.down:
            self.direction.y = -1
        elif self.down and not self.up:
            self.direction.y = 1
        else:
            self.direction.y = 0
        
        if self.left and not self.right:
            self.direction.x = -1
        elif self.right and not self.left:
            self.direction.x = 1
        else:
            self.direction.x = 0
        
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
                    
    def get_controller_input(self):
        for attr, value in button_one_time_press.items():
            if value == True:
                self.setattr(attr, False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.JOYBUTTONDOWN:
                for attr, mapping in controller_button_mapping.items():
                    if event.button in mapping:
                        self.setattr(attr, True)

            if event.type == pygame.JOYBUTTONUP:
                for attr, mapping in controller_button_mapping.items():
                    if not button_one_time_press[attr]:
                        if event.button in mapping:
                            self.setattr(attr, False)

            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    self.direction.x = event.value
                if event.axis == 1:
                    self.direction.y = event.value

        if self.direction.x > MENU_MOVEMENT_THRESHHOLD:
            self.right_menu = True
        if self.direction.x < -MENU_MOVEMENT_THRESHHOLD:
            self.left_menu = True
        
        if self.direction.magnitude() < MOVEMENT_THRESHHOLD:
            self.direction = pygame.math.Vector2()

    def update(self):
        if pygame.joystick.get_count() > 0:
            self.get_controller_input()
        else:
            self.get_keyboard_input()

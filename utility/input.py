import pygame


class input():
    mouse_pos = pygame.Vector2(0, 0)
    key_pressed = [False for i in range(512)]
    key_just_pressed = [False for i in range(512)]
    key_just_released = [False for i in range(512)]
    
    @staticmethod
    def get_key_pressed(key):
        return input.key_pressed[key]
    
    def get_key_down(key):
        return input.key_just_pressed[key]

    @staticmethod
    def on_tick():
        input.mouse_pos = pygame.Vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        key_pressed_last_frame = input.key_pressed
        input.key_pressed = pygame.key.get_pressed()

        for key in range(512):
            input.key_just_pressed[key] = (input.key_pressed[key]) and (not key_pressed_last_frame[key])
            input.key_just_released[key] = (not input.key_pressed[key]) and (key_pressed_last_frame[key])
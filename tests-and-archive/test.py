import pygame
from pygame import Vector2
import time
import utility.anim as anim
import math
import utility.utils as utils

class config():
    max_fps = 0
    min_delta = 0

    @staticmethod
    def set_max_fps(value):
        config.max_fps = value
        config.min_delta = 1 / config.max_fps
  

pygame.display.set_caption('Chess')
screen = pygame.display.set_mode((
    1000, # Window width 
    700  # Window height
))

config.set_max_fps(99999)

current_time = time.time()
time_last_frame = current_time
delta = config.min_delta

surface = pygame.Surface((400, 400))
surface.fill(pygame.Color(255, 255, 255))
print(surface.get_size())
surface = pygame.transform.smoothscale(surface, (100, 100))
print(surface.get_size())

fps_list = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.event.clear()

    screen.fill(pygame.Color(0, 0, 0))

    screen.blit(surface, (0, 0))

    pygame.display.flip()

    current_time = time.time()
    delta = current_time - time_last_frame
    if delta < config.min_delta:
        time.sleep(config.min_delta - delta)
        current_time = time.time()
        delta = current_time - time_last_frame
    time_last_frame = current_time
    fps_list.append(1 / delta)
    
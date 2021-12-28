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

pos = Vector2(100, 100)
velocity = Vector2()

fps_list = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.event.clear()

    target_coords = Vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    angle = (pos - target_coords).angle_to(Vector2(0, 1))
    
    velocity_in_direction = 0
    velocity_in_direction += velocity.x * math.cos(math.radians(angle + 90))
    velocity_in_direction += velocity.y * math.cos(math.radians(angle + 180))

    distance = math.sqrt(math.pow(target_coords.x - pos.x, 2) + math.pow(target_coords.y - pos.y, 2))

    velocity_in_direction = anim.circular_exponential(0, velocity_in_direction, distance, 100, 1000, 0.001, delta)

    velocity.x = velocity_in_direction * math.cos(math.radians(angle + 90))
    velocity.y = velocity_in_direction * math.cos(math.radians(angle + 180))

    screen.fill(pygame.Color(0, 0, 0))
    pygame.draw.circle(screen, pygame.Color(255, 255, 255), (pos.x, pos.y), 50)
    pos += velocity * delta
    pygame.display.flip()

    current_time = time.time()
    delta = current_time - time_last_frame
    if delta < config.min_delta:
        time.sleep(config.min_delta - delta)
        current_time = time.time()
        delta = current_time - time_last_frame
    time_last_frame = current_time
    fps_list.append(1 / delta)
    
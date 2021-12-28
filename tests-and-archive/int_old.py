
import pygame
from pygame import Color, Vector2
import time
import utility.anim as anim

def row(index):
    return (index / 8) % 8

def column(index):
    return index % 8

class config():
    max_fps = 0
    min_delta = 0
    background_color = Color(0, 0, 0)

    @staticmethod
    def set_max_fps(value):
        config.max_fps = value
        config.min_delta = 1 / config.max_fps - 0.01
    
    def set_background_color(color):
        config.background_color = color
  
class piece():
    screen_pos: Vector2 = Vector2()
    actual_pos: Vector2 = Vector2()
    piece: str = 'None'
    original_image: pygame.Surface = None
    image: pygame.Surface = None

    def __init__(self, piece: str):
        self.set_image('assets/pieces/current/' + piece)
    
    def set_image(self, image):
        self.original_image = pygame.image.load(image)
        self.image = self.original_image

pygame.display.set_caption('Chess')
screen = pygame.display.set_mode((
    1000, # Window width 
    700  # Window height
))

config.set_max_fps(60)

current_time = time.time()
time_last_frame = current_time
delta = config.min_delta

class render():
    @staticmethod
    def square_board():
        for i in range(64):
            if (i % 2 == 0) == (i % 16 < 8):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255), pygame.Rect())
            else:
                print("Black square")   

pieces = []
pieces.append(piece())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(config.background_color)

    pygame.display.flip()
    
    current_time = time.time()
    delta = current_time - time_last_frame
    if delta < config.min_delta:
        time.sleep(config.min_delta - delta)
    time_last_frame = current_time
    
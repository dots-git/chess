import pygame
import time
from pygame import Vector2
from base_components import *
import math
import utility.anim as anim
import copy

PIECES = [
    'wp', 
    'wn', 
    'wb', 
    'wr', 
    'wq', 
    'wk', 
    'bp', 
    'bn', 
    'bb', 
    'br', 
    'bq', 
    'bk'
]

def approx(a, b, variance):
    return a < b + variance and a > b - variance

class config():
    max_fps = 0
    min_delta = 0
    background_color = pygame.Color(0, 0, 0)
    piece_set: str = 'default'
    piece_images = {
        'wp': None,
        'wn': None,
        'wb': None,
        'wr': None,
        'wq': None,
        'wk': None,
        'bp': None,
        'bn': None,
        'bb': None,
        'br': None,
        'bq': None,
        'bk': None,
    }

    @staticmethod
    def set_max_fps(value):
        config.max_fps = value
        config.min_delta = 1 / config.max_fps
    
    def set_background_color(color):
        config.background_color = color
    
    def load_piece_set(piece_set: str):
        for piece in PIECES:
            config.piece_images[piece] = pygame.image.load(
                'assets/images/pieces/' + piece_set + '/' + piece + '.png')

config.load_piece_set('default')
config.set_max_fps(999)

class piece(component):
    debug_points = []
    sprite = None
    transform = None
    rb = None
    being_moved = True
    visible = False
    scale = 0
    scale_change_rate = 0
    position = Vector2(0, 0)
    piece: str = '' # Can be    wp (White Pawn), 
    #                           wn (White Knight), 
    #                           wb (White Bishop), 
    #                           wr (White Rook), 
    #                           wq (White Queen), 
    #                           wk (White King), 
    #                           bp (Black Pawn), 
    #                           bn (Black Knight),  
    #                           bb (Black Bishop), 
    #                           br (Black Rook), 
    #                           bq (Black Queen), 
    #                           bk (Black King)

    def start(self):
        self.transform = self.parent.get_component(transform)
        self.sprite = self.parent.get_component(sprite)
        self.rb = self.parent.get_component(rigidbody)

    def set_piece(self, piece: str):
        self.piece = piece
        if piece == 'None':
            self.sprite.set_image(pygame.Surface((0, 0)))
        else:
            self.sprite.set_image(config.piece_images[piece])

    def make_visible(self):
        visible = True
        pass

    def on_tick(self, delta: float):
        if self.piece != 'None':
            if self.being_moved:
                self.position = Vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

            if (not approx(self.transform.position.x, self.position.x, 1)) or (not approx(self.transform.position.y, self.position.y, 1)):
                angle = (self.transform.position - self.position).angle_to(Vector2(0, 1))
                
                velocity_in_direction = 0
                velocity_in_direction += self.rb.velocity.x * math.cos(math.radians(angle + 90))
                velocity_in_direction += self.rb.velocity.y * math.cos(math.radians(angle + 180))

                distance = math.sqrt(math.pow(self.position.x - self.transform.position.x, 2) + math.pow(self.position.y - self.transform.position.y, 2))

                velocity_in_direction = anim.circular_exponential(0, velocity_in_direction, distance, 10, 1000, 0.001, delta)

                self.rb.velocity.x = velocity_in_direction * math.cos(math.radians(angle + 90))
                self.rb.velocity.y = velocity_in_direction * math.cos(math.radians(angle + 180))
            else:
                self.rb.velocity = Vector2(0, 0)
            # if not approx(self.transform.scale[0], self.scale, 0.01):
            #     self.scale_change_rate = anim.circular_exponential(self.transform.scale[0], self.scale_change_rate, self.scale, 10, 10, 0.001, delta)
            #     self.transform.scale = self.transform.scale + Vector2(self.scale_change_rate, self.scale_change_rate)

WIDTH = 1200
HEIGHT = 700

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hello")

current_time = time.time()
time_last_frame = current_time
delta = config.min_delta
display_delta = config.min_delta

# Create game objects here

pieces = []

piece_prefab = game_object()
piece_prefab.append_component(transform)
piece_prefab.append_component(rigidbody)
piece_prefab.append_component(piece)
piece_prefab.append_component(sprite)

for comp in component_manager.all_components:
    comp.start()

# Configure game objects here

piece_prefab.get_component(piece).set_piece('None')


## Game loop
running = True
while running:

    #1 Process input/events
    for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them. 
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False
    

    #3 Draw/render
    screen.fill(BLACK)
        
    # print out your name
    
    for comp in component_manager.all_components:
        comp.on_tick(delta)

    ## Done after drawing everything to the screen
    pygame.display.flip()   

    current_time = time.time()
    delta = current_time - time_last_frame
    if delta < config.min_delta:
        time.sleep(config.min_delta - delta)
        current_time = time.time()
        delta = current_time - time_last_frame
    time_last_frame = current_time

    __a__ = 0.0001
    display_delta = (display_delta + __a__)/(delta + __a__) * delta

    print("FPS: " + str(1/display_delta))
pygame.quit()
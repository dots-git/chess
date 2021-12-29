import pygame
import time
from pygame import Vector2
from base_components import *
import math
import utility.anim as anim
from copy import copy
from utility.events import input, window

START_TIME = time.time()

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
config.set_max_fps(99999)

class piece(component):
    sprite = None
    transform = None
    rb = None
    being_moved = True
    visible = False
    scale = 1
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

    def set_position(self, position: Vector2, animate = True):
        self.position = position
        if not animate:
            self.transform.position = position

    def on_tick(self, delta: float):
        if self.piece != 'None':
            if self.being_moved:
                self.position = input.mouse_pos

            if (not approx(self.transform.position.x, self.position.x, 1)) or (not approx(self.transform.position.y, self.position.y, 1)):
                angle = (self.transform.position - self.position).angle_to(Vector2(0, 1))
                
                velocity_in_direction = 0
                velocity_in_direction += self.rb.velocity.x * math.cos(math.radians(angle + 90))
                velocity_in_direction += self.rb.velocity.y * math.cos(math.radians(angle + 180))

                distance = math.sqrt(math.pow(self.position.x - self.transform.position.x, 2) + math.pow(self.position.y - self.transform.position.y, 2))

                velocity_in_direction = anim.circular_exponential(0, velocity_in_direction, distance, 10, 500, 0.001, delta)

                self.rb.velocity.x = velocity_in_direction * math.cos(math.radians(angle + 90))
                self.rb.velocity.y = velocity_in_direction * math.cos(math.radians(angle + 180))
            else:
                self.rb.velocity = Vector2(0, 0)

            if not approx(self.transform.scale[0], self.scale, 0.01):
                current_scale = math.sqrt(self.transform.scale[0])
                target_scale = math.sqrt(self.scale)

                if target_scale > current_scale:
                    self.scale_change_rate = anim.circular_exponential(0, self.scale_change_rate, target_scale - current_scale, 7, 400, 0.001, delta)
                else:
                    self.scale_change_rate = -anim.circular_exponential(0, self.scale_change_rate, current_scale - target_scale, 7, 400, 0.001, delta)

                current_scale += self.scale_change_rate * delta

                self.transform.scale[0] = math.pow(current_scale, 2)
                self.transform.scale[1] = math.pow(current_scale, 2)

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
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hello")

current_time = time.time()
time_last_frame = current_time
delta = config.min_delta
display_delta = config.min_delta
delta_list = []
fps_display_update_time = 0.5

events = []

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

test = game_object.instantiate(piece_prefab)
test.get_component(piece).set_piece('wp')
test.name = 'Test'

piece_prefab.get_component(piece).set_piece('None')

## Game loop
running = True
while running:
    window.on_tick()
    input.on_tick()

    events = pygame.event.get()
    pygame.event.clear()
    #1 Process input/events
    for event in events:        # gets all the events which have occured till now and keeps tab of them. 
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

    #3 Draw/render
    screen.fill(BLACK)
        
    # print out your name
    
    for comp in component_manager.all_components:
        comp.on_tick(delta)

    component_manager.sort_sprites()
    for spr in component_manager.all_sprites:
        screen.blit(spr.image, (
            spr.transform.position.x - spr.transform.scale.x * spr.scale.x / 2, 
            spr.transform.position.y - spr.transform.scale.y * spr.scale.y / 2
        ))

    ## Done after drawing everything to the screen
    pygame.display.flip()   

    current_time = time.time()
    delta = current_time - time_last_frame
    if delta < config.min_delta:
        time.sleep(config.min_delta - delta)
        current_time = time.time()
        delta = current_time - time_last_frame
    time_last_frame = current_time

    delta_list.append(delta)
    fps_display_update_time -= delta
    if fps_display_update_time < 0:
        print("Fps: %i (Min: %i, Max: %i)" % (len(delta_list)/sum(delta_list), 1/max(delta_list), 1/min(delta_list)))
        delta_list = []
        fps_display_update_time = 0.5


pygame.quit()
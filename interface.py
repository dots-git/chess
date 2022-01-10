import pygame
import time
from pygame import Vector2
from pygame.constants import K_SPACE
from base_components import *
import math
import utility.anim as anim
from utility.events import input, window
from utility.utils import *

# Possible piece values
# First character is the color, second character is the piece
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

class chess():
    @staticmethod
    def str_to_square(string: str):
        return (letter_to_int(string[0]), int(string[1]) - 1)

 # A class for all configurations in the game
class config():
    max_fps = 0
    min_delta = 0
    background_color = pygame.Color(0, 0, 0)
    piece_set: str = 'default'
    piece_image_scale = 0
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
    board_image = None

    just_updated = False

    @staticmethod
    # Change the FPS limit. Exists to save resources
    def set_max_fps(value):
        config.max_fps = value
        config.min_delta = 1 / config.max_fps
        config.just_updated = True
    
    @staticmethod
    # Change the background color
    def set_background_color(color):
        config.background_color = color
        config.just_updated = True
    
    @staticmethod
    # Load a piece set
    def load_piece_set(piece_set: str):
        for piece in PIECES:
            # Load all relevant piece images
            config.piece_images[piece] = pygame.image.load(
                'assets/images/pieces/' + piece_set + '/' + piece + '.png'
            ).convert_alpha()
        # Save the scale of the image for other parts of the game to use
        config.piece_image_scale = config.piece_images['wp'].get_size()[0]
        for piece in PIECES:
            # Test if all images are the same size and quadratic
            if (config.piece_images[piece].get_size()[0] != config.piece_image_scale or
                config.piece_images[piece].get_size()[1] != config.piece_image_scale):
                config.load_piece_set('default')
        # Tell other parts of the game that the config has been updated
        config.just_updated = True
    
    @staticmethod
    # Load a board set
    def load_board_set(board_set: str):
        # Load all relevant board images (Will include clock backgrounds)
        config.board_image = pygame.image.load(
            'assets/images/board/' + board_set + '/board.png'
        ).convert_alpha()
        #Tell other parts of the game that the config has been updated
        config.just_updated = True
    
    def on_tick():
        # Reset the just_updated variable to tell other parts of the game that the config has not been updated
        config.just_updated = False

# Set the maximum FPS
config.set_max_fps(61)

class auto_anim(component):
    scale = 1
    scale_change_rate = 0
    transform = None
    rb = None
    position = Vector2(0, 0)

    def start(self):
        self.transform = self.parent.get_component(transform)
        self.rb = self.parent.get_component(rigidbody)
        # print("Set self.rb and self.transform")

    def on_tick(self, delta):
        if (not approx(self.transform.position.x, self.position.x, 1)) or (not approx(self.transform.position.y, self.position.y, 1)):
            angle = (self.transform.position - self.position).angle_to(Vector2(0, 1))
            
            velocity_in_direction = 0
            velocity_in_direction += self.rb.velocity.x * math.cos(math.radians(angle + 90))
            velocity_in_direction += self.rb.velocity.y * math.cos(math.radians(angle + 180))

            distance = math.sqrt(math.pow(self.position.x - self.transform.position.x, 2) + math.pow(self.position.y - self.transform.position.y, 2))

            velocity_in_direction = anim.circular_exponential(0, velocity_in_direction, distance, 70, 500 * self.scale, 0.0001, delta)

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

    

class piece(component):
    sprite = None
    transform = None
    animator = None
    rb = None
    scale = 1
    being_moved = False
    position = Vector2(0, 0)
    board_position = Vector2(0, 0)
    piece: str = 'None' # Can be    wp (White Pawn), 
    #                               wn (White Knight), 
    #                               wb (White Bishop), 
    #                               wr (White Rook), 
    #                               wq (White Queen), 
    #                               wk (White King), 
    #                               bp (Black Pawn), 
    #                               bn (Black Knight),  
    #                               bb (Black Bishop), 
    #                               br (Black Rook), 
    #                               bq (Black Queen), 
    #                               bk (Black King),
    #                               None (None)

    def start(self):
        self.transform = self.parent.get_component(transform)
        self.sprite = self.parent.get_component(sprite)
        self.rb = self.parent.get_component(rigidbody)
        self.animator = self.parent.get_component(auto_anim)

    def set_piece(self, piece: str):
        self.piece = piece
        if piece == 'None':
            self.sprite.set_image(pygame.Surface((0, 0)))
        else:
            self.sprite.set_image(config.piece_images[piece])

    def set_board_position(self, position: Vector2):
        self.board_position = position

    def set_position(self, position: Vector2, animate = True):
        self.position = position
        if not animate:
            self.transform.position = position
    
    def set_scale(self, scale: float, animate = True):
        self.scale = scale
        if not animate:
            self.transform.scale = Vector2(scale, scale)

    def on_tick(self, delta: float):
        if config.just_updated:
            self.set_piece(self.piece)

        if self.being_moved:
            self.position = input.mouse_pos
            self.sprite.z_layer = layer.MOVING_PIECES
        else:
            self.sprite.z_layer = layer.STILL_PIECES
            
        if self.piece != 'None':
            self.animator.scale = self.scale
            self.animator.position = self.position

    
    # def refresh_config(self):
    #     self.set_piece(self.piece)

class board(component):
    board = [['None' for i in range(8)] for j in range(8)]
    active_player = 'w'
    can_castle = {
        'wk' : True,
        'wq' : True,
        'bk' : True,
        'bq' : True,
    }
    current_move = 0
    en_passant_square = None
    fifty_move_counter = 0

    pieces: 'list[game_object]' = []

    scale = 100
    sprite = None
    board_scale = 1
    piece_scale = 1

    def load_fen(self, fen: str):
        try:
            self._load_fen_priv(fen)
        except Exception:
            return False
        self.generate_pieces(self.pieces == [])

    def _load_fen_priv(self, fen: str):
        for x in range(8):
            for y in range(8):
                self.board[x][y] = 'None'

        self.can_castle = {
        'wk' : False,
        'wq' : False,
        'bk' : False,
        'bq' : False,
        }   

        i = 0

        x = 0
        y = 0
        while fen[i] != ' ':
            if fen[i].isnumeric():
                x += int(fen[i])
            elif fen[i] == '/':
                y += 1
                x = 0
            else:
                piece = ''
                if fen[i].isupper():
                    piece += 'w'
                else:
                    piece += 'b'

                piece += fen[i].lower()

                self.board[x][y] = piece
                x += 1
            i += 1

        self.active_player = fen[i + 1]

        i += 3

        while i < len(fen) and fen[i] != ' ':
            if fen[i] != '-':
                if fen[i].isupper():
                    self.can_castle['w' + fen[i].lower()] = True
                else: 
                    self.can_castle['b' + fen[i].lower()] = True
            i += 1

        if len(fen) < i + 1: return

        if fen[i + 1] != '-':
            self.en_passant_square = chess.str_to_square(fen[i + 1:i + 3])
            i += 1

        if len(fen) < i + 3: return

        i += 3
        fifty_move_str = ''
        while i < len(fen) and fen[i] != ' ':
            fifty_move_str += fen[i]
            i += 1
        self.fifty_move_counter = int(fifty_move_str)

        if len(fen) < i + 1: return

        i += 1
        move_str = ''
        while i < len(fen):
            move_str += fen[i]
            i += 1
        self.fifty_move_counter = int(move_str) * 2 + int(self.active_player == 'b')


    def start(self):
        self.sprite = self.parent.get_component(sprite)
        self.sprite.set_image(config.board_image)

        self.update_scale_and_offset()

    def secondary_start(self):
        self.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    
    def generate_pieces(self, from_empty=True, name_start = ''):
        if from_empty:
            print("Generating pieces from empty")
            for x in range(8):
                for y in range(8):
                    if self.board[x][y] != 'None':
                        self.pieces.append(game_object.instantiate(piece_prefab))
                        comp = self.pieces[len(self.pieces) - 1].get_component(piece)
                        comp.set_piece(self.board[x][y])
                        comp.set_scale(
                            self.scale * 1/8 * 1/config.piece_image_scale * self.piece_scale, 
                            animate = False
                        )
                        comp.set_position(
                            Vector2(
                                self.scale * x / 8 + comp.scale * config.piece_image_scale / 2, 
                                self.scale * y / 8 + comp.scale * config.piece_image_scale / 2
                            ), 
                            animate = False
                        )
                        comp.board_position = Vector2(x, y)
                        self.pieces[len(self.pieces) - 1].name = name_start + "Piece at x = %f, y = %f" % (x, y)
        elif False:
            print("Generating pieces from empty")
            for p in self.pieces:
                p.remove()
            self.pieces = []
            self.generate_pieces(True)
        else:
            min_piece_distance = {
            }
            square_is_assigned = [[False for i in range(8)] for j in range(8)]
            # Move all pieces with counterparts on the current board to the closest position
            done = False
            while not done:
                # Find the minimal distance between each piece and the respective squares
                for x in range(8):
                    for y in range(8):
                        if self.board[x][y] == 'None':
                            square_is_assigned[x][y] = True
                        if not square_is_assigned[x][y]:
                            for i in range(len(self.pieces)):
                                comp = self.pieces[i].get_component(piece)
                                if comp.piece == self.board[x][y]:
                                    distance = comp.board_position.distance_to(Vector2(x, y))
                                    # Updating distance if: 
                                    # a) Piece is not registered in the distance dictionary
                                    # or b) the registered distance is greater than the current one AND it has not been given a target yet
                                    if (not i in min_piece_distance.keys()) or ((not min_piece_distance[i]['is_used']) and distance < min_piece_distance[i]['distance']):
                                        min_piece_distance[i] = {
                                            'distance': distance,
                                            'square': Vector2(x, y),
                                            'is_used': False
                                        }
                                        print("Updating distance for " + str(comp.parent.name))
                
                min_distance = math.inf
                index = 0
                for key in min_piece_distance.keys():
                    if not min_piece_distance[key]['is_used'] and min_piece_distance[key]['distance'] < min_distance:
                        min_distance = min_piece_distance[key]['distance']
                        index = key
                        min_piece_distance[key]['is_used'] = True
                        square_is_assigned[int(min_piece_distance[index]['square'].x)][int(min_piece_distance[index]['square'].y)] = True
                self.pieces[index].get_component(piece).set_board_position(min_piece_distance[index]['square'])
                self.pieces[index].get_component(piece).set_position(self.scale * comp.board_position / 8 + vec(comp.scale * config.piece_image_scale / 2))


                for key in min_piece_distance.keys():
                    if not min_piece_distance[key]['is_used']:
                        print("Piece is unused {}".format(self.pieces[key]))
                    else:
                        print("Piece {} is used at {}".format(self.pieces[key].get_component(piece).piece, self.pieces[key].get_component(piece).board_position))

                done = True
                for x in range(8):
                    for y in range(8):
                        if not square_is_assigned[x][y]:
                            done = False
                            print("Square {} is not assigned".format((x, y)))
                        else:
                            print("Square {} is assigned with {}".format((x, y), self.board[x][y]))



    def update_scale_and_offset(self):
        if window.scale.y > window.scale.x:
            self.scale = window.scale.x * self.board_scale
        else:
            self.scale = window.scale.y * self.board_scale
        
        

    def on_tick(self, delta):

        if input.key_just_pressed[K_SPACE]:
            self.load_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
            print(self.board)

        if window.just_resized:
            self.update_scale_and_offset()

            for p in self.pieces:
                comp = p.get_component(piece)
                comp.set_scale(self.scale * 1/8 * 1/config.piece_image_scale * self.piece_scale)
                if not comp.being_moved:
                    comp.set_position(self.scale * comp.board_position / 8 + vec(comp.scale * config.piece_image_scale / 2))
            
    

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


config.load_piece_set('default')

# Create game objects here

piece_prefab = game_object()
piece_prefab.append_component(transform)
piece_prefab.append_component(piece)
piece_prefab.append_component(auto_anim)
piece_prefab.append_component(rigidbody)
piece_prefab.append_component(sprite)

board_object = game_object()
board_object.append_component(transform)
board_object.append_component(board)
board_object.append_component(auto_anim)
board_object.append_component(rigidbody)
board_object.append_component(sprite)

window.on_tick()
input.on_tick()

for comp in component_manager.all_components:
    comp.start()
for comp in component_manager.all_components:
    comp.secondary_start()
# Configure game objects here

piece_prefab.get_component(piece).set_piece('None')
piece_prefab.name = 'Prefab'

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
    
    component_run_times = []

    for comp in component_manager.all_components:
        # comp_start_time = time.time()
        comp.on_tick(delta)
    #     component_run_times.append({'component': type(comp).__name__, 'game_object': comp.parent.name, 'run_time': time.time() - comp_start_time})

    # for i in range(1, len(component_run_times)):
    #         key = component_run_times[i]

    #         j = i - 1
    #         while j >= 0 and component_run_times[j]['run_time'] > key['run_time']:
    #             component_run_times[j + 1] = component_run_times[j] 
    #             j -= 1
    #         component_run_times[j + 1] = key
    
    # total_time = 0
    # for i in range(len(component_run_times)):
    #     print("Running on_tick for component {} from object {} took {} seconds".format(component_run_times[i]['component'], component_run_times[i]['game_object'], component_run_times[i]['run_time']))
    #     total_time += component_run_times[i]['run_time']
    # print("In total, all components took {} seconds, which can be executed {} times per second".format(total_time, 1/total_time))

    # draw_start_time = time.time()
    component_manager.sort_sprites()
    for spr in component_manager.all_sprites:
        screen.blit(spr.image, (
            spr.transform.position.x - spr.transform.scale.x * spr.scale.x / 2, 
            spr.transform.position.y - spr.transform.scale.y * spr.scale.y / 2
        ))
    # print("Drawing sprites took {} seconds".format(time.time() - draw_start_time))
    
    config.on_tick()

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
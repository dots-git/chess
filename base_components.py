import pygame
from pygame import Vector2
from copy import deepcopy

class layer():
    BACKGROUND = -1
    BASE = 0
    BOARD = 1
    STILL_PIECES = 2
    MOVING_PIECES = 3
    UI = 4

class component_manager():
    all_components: 'list[component]' = []
    all_sprites: 'list[sprite]' = []
    
    @staticmethod
    def sort_sprites():
        for i in range(1, len(component_manager.all_sprites)):
            key = component_manager.all_sprites[i]

            j = i - 1
            while j >= 0 and (
                (
                    component_manager.all_sprites[j].z_layer == key.z_layer and 
                    component_manager.all_sprites[j].z_order > key.z_order
                ) or (
                    component_manager.all_sprites[j].z_layer > key.z_layer
                )):
                component_manager.all_sprites[j + 1] = component_manager.all_sprites[j] 
                j -= 1
            component_manager.all_sprites[j + 1] = key

class component():
    def __init__(self, parent):
        self.parent: game_object = parent
        component_manager.all_components.append(self)
    
    def set_parent(self, parent):
        self.parent = parent

    def start(self):
        pass

    def on_tick(self, delta: float):
        pass

    def prepare_for_deepcopy(self):
        pass

    def restore_after_deepcopy(self, debug_data):
        pass

    def run_if_clone(self):
        pass

class transform(component):
    position: Vector2 = Vector2(100, 100)
    scale: Vector2 = Vector2(1, 1)

    def set_scale(self, scale: Vector2):
        self.scale = scale

    def set_position(self, position: Vector2):
        self.position = position

class rigidbody(component):
    velocity: Vector2 = Vector2(0, 0)
    transform: transform = None

    def start(self):
        self.transform = self.parent.get_component(transform)

    def on_tick(self, delta: float):
        self.transform.position += self.velocity * delta

class sprite(component):
    z_layer: int = layer.BASE
    z_order: int = 0
    og_image = pygame.Surface((0, 0))
    image = pygame.Surface((0, 0))
    scale = Vector2(1, 1)
    transform = None
    
    def set_image(self, image):
        if isinstance(image, str):
            self.og_image: pygame.Surface = pygame.image.load(image)
            self.image = self.og_image
        if isinstance(image, pygame.Surface):
            self.og_image: pygame.Surface = image.copy()
            self.image = self.og_image
        self.scale = Vector2(self.image.get_size()[0], self.image.get_size()[1])
    
    def set_scale(self, scale: Vector2):
        self.scale = scale
        self.image = pygame.transform.scale(self.image, (scale.x, scale.y))
    
    def start(self):
        self.transform = self.parent.get_component(transform)
        component_manager.all_sprites.append(self)

    def on_tick(self, delta: float):
        if self.image.get_size() is not (int(self.scale.x * self.transform.scale.x), int(self.scale.y * self.transform.scale.y)):
            self.image = pygame.transform.scale(
                self.og_image, 
                (
                    int(self.scale.x * self.transform.scale.x), 
                    int(self.scale.y * self.transform.scale.y)
                )
            )
    
    # def draw(self):
    #     pygame.display.get_surface().blit(self.image, (self.transform.position.))
    
    def prepare_for_deepcopy(self):
        temp = {'og_image': self.og_image, 'image': self.image}
        self.image = None
        self.og_image = None
        return temp
    
    def restore_after_deepcopy(self, debug_data):
        self.og_image = debug_data['og_image'].copy()
        self.image = debug_data['image'].copy()
    
    def run_if_clone(self):
        component_manager.all_sprites.append(self)


class game_object():
    def __init__(self, name = 'New Game Object'):
        self.components = []
        self.is_active = False
        self.name = name
    
    def append_component(self, comp: type):
        comp_instance = comp(self)
        self.components.append(comp_instance)
    
    def get_component(self, type):
        for comp in self.components:
            if isinstance(comp, type):
                return comp
    
    def set_active(self, is_active, call_start = False):
        self.is_active = is_active
        if call_start:
            for comp in self.components:
                comp.start()

    @staticmethod
    def instantiate(prefab: 'game_object'):
        deepcopy_debug_data = []
        for comp in prefab.components:
            # Prepare for deepcopy. Nessesary because some objects like pygame surfaces can't be pickled. WHY?!?!?!
            deepcopy_debug_data.append(comp.prepare_for_deepcopy())
        instance = deepcopy(prefab)

        for i in range(len(instance.components)):
            # Restore things like surfaces after cloning
            prefab.components[i].restore_after_deepcopy(deepcopy_debug_data[i])
            instance.components[i].restore_after_deepcopy(deepcopy_debug_data[i])
            instance.components[i].run_if_clone()

            component_manager.all_components.append(instance.components[i])
            # print(type(comp))
        return instance
import pygame
from pygame import Vector2
from copy import deepcopy

class component_manager():
    all_components: 'list[component]' = []

class component():
    def __init__(self, parent):
        self.parent: game_object = parent
        component_manager.all_components.append(self)
        print("Added component")
    
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

class transform(component):
    position: Vector2 = Vector2(0, 0)
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

    def on_tick(self, delta: float):
        if self.image.get_size() is not (int(self.scale.x * self.transform.scale.x), int(self.scale.y * self.transform.scale.y)):
            self.image = pygame.transform.scale(
                self.og_image, 
                (
                    int(self.scale.x * self.transform.scale.x), 
                    int(self.scale.y * self.transform.scale.y)
                )
            )
        pygame.display.get_surface().blit(self.image, (
            self.transform.position.x - self.scale.x * self.transform.scale.x / 2, 
            self.transform.position.y - self.scale.x * self.transform.scale.x / 2
        ))
    
    def prepare_for_deepcopy(self):

        temp = {'og_image': self.og_image, 'image': self.image}
        self.image = None
        self.og_image = None
        return temp
    
    def restore_after_deepcopy(self, debug_data):
        self.og_image = debug_data['og_image'].copy()
        self.image = debug_data['image'].copy()


class game_object():
    def __init__(self):
        self.components = []
    
    def append_component(self, comp: component):
        comp_instance = comp(self)
        self.components.append(comp_instance)
    
    def get_component(self, type):
        for comp in self.components:
            if isinstance(comp, type):
                return comp
    
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

            component_manager.all_components.append(instance.components[i])
            # print(type(comp))
        return instance
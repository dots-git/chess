from pygame import Vector2

def to_tuple(vec: Vector2):
    return (vec.x, vec.y)

def vec(i: int) -> Vector2:
    return Vector2(i, i)
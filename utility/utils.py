from pygame import Vector2
from typing import Tuple

def to_tuple(vec: Vector2):
    return (vec.x, vec.y)

def vec(i) -> Vector2:
    if isinstance(i, int):
        return Vector2(i, i)
    if isinstance(i, float):
        return Vector2(i, i)
    if isinstance(i, Tuple):
        return Vector2(i[0], i[1])

def approx(a, b, variance):
    return a < b + variance and a > b - variance

def letter_to_int(letter: str):
    return ord(letter.lower()) - 97
import pygame
class Sprite():
    path = ""
    load = pygame.Surface((15, 15))
    wight = 0
    height = 0
    def __init__(self, path):
        self.path = path
        self.load = pygame.image.load(path)
        self.wight = self.load.get_width()
        self.height = self.load.get_height()
class Font():
    font = None
    size = 20
    def __init__(self, path, size=20):
        self.size = size
        self.font = pygame.font.Font(path, size)
def lerp(a, b, t: float):
    return a * (1 - t) + b * t
def clamp(number, min, max):
    return min if number < min else max if number > max else number
class Vector():
    x = 0
    y = 0

    @staticmethod
    def zero():
        return Vector(0, 0)
    def __init__(self, x=0.0, y=0.0):
     self.x = x
     self.y = y
    def AsString(self, roundnums=2):
        return f'({round(self.x, roundnums)}, {round(self.y, roundnums)})'
    def __add__(self, other):
        if not isinstance(other, Vector):
            raise ArithmeticError("Правый операнд должен быть вектором")
        return Vector(self.x + other.x, self.y + other.y)
    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise ArithmeticError("Правый операнд должен быть float or int")
        return Vector(self.x * other, self.y * other)
    def __eq__(self, other):
        if not isinstance(other, Vector):
            raise ArithmeticError("Правый операнд должен быть вектором")
        return self.x == other.x and self.y == other.y
    def __sub__(self, other):
        if not isinstance(other, Vector):
            raise ArithmeticError("Правый операнд должен быть вектором")
        return Vector(self.x - other.x, self.y - other.y)
    def __truediv__(self, other):
        if not isinstance(other, (float, int)):
            raise ArithmeticError("Правый операнд должен быть float or int")
        return Vector(self.x/other, self.y/other)
    def __neg__(self):
        return Vector(-self.x, -self.y)
    def __str__(self):
        return f'({round(self.x, 2)}, {round(self.y, 2)})'
    def Lerp(a, b, t: float):
        nx = lerp(a.x, b.x, t)
        ny = lerp(a.y, b.y, t)
        return Vector(nx, ny)

import pygame as pg
import pygame.threads as pgt
from enum import Enum
from typing import *

pg.init()
pg.mixer.init()
screen_width: int = 600
screen_height: int = 600
screen_size: Tuple[int, int] = (screen_width, screen_height)
screen = pg.display.set_mode(screen_size)
Num = TypeVar('Num', int, float)
key_flags: List[pg.event.EventType] = []


def new_thread(loop: Callable) -> pgt.Thread:

    def run():
        while pg.QUIT not in key_flags:
            loop()
            while Time.paused:
                pg.time.wait(1)

    return pgt.Thread(target=run)


class Dir(Enum):
    FORWARD = (1, 0)
    BACKWARD = (-1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class Time(object):
    __paused: bool = True
    __paused_time: int = 0
    __previous_absolute_time: int = 0

    @classmethod
    def switch_pause(cls) -> NoReturn:
        if Time.__paused:
            cls.__paused_time += pg.time.get_ticks() - cls.__previous_absolute_time
            Time.__paused = False
            pg.mixer.music.unpause()
        else:
            cls.__previous_absolute_time = pg.time.get_ticks()
            Time.__paused = True
            pg.mixer.music.pause()

    @classmethod
    def to_pause(cls) -> NoReturn:
        if not Time.__paused:
            cls.__previous_absolute_time = pg.time.get_ticks()
            Time.__paused = True
            pg.mixer.music.pause()

    @classmethod
    def to_resume(cls) -> NoReturn:
        if Time.__paused:
            cls.__paused_time += pg.time.get_ticks() - cls.__previous_absolute_time
            Time.__paused = False
            pg.mixer.music.unpause()

    @classmethod
    def related_time(cls):
        if Time.__paused:
            return Time.__previous_absolute_time - Time.__paused_time
        else:
            return pg.time.get_ticks() - Time.__paused_time

    @classmethod
    def paused(cls):
        return cls.__paused

    @classmethod
    def paused_time(cls):
        return cls.__paused_time

    @classmethod
    def reset(cls):
        cls.__paused_time += cls.related_time()


class Sprite(object):
    _all: list = []

    def __init__(self, surface: pg.Surface, init_position: Tuple[Num, Num], align: str = "center"):
        self._birth_time: int = Time.related_time()
        self._surface: pg.Surface = surface
        self._rect: pg.Rect = surface.get_rect()
        self._align: str = align
        self._init_position: Tuple[Num, Num] = init_position
        self.tp(init_position)
        self.__class__._all.append(self)

    def tp(self, position: Tuple[Num, Num]) -> NoReturn:
        if self._align == "center":
            self._rect.center = position
        elif self._align == "topleft":
            self._rect.topleft = position
        elif self._align == "topright":
            self._rect.topright = position
        elif self._align == "bottomleft":
            self._rect.bottomleft = position
        elif self._align == "bottomright":
            self._rect.bottomright = position

    def move(self, displacement: Tuple[Num, Num]) -> NoReturn:
        self._rect = self._rect.move(displacement[0], displacement[1])

    @classmethod
    def kill(cls, target):
        try:
            cls._all.remove(target)
            del target
        except ValueError:
            pass

    @property
    def birth_time(self) -> float:
        return self._birth_time

    @property
    def age(self) -> float:
        return Time.related_time() - self._birth_time

    @property
    def rect(self) -> pg.Rect:
        return self._rect

    @property
    def surface(self) -> pg.Surface:
        return self._surface

    def refresh(self):
        screen.blit(self._surface, self._rect)

    @classmethod
    def refresh_all(cls):
        for _ in cls._all:
            _.refresh()


class TextLabel(Sprite):
    _all: list = []

    def __init__(self, filename: str, text: Callable[[], str], init_position: Tuple[Num, Num], size: int, color: Tuple[int, int, int],
                 antialias: bool = True, bg_color: Tuple[int, int, int] = None, align: str = "topleft"):
        self._filename: str = filename
        self._size: int = size
        self._font: pg.font.Font = pg.font.Font(filename, size)
        self._color: Tuple[int, int, int] = color
        self._bg_color: Tuple[int, int, int] = bg_color
        self._text: Callable[[], str] = text
        self._antialias: bool = antialias
        Sprite.__init__(self, self._font.render(text(), antialias, color, bg_color), init_position, align)

    @property
    def text(self):
        return self._text

    def refresh(self):
        self._surface = self._font.render(self._text(), self._antialias, self._color, self._bg_color)
        screen.blit(self._surface, self._rect)
        self.tp(self._init_position)

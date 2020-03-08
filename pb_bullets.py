import pygame.threads as pgt
import pygame as pg
from pb_core import Time, Sprite, Num, screen, screen_width, screen_height, key_flags
from pb_player import Player
from pb_animate import Animate
from typing import *
from math import cos, sin, sqrt

pg.init()
pg.mixer.init()


class Bullet(Sprite):
    _all = []
    sound_miss: pg.mixer.SoundType = pg.mixer.Sound('audio/combobreak.mp3')
    sound_graze: pg.mixer.SoundType = pg.mixer.Sound('audio/graze.wav')

    surface_pink_bullet: pg.Surface = pg.image.load('image/pink_bullet.png')
    surface_ani_crush: pg.Surface = pg.image.load('image/ani_explosion.png')
    surface_ani_graze: pg.Surface = pg.image.load('image/ani_graze.png')

    def __init__(self, surface: pg.Surface, orbit: Callable[[Num], Tuple[Num, Num]]):
        self._orbit: Callable[[Num], Tuple[Num, Num]] = orbit
        Sprite.__init__(self, surface, orbit(0))
        self.__grazed = False

    @property
    def orbit(self) -> Callable[([float], Tuple[(Num, Num)])]:
        return self._orbit

    def crushed(self):
        Bullet.sound_miss.play()
        Animate(Bullet.surface_ani_graze, (5, 8), self._rect.move(0, -25).center, slowness=5).start()
        Bullet.kill(self)
        Player.player().missed()

    def grazed(self):
        Bullet.sound_graze.play()
        # Animate(Bullet.surface_ani_graze, (5, 8), self._rect.center, slowness=5).start()
        Player.player().grazed()
        self.__grazed = True

    def refresh(self):
        self.tp(self.orbit(self.age))
        screen.blit(self.surface, self.rect)
        distance = sqrt((self.rect.centerx - Player.player().rect.centerx) ** 2 + (self.rect.centery - Player.player().rect.centery) ** 2)
        if self.rect.centerx < -100 or self.rect.centerx > screen_width + 100 or self.rect.centery < -100 or self.rect.centery > screen_height + 100:
            Bullet.kill(self)
        if Player.player().vincible and distance < 4:
            self.crushed()
        if Player.player().vincible and distance < 12 and not self.__grazed:
            self.grazed()

    @classmethod
    def all(cls, new_list: Union[List[Sprite], Callable[[Sprite], bool], None] = None) -> list:
        if new_list is not None:
            cls._all = new_list
        if isinstance(new_list, Callable):
            new_all = []
            for _ in cls._all:
                if new_list(_):
                    new_all.append(_)
            cls._all = new_all
        return cls._all


class UniformBullet(Bullet):
    def __init__(self, surface: pg.Surface, init_position: Tuple[Num, Num], speed: float, direction: float):
        self._init_position: Tuple[Num, Num] = init_position
        self._speed: float = speed
        self._direction: float = direction
        Bullet.__init__(self, surface, lambda t: (
            init_position[0] + speed * cos(direction) * t, init_position[1] + speed * sin(-direction) * t))

    @property
    def init_position(self) -> Tuple[Num, Num]:
        return self._init_position

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def direction(self) -> float:
        return self._direction


class AimedUniformBullet(UniformBullet):
    def __init__(self, surface: pg.Surface, init_position: Tuple[Num, Num], speed: float, target_position: Tuple[Num, Num]):
        self._init_position: Tuple[Num, Num] = init_position
        self._speed: float = speed
        self._target_position: Tuple[Num, Num] = target_position

        delta_x = target_position[0] - init_position[0]
        delta_y = target_position[1] - init_position[1]
        distance = sqrt(delta_x ** 2 + delta_y ** 2)
        x_cos = delta_x / distance
        y_cos = delta_y / distance
        Bullet.__init__(self, surface, lambda t: (
            init_position[0] + speed * x_cos * t,
            init_position[1] + speed * y_cos * t))


class Barrage(object):

    def __init__(self, bullets: List[Bullet] = None):
        if bullets is None:
            bullets = []
        self._all: List[Bullet] = bullets

    def __call__(self) -> List[Bullet]:
        return self._all

    def refresh(self):
        for _ in self._all:
            _.refresh()

    def append(self, bullet: Bullet):
        self._all.append(bullet)

    def kill(self, bullet: Bullet):
        try:
            self._all.remove(bullet)
            del bullet
        except ValueError:
            pass

    def filter(self, threshold: Callable[[Bullet], bool]):
        new_all = []
        for _ in self._all:
            if threshold(_):
                new_all.append(_)
        self._all = new_all

    def collect(self, threshold: Callable[[Bullet], bool]):
        output_all: Barrage = self.__new__(self.__class__)
        for _ in self._all:
            if threshold(_):
                output_all.append(_)
        return output_all

    def add_bullet(self, surface: pg.Surface, orbit: Callable[([float], Tuple[(Num, Num)])]) -> Bullet:
        new_bullet = Bullet(surface, orbit)
        self._all.append(new_bullet)
        return new_bullet

    def add_uniform_bullet(self, surface: pg.Surface, init_position: tuple, speed: float, direction: float) -> Bullet:
        new_bullet = UniformBullet(surface, init_position, speed, direction)
        self._all.append(new_bullet)
        return new_bullet

    def add_aimed_uniform_bullet(self, surface: pg.Surface, init_position: tuple, speed: float, target_position: tuple):
        new_bullet = AimedUniformBullet(surface, init_position, speed, target_position)
        self._all.append(new_bullet)
        return new_bullet


class BarrageThread(pgt.Thread):

    def __init__(self, unit_action: Callable[[int], NoReturn], duration: int = 256000, bgm: str = None):
        self._unit_action: Callable[[int], NoReturn] = unit_action
        self._bgm: str = bgm
        self._duration: int = duration
        self._barrage: Barrage = Barrage()
        pgt.Thread.__init__(self)

    def run(self) -> None:
        count = 0
        if self._bgm is not None:
            pg.mixer.music.load(self._bgm)
        pg.mixer.music.play()
        pg.mixer.music.pause()
        while pg.QUIT not in key_flags and pg.K_BACKSPACE not in key_flags and Time.related_time() < self._duration:
            if not Time.paused():
                self._unit_action(count)
                count += 1
            pg.time.wait(2)
        if pg.K_BACKSPACE in key_flags:
            key_flags.remove(pg.K_BACKSPACE)
            Bullet.all([])
            Time.to_pause()
            self.run()

from pb_core import pg, Sprite, screen, key_flags
from typing import *
import pygame.threads as pgt

# pg.init()


class Animate(pgt.Thread, Sprite):

    def __init__(self, surface: pg.Surface, frame_size: tuple, position: tuple,
                 slowness: int = 10):
        Sprite.__init__(self, surface, position)
        pgt.Thread.__init__(self)
        self._slowness = slowness
        self._frames = []
        frame_rect = self._rect.copy()
        frame_rect.width /= frame_size[1]
        frame_rect.height /= frame_size[0]
        for _ in range(frame_size[0] * frame_size[1]):
            frame_rect.x = _ % frame_size[1] * frame_rect.width
            frame_rect.y = _ // frame_size[1] * frame_rect.height
            self._frames.append(self._surface.subsurface(frame_rect))

        self._rect = frame_rect.copy()
        self.tp(position)

    def run(self) -> NoReturn:
        for _ in self._frames:
            screen.blit(_, self._rect)
            pg.time.wait(self._slowness)

    def __call__(self, position: Tuple[(int, int)], slowness: int = 10):
        self._rect.center = position
        self._slowness = slowness
        self.start()


class DurativeAnimate(Animate):

    def __init__(self, surface: pg.Surface, frame_size: tuple, position: tuple, duration: int,
                 slowness: int = 10):
        Animate.__init__(self, surface, frame_size, position, slowness)
        pgt.Thread.__init__(self, target=self.run)
        self._duration = duration
        self._dying = False

    def run(self) -> NoReturn:
        try:
            while self.age < self._duration or self._duration == 0:
                if not self._dying and pg.QUIT not in key_flags:
                    for _ in self._frames:
                        screen.blit(_, self._rect)
                        pg.time.wait(self._slowness)

        except pg.error:
            print("Get an error")

    def interrupt(self) -> NoReturn:
        self._dying = True

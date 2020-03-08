from pb_core import *
from typing import *
# from math import sqrt

pg.init()


class Player(Sprite):
    __player: Sprite = None
    __initialized: bool = False
    image_player: str = 'image/heart.png'
    init_position = (screen_width * 0.5, screen_height * 0.8)

    def __new__(cls, *args, **kwargs):
        if cls.__player is None:
            cls.__player = super(Player, cls).__new__(cls)
            cls.__player._slowness = 1
        return cls.__player

    def __init__(self, init_position: tuple = None):
        if init_position is not None:
            if init_position is not ():
                self.__init_position = init_position
            Sprite.__init__(self, pg.image.load(Player.image_player), self.__init_position)
            self.__slowness: int = 1
            self.__speed: int = 1
            self.__misses: List[int] = [Time.related_time()]
            self.__graze: int = 0
            self.__score: float = 0.0
            Player.__initialized = True

    @classmethod
    def player(cls):
        return cls.__player

    @property
    def slowness(self) -> float:
        return self.__slowness

    @slowness.setter
    def slowness(self, value) -> NoReturn:
        self.__slowness = value

    @property
    def speed(self) -> float:
        return self.__speed

    @speed.setter
    def speed(self, value) -> NoReturn:
        self.__speed = value

    @property
    def misses(self) -> List[int]:
        return self.__misses

    @property
    def miss(self) -> int:
        return len(self.__misses) - 1

    @property
    def graze(self) -> int:
        return self.__graze

    @property
    def score(self) -> float:
        return self.__score

    @property
    def combo_time(self) -> int:
        return Time.related_time() - self.__misses[-1]

    @property
    def vincible(self) -> bool:
        return self.miss == 0 or self.combo_time >= 2000

    def move(self, direction: Dir) -> NoReturn:
        pg.time.wait(self.__slowness)
        if direction == Dir.FORWARD and self._rect.top > 0:
            self._rect = self._rect.move((0, -self.__speed))
        elif direction == Dir.BACKWARD and self._rect.bottom < screen_height:
            self._rect = self._rect.move((0, self.__speed))
        elif direction == Dir.LEFT and self._rect.left > 0:
            self._rect = self._rect.move((-self.__speed, 0))
        elif direction == Dir.RIGHT and self._rect.right < screen_width:
            self._rect = self._rect.move((self.__speed, 0))

    def refresh(self) -> NoReturn:
        if self.vincible or Time.related_time() % 100 < 50:  # blinking effect at invincible time
            screen.blit(self._surface, self._rect)

    def missed(self) -> NoReturn:
        self.__misses.append(Time.related_time())
        self.__score -= 1

    def grazed(self) -> NoReturn:
        self.__graze += 1
        self.__score += 0.1

    def survival_score_for_each_tick(self) -> NoReturn:
        self.__score += 0.001 * (self.combo_time//2000)**0.8

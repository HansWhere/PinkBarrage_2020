from pb_bullets import *
from pb_player import *
from math import pi
import os

pg.init()
os.environ['SDL_VIDEO_WINDOWS_POS'] = '%d, %d' % (50, 50)
pg.display.set_caption('Pink Barrage')
background = 0, 0, 0
pg.mixer.init()
bgm_barrage_1: str = 'audio/3rd eye.flac'
pink_bullet_image: str = 'image/pink_bullet.png'
current_barrage: pgt.Thread


def run_ui() -> NoReturn:
    print("hello text")
    TextLabel("font/comic.ttf", lambda: "miss: "+str(Player.player().miss), (10, 0), 30, (255, 0, 0))
    TextLabel("font/comic.ttf", lambda: "graze: " + str(Player.player().graze), (10, 35), 30, (255, 0, 0))
    TextLabel("font/comic.ttf", lambda: "coef: " + str(int((Player.player().combo_time//2000)**0.8)), (10, 70), 30, (255, 0, 0))
    TextLabel("font/comic.ttf", lambda: "score: " + str(round(Player.player().score, 3)), (screen_width-100, 0), 30, (255, 255, 0), align="topright")


def run_player_control() -> NoReturn:
    while pg.QUIT not in key_flags:
        if not Time.paused():
            if pg.K_w in key_flags:
                Player.player().move(Dir.FORWARD)
            if pg.K_s in key_flags:
                Player.player().move(Dir.BACKWARD)
            if pg.K_a in key_flags:
                Player.player().move(Dir.LEFT)
            if pg.K_d in key_flags:
                Player.player().move(Dir.RIGHT)
            if pg.K_RSHIFT in key_flags:
                Player.player().slowness = 1
                Player.player().speed = 1
            else:
                Player.player().slowness = 5
                Player.player().speed = 2
        pg.time.wait(2)


def run_barrage_1() -> NoReturn:
    count = 0
    pg.mixer.music.load(bgm_barrage_1)
    pg.mixer.music.play()
    pg.mixer.music.pause()
    while pg.QUIT not in key_flags and pg.K_BACKSPACE not in key_flags and (Bullet.all() or Time.related_time() < 256000):
        if not Time.paused() and Time.related_time() < 256000:
            angle = (count - 10033) ** 2 / 12500
            UniformBullet(pg.transform.rotate(Bullet.surface_pink_bullet, angle * 180 / pi - 90),
                          (screen_width/2, screen_height/2), 0.2, angle)
            count += 1
        pg.time.wait(3)
    Time.to_pause()
    if pg.K_BACKSPACE in key_flags:
        key_flags.remove(pg.K_BACKSPACE)
        Bullet.all([])
        run_barrage_1()


# def run_barrage_1_2() -> NoReturn:
#     count = 0
#     barrage_1_2 = Barrage()
#     barrages.append(barrage_1_2)
#     while pg.QUIT not in key_flags:
#         if Time.related_time() < 256000 and not Time.paused():
#             angle = (count - 10033) ** 2 / 12500
#             b_image = pg.transform.rotate(pg.image.load(pink_bullet_image), angle * 180 / pi - 90)
#             barrage_1_2.add_uniform_bullet(b_image, (screen_width/2, screen_height/2), 0.2, angle)
#             count += 1
#         pg.time.wait(5)


def run_barrage_2() -> NoReturn:
    count = 0
    while pg.QUIT not in key_flags:
        UniformBullet(pg.image.load(pink_bullet_image), (screen_width/2, screen_height/2), 0.2, count)
        count += 1
        pg.time.wait(5)


# def run_bullet_killer() -> NoReturn:
#     while pg.QUIT not in key_flags:
#         for bullet in Bullet.all():
#             if bullet.rect.centerx < 0 or bullet.rect.centerx > screen_width or bullet.rect.centery < 0 or bullet.rect.centery > screen_height:
#                 Bullet.kill(bullet)
#             if sqrt((bullet.rect.centerx - Player.player().rect.centerx)**2 + (bullet.rect.centery - Player.player().rect.centery)**2) < 4:
#                 bullet.crushed()
#         pg.time.wait(10)


def run_barrages() -> NoReturn:
    global current_barrage

    current_barrage = pgt.Thread(target=run_barrage_1)
    current_barrage.start()

    while pg.QUIT not in key_flags:
        if not Time.paused() and current_barrage.is_alive():
            Player.player().survival_score_for_each_tick()
        pg.time.wait(100)


if __name__ == '__main__':
    print('Pink Barrage -- by Hans')
    Player((screen_width * 0.5, screen_height * 0.8))
    threads: List[pgt.Thread] = []

    thr_player_control = pgt.Thread(target=run_player_control)
    threads.append(thr_player_control)
    thr_player_control.start()

    thr_barrages = pgt.Thread(target=run_barrages)
    threads.append(thr_barrages)
    thr_barrages.start()

    thr_ui = pgt.Thread(target=run_ui)
    threads.append(thr_ui)
    thr_ui.start()

    # thr_bullet_killer = pgt.Thread(target=run_bullet_killer)
    # threads.append(thr_bullet_killer)
    # thr_bullet_killer.start()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                key_flags.append(pg.QUIT)
                for _ in threads:
                    _.join()
                pg.quit()
                quit()
                exit()
            if event.type == pg.KEYDOWN and event.key not in key_flags:
                key_flags.append(event.key)
                if event.key == pg.K_ESCAPE:
                    Time.switch_pause()
                if event.key == pg.K_BACKSPACE:
                    Player(())
            elif event.type == pg.KEYUP:
                try:
                    key_flags.remove(event.key)
                except ValueError:
                    pass
        screen.fill(background)
        pg.time.wait(2)
        Player.player().refresh()
        Bullet.refresh_all()
        TextLabel.refresh_all()
        pg.time.wait(1)
        pg.display.update()

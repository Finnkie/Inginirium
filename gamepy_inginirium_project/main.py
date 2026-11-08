import pygame as pg


def main():
    pg.init()

    screen = pg.display.set_mode((1280, 720))
    # pg.display.flip()
    # прямоугольник: (x левого верхнего угла, y, ширина, высота)
    pg.draw.rect(screen, (255, 190, 0), (40, 40, 200, 200))
    pg.draw.rect(screen, (255, 0, 0), (20, 20, 200, 200))

    pg.draw.circle(screen, (255, 190, 0), (320, 320), 80)
    pg.draw.circle(screen, (255, 0, 0), (300, 300), 80)

    pg.draw.rect(screen, (255, 190, 0), (60, 40, 200, 200))
    pg.draw.rect(screen, (255, 0, 0), (60, 20, 200, 200))

    pg.draw.circle(screen, (255, 190, 0), (380, 320), 80)
    pg.draw.circle(screen, (255, 0, 0), (360, 300), 80)

    pg.draw.rect(screen, (255, 190, 0), (80, 40, 200, 200))
    pg.draw.rect(screen, (255, 0, 0), (80, 20, 200, 200))

    pg.draw.circle(screen, (255, 190, 0), (420, 320), 80)
    pg.draw.circle(screen, (255, 0, 0), (400, 300), 80)

    pg.draw.rect(screen, (255, 190, 0), (100, 40, 200, 200))
    pg.draw.rect(screen, (255, 0, 0), (120, 20, 200, 200))

    pg.draw.circle(screen, (255, 190, 0), (520, 320), 80)
    pg.draw.circle(screen, (255, 0, 0), (500, 300), 80)

    pg.display.flip()

    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return  # выходим из main(), иначе цикл продолжится после закрытия окна
        pg.display.flip()  # показать нарисованный кадр на экране
        clock.tick(60)  # не быстрее 60 кадров в секунду


if __name__ == "__main__":
    main()

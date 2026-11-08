import pygame as pg
import numpy as np


def main():
    pg.init()

    screen = pg.display.set_mode((800, 600))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


if __name__ == "__main__":
    main()

"""Пуля: полёт, хитбокс и отрисовка."""

import pygame as pg

from settings import BULLET_SPEED, BLACK


class Bullet:
    """Пуля: летит прямолинейно, проверяется квадратом 8x8."""

    HITBOX = 8

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx * BULLET_SPEED
        self.y += self.vy * BULLET_SPEED

    @property
    def rect(self):
        return pg.Rect(self.x - 4, self.y - 4, Bullet.HITBOX, Bullet.HITBOX)

    def off_screen(self, width, height):
        return (
            self.rect.right < 0
            or self.rect.left > width
            or self.rect.bottom < 0
            or self.rect.top > height
        )

    def draw(self, screen):
        bx, by = int(self.x), int(self.y)
        pg.draw.circle(screen, BLACK, (bx, by), 8)  # чёрный контур
        pg.draw.circle(screen, (130, 130, 130), (bx, by), 6)  # серый шарик
        pg.draw.circle(screen, (175, 175, 175), (bx - 2, by - 2), 3)  # светлый блик

"""Главный герой: движение без диагоналей, стрельба и отрисовка."""

import random

import pygame as pg

from bullet import Bullet
from maze import player_cell
from settings import (
    BLACK,
    PLAYER_COLOR,
    R,
    SCALE,
    DIRECTION_VECTORS,
    DIRECTION_KEYS,
)


# Куда показывает персонаж? Отрисовка относительно направления движения:
def directed(player_x, player_y, direction, dx, dy, w, h):
    """Деталь нарисована в позе «вправо»:
    (dx, dy) - левый верхний угол относительно центра солдата,
    (w, h) - размер. Возвращает (x, y, w, h)
    на экране для текущего направления.
      right: как есть
      left:  зеркально по вертикали через центр
      up:    «вправо», повёрнутый на 90 градусов против часовой стрелки
             (ширина и высота меняются местами)
      down:  «влево», повёрнутый на 90 градусов против часовой стрелки
    """
    # масштаб применяем один раз ко всей детали
    dx, dy, w, h = dx * SCALE, dy * SCALE, w * SCALE, h * SCALE
    if direction == "right":
        return (player_x + dx, player_y + dy, w, h)
    if direction == "left":
        return (player_x - dx - w, player_y + dy, w, h)
    if direction == "up":
        return (player_x + dy, player_y - dx - w, h, w)
    return (player_x + dy, player_y + dx, h, w)


def eye_center(player_x, player_y, direction, dx, dy):
    """Центр глаз для текущего направления."""
    dx, dy = dx * SCALE, dy * SCALE
    if direction == "right":
        return (player_x + dx, player_y + dy)
    if direction == "left":
        return (player_x - dx, player_y + dy)
    if direction == "up":
        return (player_x + dy, player_y - dx)
    return (player_x + dy, player_y + dx)


class Soldier:
    """Главный герой: позиция, направление взгляда, очки и патроны.
    Умеет ходить вниз, вверх, влево, вправо и стрелять"""

    SPEED = 3  # стартовая скорость: шаг за кадр

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = "right"  # "right", "left", "up", "down"
        self.score = 0
        self.ammo = 1  # патроны: изначально один
        self.speed = self.SPEED  # скорость растёт с каждым сундуком

    # Определение клетки солдата: нужно для исключений
    def cell(self):
        return player_cell(self.x, self.y)

    def tick(self, keys):
        """Управление ЗАЖАТЫМИ клавишами"""
        if keys[pg.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
        elif keys[pg.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"
        elif keys[pg.K_UP]:
            self.y -= self.speed
            self.direction = "up"
        elif keys[pg.K_DOWN]:
            self.y += self.speed
            self.direction = "down"

    def handle_tap(self, event, keys):
        """Управление ОДИНОЧНЫМ нажатием клавиш"""
        if event.key not in (pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN):
            return
        something_held = (
            keys[pg.K_LEFT] or keys[pg.K_RIGHT] or keys[pg.K_UP] or keys[pg.K_DOWN]
        )
        if something_held:
            return
        dx, dy = DIRECTION_VECTORS[DIRECTION_KEYS[event.key]]
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.direction = DIRECTION_KEYS[event.key]

    def shoot(self):
        """Выстрел: тратит патрон и возвращает пулю из конца ствола.
        Пуля появляется от КРАЯ ТЕЛА (R)"""
        if self.ammo <= 0:
            return None
        self.ammo -= 1
        vx, vy = DIRECTION_VECTORS[self.direction]
        return Bullet(self.x + vx * R, self.y + vy * R, vx, vy)

    # Каждый сундук даёт случайно от 1 до 3 патронов
    def gain_ammo(self):
        self.ammo += random.randint(1, 3)

    # и небольшое ускорение до конца игры
    def speed_boost(self):
        self.speed += 0.1

    def draw(self, screen):
        pg.draw.circle(screen, BLACK, (self.x, self.y), R + 3)  # Контур
        pg.draw.circle(screen, PLAYER_COLOR, (self.x, self.y), R)  # тело Перонажа

        # ВНЕШНОСТЬ
        # ПРИЧЁСКА: 5 прядей, каждая вылезает за круг на 12 пикселей.
        hair = []
        for i in range(5):
            hair_dy = -46 + i * 6
            back_edge = -((2500 - hair_dy * hair_dy) ** 0.5)
            strand_from = back_edge - 12
            strand_to = 5 - i * 4
            hair.append((strand_from, hair_dy, strand_to - strand_from, 3))
        for dx, dy, w, h in hair:
            pg.draw.rect(
                screen, BLACK, directed(self.x, self.y, self.direction, dx, dy, w, h)
            )

        pg.draw.circle(
            screen, BLACK, eye_center(self.x, self.y, self.direction, 20, -15), 4
        )  # глаз
        pg.draw.rect(
            screen, BLACK, directed(self.x, self.y, self.direction, 3, -30, 35, 6)
        )  # бровь
        pg.draw.rect(
            screen,
            (60, 60, 70),
            directed(self.x, self.y, self.direction, 35, -10, 45, 20),
        )  # ствол
        pg.draw.rect(
            screen,
            (60, 60, 70),
            directed(self.x, self.y, self.direction, 35, -10, 17, 32),
        )  # рукоять

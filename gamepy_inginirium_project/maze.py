"""Лабиринт: границы арены, стены-блоки, бреши от пуль и ремонт.
Плюс помощники работы с сеткой клеток (позиции, случайная клетка)."""

import pygame as pg

from settings import (
    FIELD_LEFT,
    FIELD_TOP,
    CELL_SIZE,
    CELLS_COUNT,
    BLOCK,
)
from wall_block import WallBlock


def player_cell(player_x, player_y):
    """В какой клетке лабиринта стоит солдат."""
    col = int((player_x - FIELD_LEFT) // CELL_SIZE)
    row = int((player_y - FIELD_TOP) // CELL_SIZE)
    col = max(0, min(CELLS_COUNT - 1, col))
    row = max(0, min(CELLS_COUNT - 1, row))
    return (col, row)


def random_cell(rng, not_cell=None):
    """Случайная клетка лабиринта; not_cell можно исключить (клетка игрока)."""
    while True:
        cell = (rng.randrange(CELLS_COUNT), rng.randrange(CELLS_COUNT))
        if cell != not_cell:
            return cell


def cell_center(cell):
    """Центр клетки: сюда ставим сундук, здесь появляется солдат."""
    col, row = cell
    return (
        FIELD_LEFT + col * CELL_SIZE + CELL_SIZE // 2,
        FIELD_TOP + row * CELL_SIZE + CELL_SIZE // 2,
    )


class Maze:
    """Лабиринт: границы арены, стены-блоки, бреши от пуль и ремонт."""

    def __init__(self, rng):
        self.blocks = [
            WallBlock(pg.Rect(35, 155, 1010, 8), "border"),  # верхняя граница
            WallBlock(pg.Rect(35, 1157, 1010, 8), "border"),  # нижняя граница
            WallBlock(pg.Rect(35, 155, 8, 1010), "border"),  # левая граница
            WallBlock(pg.Rect(1037, 155, 8, 1010), "border"),  # правая граница
        ]
        self.breaches = []  # разбитые деревянные блоки - вернутся металлом

        # 1. Случайный обход: связывает ВСЕ клетки в одно целое
        linked = {(c, r): set() for c in range(CELLS_COUNT) for r in range(CELLS_COUNT)}
        visited = {(0, 0)}
        stack = [(0, 0)]
        while stack:
            c, r = stack[-1]
            neighbours = [
                (nc, nr)
                for nc, nr in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1))
                if 0 <= nc < CELLS_COUNT
                and 0 <= nr < CELLS_COUNT
                and (nc, nr) not in visited
            ]
            if not neighbours:
                stack.pop()  # тупик - отходим назад и пробуем другие пути
                continue
            nxt = rng.choice(neighbours)
            linked[(c, r)].add(nxt)
            linked[nxt].add((c, r))
            visited.add(nxt)
            stack.append(nxt)

        # 2. Петли: убираются несколько случайных стен - обходные пути
        for _ in range(6):
            c, r = rng.randrange(CELLS_COUNT), rng.randrange(CELLS_COUNT)
            choices = [
                (nc, nr)
                for nc, nr in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1))
                if 0 <= nc < CELLS_COUNT
                and 0 <= nr < CELLS_COUNT
                and (nc, nr) not in linked[(c, r)]
            ]
            if choices:
                nxt = rng.choice(choices)
                linked[(c, r)].add(nxt)
                linked[nxt].add((c, r))

        # 3. Ставим деревянные стены там, где клетки НЕ связаны
        for c in range(CELLS_COUNT):
            for r in range(CELLS_COUNT):
                if c + 1 < CELLS_COUNT and (c + 1, r) not in linked[(c, r)]:
                    x = FIELD_LEFT + (c + 1) * CELL_SIZE
                    self._chop(x - 4, FIELD_TOP + r * CELL_SIZE, 8, CELL_SIZE)
                if r + 1 < CELLS_COUNT and (c, r + 1) not in linked[(c, r)]:
                    y = FIELD_TOP + (r + 1) * CELL_SIZE
                    self._chop(FIELD_LEFT + c * CELL_SIZE, y - 4, CELL_SIZE, 8)

    def _chop(self, x, y, w, h):
        """Линия стены -> блоки длиной BLOCK, толщина не меняется."""
        if w >= h:  # горизонтальная: рубим по длине
            x0 = x
            while x0 < x + w:
                seg = min(BLOCK, x + w - x0)
                self.blocks.append(WallBlock(pg.Rect(x0, y, seg, h), "wood"))
                x0 += BLOCK
        else:  # вертикальная: рубим по высоте
            y0 = y
            while y0 < y + h:
                seg = min(BLOCK, y + h - y0)
                self.blocks.append(WallBlock(pg.Rect(x, y0, w, seg), "wood"))
                y0 += BLOCK

    def handle_bullet(self, bullet):
        """Пуля врезалась в блок: граница гасит пулю без разрушения,
        дерево разбивается с одного выстрела (и уходит в бреши -
        при ремонте вернётся металлом), металл трескается с первого
        выстрела и разрушается со второго (и НЕ возрождается).
        Возвращает True, если пуля погасла."""
        for i, block in enumerate(self.blocks):
            if bullet.rect.colliderect(block.rect):
                destroyed = block.hit()
                if destroyed and block.material == "wood":
                    self.breaches.append(block)
                    self.blocks.pop(i)
                elif destroyed:
                    # разбитый металл не уходит в бреши - значит не вернётся
                    self.blocks.pop(i)
                return True
        return False

    def repair(self):
        """РЕМОНТ ЛАБИРИНТА: разбитые деревянные блоки возвращаются ровно
        на свои места металлическими. Разбитый металл не восстанавливается."""
        for block in self.breaches:
            block.material = "metal"
            block.hp = 2
            self.blocks.append(block)
        self.breaches = []

    def draw(self, screen):
        for block in self.blocks:
            block.draw(screen)

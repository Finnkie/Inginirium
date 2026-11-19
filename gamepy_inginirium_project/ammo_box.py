import pygame as pg

from maze import cell_center, random_cell

BLACK = (20, 20, 20)


class AmmoBox:
    def __init__(self, cell):
        self.cell = cell
        self.x, self.y = cell_center(cell)

    def move_to_random(self, rng, not_cell):
        """Ящик перерождается в случайной клетке, кроме занятой солдатом."""
        self.cell = random_cell(rng, not_cell=not_cell)
        self.x, self.y = cell_center(self.cell)

    @property
    def rect(self):
        return pg.Rect(self.x - 24, self.y - 24, 48, 48)

    def draw(self, screen):
        body = (185, 145, 90)  # светлое дерево ящика
        plank = (165, 120, 65)  # доски - на тон темнее тела
        cx, cy = self.x, self.y
        # квадрат-ящик
        pg.draw.rect(screen, body, (cx - 24, cy - 24, 48, 48))
        # чёрная окайма по периметру
        pg.draw.rect(screen, BLACK, (cx - 24, cy - 24, 48, 48), width=4)
        # пара досок поперёк - торчат за контур на 5 пикселей
        for dx in (-12, 12):
            plank_rect = pg.Rect(cx + dx - 6, cy - 29, 12, 58)
            pg.draw.rect(screen, plank, plank_rect)
            pg.draw.rect(screen, BLACK, plank_rect, width=2)
        # пара досок вдоль (поперёк первой пары) - тоже торчат за контур
        for dy in (-12, 12):
            plank_rect = pg.Rect(cx - 29, cy + dy - 6, 58, 12)
            pg.draw.rect(screen, plank, plank_rect)
            pg.draw.rect(screen, BLACK, plank_rect, width=2)

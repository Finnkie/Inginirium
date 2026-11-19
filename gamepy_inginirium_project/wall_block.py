import pygame as pg

from settings import WALL_COLOR, METAL_COLOR, BLACK


class WallBlock:
    HP_BY_MATERIAL = {"wood": 1, "metal": 2}

    def __init__(self, rect, material):
        self.rect = rect
        self.material = material
        self.hp = self.HP_BY_MATERIAL.get(material, 9999)

    def hit(self):
        """Выстрел в блок. Возвращает True, если блок разрушен."""
        if self.material == "border":
            return False  # граница держит сколько угодно выстрелов
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        if self.material == "metal":
            pg.draw.rect(screen, METAL_COLOR, self.rect)
            # чёрные полоски поперёк блока
            if self.rect.w >= self.rect.h:
                for sx in range(self.rect.left + 5, self.rect.right - 2, 12):
                    pg.draw.rect(
                        screen, BLACK, (sx, self.rect.top + 1, 2, self.rect.h - 2)
                    )
            else:
                for sy in range(self.rect.top + 5, self.rect.bottom - 2, 12):
                    pg.draw.rect(
                        screen, BLACK, (self.rect.left + 1, sy, self.rect.w - 2, 2)
                    )
            if self.hp == 1:
                # ПЕРЕХОДНОЕ СОСТОЯНИЕ: сеть трещин - блок держится из последних
                # сил. Главная трещина вдоль блока плюс лучи к четырём углам.
                cx, cy = self.rect.center
                left, right = self.rect.left, self.rect.right
                top, bottom = self.rect.top, self.rect.bottom
                # главная трещина вдоль блока
                pg.draw.line(screen, BLACK, (left + 4, cy - 2), (cx, cy + 2), 2)
                pg.draw.line(screen, BLACK, (cx, cy + 2), (right - 4, cy - 3), 2)
                # расходящиеся трещины к углам
                pg.draw.line(screen, BLACK, (cx, cy), (left + 5, top + 3), 1)
                pg.draw.line(screen, BLACK, (cx, cy), (right - 5, top + 3), 1)
                pg.draw.line(screen, BLACK, (cx, cy), (left + 5, bottom - 3), 1)
                pg.draw.line(screen, BLACK, (cx, cy), (right - 5, bottom - 3), 1)
        else:
            pg.draw.rect(screen, WALL_COLOR, self.rect)

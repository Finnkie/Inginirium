import random
import sqlite3
from datetime import datetime

import pygame as pg

# импорт констант настроек и визуального стиля
from settings import (
    BLACK,
    BLOCK,
    BULLET_SPEED,
    CELL_SIZE,
    CELLS_COUNT,
    DB_FILE,
    DIRECTION_KEYS,
    DIRECTION_VECTORS,
    FIELD_LEFT,
    FIELD_TOP,
    FLOOR_COLOR,
    GAME_TIMER,
    METAL_COLOR,
    PLAYER_COLOR,
    R,
    SCALE,
    WALL_COLOR,
)


# Куда показывает персонаж? Отрисовка относительно направления движения:
def directed(player_x, player_y, direction, dx, dy, w, h):
    """Деталь нарисована в позе «вправо»:
    (dx, dy) - левый верхний угол относительно центра солдата,
    (w, h) - размер. Возвращает (x, y, w, h)
    на экране для текущего направления.
      right: как есть
      left:  зеркало по вертикали через центр
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
    """Центр круглой детали (глаз) для текущего направления."""
    dx, dy = dx * SCALE, dy * SCALE
    if direction == "right":
        return (player_x + dx, player_y + dy)
    if direction == "left":
        return (player_x - dx, player_y + dy)
    if direction == "up":
        return (player_x + dy, player_y - dx)
    return (player_x + dy, player_y + dx)


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


class Soldier:
    """Главный герой: позиция, направление взгляда, очки и патроны.
    Умеет ходить (без диагоналей), стрелять и рисовать себя."""

    SPEED = 3  # стартовая скорость: шаг за кадр

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = "right"  # "right", "left", "up", "down"
        self.score = 0
        self.ammo = 1  # патроны: изначально один
        self.speed = self.SPEED  # скорость растёт с каждым сундуком

    def cell(self):
        """Клетка лабиринта, в которой стоит солдат."""
        return player_cell(self.x, self.y)

    def tick(self, keys):
        """ЗАЖАТЫЕ клавиши. elif вместо if: сработает только ПЕРВАЯ зажатая
        клавиша из списка - диагональное движение невозможно."""
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
        """ОДИНОЧНОЕ нажатие стрелки: засчитывается, только если ни одна
        кнопка движения не зажата - иначе вышел бы шаг по диагонали."""
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

    def speed_up(self):
        """Сундук подбран - солдат бегает чуть быстрее (+0.25 px за кадр)."""
        self.speed += 0.25

    def shoot(self):
        """Выстрел: тратит патрон и возвращает пулю из конца ствола.
        Пуля появляется от КРАЯ ТЕЛА (R) - коллизия гарантирует, что стена
        не бывает ближе R к центру, значит сквозь неё пуля не родится."""
        if self.ammo <= 0:
            return None
        self.ammo -= 1
        vx, vy = DIRECTION_VECTORS[self.direction]
        return Bullet(self.x + vx * R, self.y + vy * R, vx, vy)

    def gain_ammo(self):
        """Каждый сундук даёт случайно от 1 до 3 патронов."""
        self.ammo += random.randint(1, 3)

    def draw(self, screen):
        pg.draw.circle(screen, PLAYER_COLOR, (self.x, self.y), R)

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


class Bullet:
    """Пуля: летит прямолинейно, проверяется квадратиком 8x8. Его размер
    равен скорости полёта, поэтому зоны проверки соседних кадров стыкуются
    вплотную - пуля не может перепрыгнуть стену толщиной 8."""

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


class WallBlock:
    """Один блок стены.
    material "border": граница арены - неразрушима;
    material "wood":   разбивается с одного выстрела; при ремонте
                       лабиринта возвращается МЕТАЛЛИЧЕСКИМ;
    material "metal":  держит ДВА выстрела (после первого покрывается
                       трещинами); разбитый металл при ремонте
                       НЕ возрождается - дыра остаётся навсегда.
    """

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


class Maze:
    """Лабиринт: границы арены, стены-блоки, бреши от пуль и ремонт."""

    def __init__(self, rng):
        self.blocks = [
            WallBlock(pg.Rect(35, 35, 8, 1010), "border"),  # левая граница
            WallBlock(pg.Rect(35, 35, 1010, 8), "border"),  # верхняя граница
            WallBlock(pg.Rect(35, 1037, 1010, 8), "border"),  # нижняя граница
            WallBlock(pg.Rect(1037, 35, 8, 1010), "border"),  # правая граница
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


class Chest:
    """Оружейный сундук: тёмно-коричневое тело с редкими досками, крышка
    с частыми досками, золотой замок и чёрный контур."""

    def __init__(self, cell):
        self.cell = cell
        self.x, self.y = cell_center(cell)

    def move_to_random(self, rng, not_cell):
        """Сундук перерождается в случайной клетке, кроме занятой солдатом."""
        self.cell = random_cell(rng, not_cell=not_cell)
        self.x, self.y = cell_center(self.cell)

    @property
    def rect(self):
        return pg.Rect(self.x - 30, self.y - 18, 60, 44)

    def draw(self, screen):
        body = (110, 70, 35)
        gold = (218, 165, 32)
        cx, cy = self.x, self.y
        # тело ящика
        pg.draw.rect(screen, body, (cx - 30, cy - 4, 60, 30))
        # редкие поперечные линии на теле
        for i in range(1, 4):
            pg.draw.rect(screen, BLACK, (cx - 30 + i * 15, cy - 4, 2, 30))
        # крышка
        pg.draw.rect(screen, body, (cx - 30, cy - 18, 60, 14))
        # десяток тонких поперечных линий на крышке (зазоры между досками)
        for i in range(1, 11):
            pg.draw.rect(
                screen, BLACK, (int(cx - 30 + i * 60 / 11) - 1, cy - 18, 2, 14)
            )
        # палочка-разделитель между крышкой и телом
        pg.draw.rect(screen, BLACK, (cx - 30, cy - 5, 60, 4))
        # золотой замок ближе к крышке, по центру (поверх разделителя)
        pg.draw.rect(screen, gold, (cx - 7, cy - 6, 14, 12))
        # чёрный контур вокруг всего сундука, толщина - как у разделителя
        pg.draw.rect(screen, BLACK, (cx - 30, cy - 18, 60, 44), width=4)


class ResultDB:
    """Логи результатов в SQLite: сохранение раундов и топ-5 игроков.
    При равенстве очков выше тот, кто набрал их раньше."""

    def __init__(self, path):
        self.path = path
        conn = sqlite3.connect(self.path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS results ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nickname TEXT NOT NULL, "
            "score INTEGER NOT NULL, "
            "played_at TEXT NOT NULL)"
        )
        conn.commit()
        conn.close()

    def save(self, nickname, score):
        """Сохраняет результат раунда и возвращает топ-5: список пар
        (ник, очки)."""
        conn = sqlite3.connect(self.path)
        played_at = datetime.now().strftime("%d.%m.%Y %H:%M")
        conn.execute(
            "INSERT INTO results (nickname, score, played_at) VALUES (?, ?, ?)",
            (nickname, score, played_at),
        )
        conn.commit()
        top = conn.execute(
            "SELECT nickname, score FROM results "
            "ORDER BY score DESC, played_at ASC LIMIT 5"
        ).fetchall()
        conn.close()
        return top


def main():
    pg.init()

    screen = pg.display.set_mode((1080, 1080))
    rng = random.Random()
    clock = pg.time.Clock()
    font = pg.font.Font(None, 56)
    big_font = pg.font.Font(None, 96)

    db = ResultDB(DB_FILE)  # логи результатов в SQLite
    maze = Maze(rng)  # границы + лабиринт из блоков
    chest = Chest(random_cell(rng, not_cell=(0, 0)))
    soldier = Soldier(*cell_center((0, 0)))  # верхний левый угол, смотрит вправо
    bullets = []  # летящие пули

    # ВВОД НИКНЕЙМА: первый экран игры, Enter - начать раунд
    entering_nickname = True
    nickname = ""
    result_top = None  # топ-5 из базы, появляется на экране результата
    game_over = False
    last_ticks = pg.time.get_ticks()
    time_left = float(GAME_TIMER)  # таймер хранит дробные секунды

    while True:
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return  # выход из main()
            # после конца игры ESC тоже закрывает
            if game_over and event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                return

            # ввод никнейма: печатаем буквы, Backspace стирает, Enter - старт
            if entering_nickname and event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    entering_nickname = False
                    if not nickname:
                        nickname = "Игрок"  # пустой ник не оставляем
                elif event.key == pg.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif (
                    event.unicode and event.unicode.isprintable() and len(nickname) < 15
                ):
                    nickname += event.unicode
                continue  # пока вводим ник - стрелки и пробел не работают

            if game_over:
                continue  # в игре больше не кликаем

            # ВЫСТРЕЛ: одиночный пробел, тратит патрон, пуля летит по взгляду
            # (стрелять можно и на бегу - пробел не блокируется зажатыми стрелками)
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                bullet = soldier.shoot()
                if bullet:
                    bullets.append(bullet)

            # ОДИНОЧНЫЕ нажатия стрелок (без диагоналей)
            if event.type == pg.KEYDOWN:
                soldier.handle_tap(event, keys)

        # ЭКРАН ВВОДА НИКА: игра ещё не началась, таймер стоит на месте
        if entering_nickname:
            screen.fill((30, 30, 50))
            t1 = font.render("Введите имя игрока и нажми Enter:", True, (230, 230, 230))
            t2 = big_font.render(nickname + "_", True, (240, 220, 120))
            center_x = screen.get_width() // 2
            screen.blit(t1, (center_x - t1.get_width() // 2, 420))
            screen.blit(t2, (center_x - t2.get_width() // 2, 520))
            pg.display.flip()
            clock.tick(60)
            continue

        # ТАЙМЕР: 60 секунд, тикают вниз дробями; сундуки добавляют 1-3 секунды
        now = pg.time.get_ticks()
        time_left -= (now - last_ticks) / 1000
        last_ticks = now
        seconds_left = max(0, int(time_left))
        if time_left <= 0 and not game_over:
            # конец раунда: результат уходит в базу, достаём топ-5
            game_over = True
            result_top = db.save(nickname, soldier.score)

        if game_over:
            # ЭКРАН РЕЗУЛЬТАТА: итог игрока + топ-5 из базы
            screen.fill((40, 40, 60))
            t1 = big_font.render("ВРЕМЯ ВЫШЛО!", True, (240, 220, 120))
            t2 = font.render(
                f"{nickname} собрал сундуков: {soldier.score}", True, (240, 240, 240)
            )
            t3 = font.render("Нажми ESC или закрой окно", True, (180, 180, 180))
            center_x = screen.get_width() // 2
            screen.blit(t1, (center_x - t1.get_width() // 2, 240))
            screen.blit(t2, (center_x - t2.get_width() // 2, 370))
            t4 = font.render("ТОП-5 ИГРОКОВ:", True, (120, 220, 120))
            screen.blit(t4, (center_x - t4.get_width() // 2, 470))
            for i, (top_nick, top_score) in enumerate(result_top or [], 1):
                # свой результат подсвечивается золотым
                color = (240, 220, 120) if top_nick == nickname else (200, 200, 200)
                row = font.render(f"{i}. {top_nick} - {top_score}", True, color)
                screen.blit(row, (center_x - 150, 530 + i * 60))
            screen.blit(t3, (center_x - t3.get_width() // 2, 920))
            pg.display.flip()
            clock.tick(60)
            continue

        screen.fill(FLOOR_COLOR)

        # стены: границы + лабиринт + металлические блоки
        maze.draw(screen)

        # сундук
        chest.draw(screen)

        # солдат: тело, причёска, глаз, бровь, пистолет «Г»
        soldier.draw(screen)

        # ПУЛИ: чёрный контур, серый шарик, чуть более светлый блик
        for bullet in bullets:
            bullet.draw(screen)

        # Насчитывается только одиночное ЗАЖАТИЕ
        soldier.tick(keys)

        # ЖЁСТКАЯ КОЛЛИЗИЯ: круг выталкивается из каждого блока (и из
        # металлических тоже), в который залез.
        for block in maze.blocks:
            near_x = max(block.rect.left, min(soldier.x, block.rect.right))
            near_y = max(block.rect.top, min(soldier.y, block.rect.bottom))
            push_x = soldier.x - near_x
            push_y = soldier.y - near_y
            dist_sq = push_x * push_x + push_y * push_y
            if dist_sq < R * R:
                if dist_sq == 0:
                    soldier.y = block.rect.top - R  # редкий случай: центр внутри
                else:
                    dist = dist_sq**0.5
                    soldier.x = near_x + push_x / dist * R
                    soldier.y = near_y + push_y / dist * R

        # ПОДАЧА СУНДУКА: подобрал - очко, бонус времени, патроны,
        # лабиринт ремонтируется (бреши становятся металлом), сундук перерождается
        chest_dx = soldier.x - chest.x
        chest_dy = soldier.y - chest.y
        if chest_dx * chest_dx + chest_dy * chest_dy < (R + 30) * (R + 30):
            soldier.score += 1
            # бонус времени: от 1 секунды в начале раунда до 3 секунд под конец -
            # чем меньше времени осталось, тем больше прибавка
            time_bonus = 1 + 2 * (1 - time_left / GAME_TIMER)
            time_left += time_bonus
            soldier.gain_ammo()
            soldier.speed_up()  # чуточку ускоряется - до конца игры
            maze.repair()
            chest.move_to_random(rng, not_cell=soldier.cell())

        # ПУЛИ: летят по направлению выстрела. Кусок лабиринта разбивается
        # с одного выстрела и уходит в бреши (при подборе сундука вернётся
        # металлом). Металл держит два выстрела: первый - трещины, второй -
        # блок исчезает НАВСЕГДА (при ремонте не возвращается). Границы
        # неразрушимы. Пулей можно разбить и сундук - он переродится,
        # но очков и бонусов за разбитый сундук нет.
        for bullet in bullets:
            bullet.update()
        alive_bullets = []
        for bullet in bullets:
            if bullet.off_screen(screen.get_width(), screen.get_height()):
                continue  # улетела за экран
            if maze.handle_bullet(bullet):
                continue  # погасилась о стену
            if chest.rect.colliderect(bullet.rect):
                # разбил сундук: он перерождается, но без награды
                chest.move_to_random(rng, not_cell=soldier.cell())
                continue
            alive_bullets.append(bullet)
        bullets = alive_bullets

        # Интерфейс: патроны в левом углу, очки и время - в правом (время под очками)
        ammo_surf = font.render(f"Патроны: {soldier.ammo}", True, (150, 60, 20))
        score_surf = font.render(f"Очки: {soldier.score}", True, (40, 60, 120))
        timer_surf = font.render(f"Время: {seconds_left}", True, (120, 40, 40))
        screen.blit(ammo_surf, (50, 40))
        screen.blit(score_surf, (screen.get_width() - score_surf.get_width() - 50, 40))
        screen.blit(timer_surf, (screen.get_width() - timer_surf.get_width() - 50, 115))

        pg.display.flip()
        clock.tick(60)  # 60 кадров в секунду


if __name__ == "__main__":
    main()

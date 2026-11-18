import pygame as pg
import random

# Масштаб Персонажа:
SCALE = 0.6
R = int(50 * SCALE)  # размер Персонажа (радиус)

WALL_COLOR = (170, 120, 70)  # стены и границы в RGB
FLOOR_COLOR = (220, 220, 220)  # пол в RGB
PLAYER_COLOR = (60, 130, 60)  # Персонаж-солтат в RGB

FIELD_LEFT = 43  # внутренний край левой стены
FIELD_TOP = 43  # внутренний край верхней стены
CELL_SIZE = 71  # размер клетки: в 2 раза уже старой (проход 65 > диаметра 60)
CELLS_COUNT = 14  # клеток по каждой стороне: 14 x 14 - лабиринт крупнее и хитрее

GAME_TIMER = 60  # длительность раунда

# Блок стены: длина стандартного куска и стандартная ширина прохода.
BLOCK = 76

BULLET_SPEED = 8  # скорость пули: пикселей за кадр
DIRECTION_VECTORS = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1),
}


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


def build_walls(rng):
    """Границы арены + лабиринт, построенный алгоритмом «случайного обхода».

    Обходчик блуждает по клеткам 7x7 и прокладывает проходы между ними;
    между клетками, которые он НЕ связал, ставится стена. Получается
    случайно сгенерированный лабиринт с тупиками, где все клетки карты
    можно обойти.
    Потом несколько лишних стен убирается - появляются петли-обходы.
    Все стены нарублены на куски длиной около радиуса Персонажа.
    """
    walls = [
        pg.Rect(35, 35, 8, 1010),  # левая граница
        pg.Rect(35, 35, 1010, 8),  # верхняя граница
        pg.Rect(35, 1037, 1010, 8),  # нижняя граница
        pg.Rect(1037, 35, 8, 1010),  # правая граница
    ]

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

    # 2. Петли: убираются несколько случайных стен - появляются обходные пути
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

    # 3. Ставим стены там, где клетки НЕ связаны; рубим на блоки длиной BLOCK
    def chop(x, y, w, h):
        if w >= h:  # горизонтальная: рубим по длине
            x0 = x
            while x0 < x + w:
                seg = min(BLOCK, x + w - x0)
                walls.append(pg.Rect(x0, y, seg, h))
                x0 += BLOCK
        else:  # вертикальная: рубим по высоте
            y0 = y
            while y0 < y + h:
                seg = min(BLOCK, y + h - y0)
                walls.append(pg.Rect(x, y0, w, seg))
                y0 += BLOCK

    for c in range(CELLS_COUNT):
        for r in range(CELLS_COUNT):
            # вертикальная стена справа от клетки (c, r)?
            if c + 1 < CELLS_COUNT and (c + 1, r) not in linked[(c, r)]:
                x = FIELD_LEFT + (c + 1) * CELL_SIZE
                chop(x - 4, FIELD_TOP + r * CELL_SIZE, 8, CELL_SIZE)
            # горизонтальная стена снизу от клетки (c, r)?
            if r + 1 < CELLS_COUNT and (c, r + 1) not in linked[(c, r)]:
                y = FIELD_TOP + (r + 1) * CELL_SIZE
                chop(FIELD_LEFT + c * CELL_SIZE, y - 4, CELL_SIZE, 8)
    return walls


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


def player_cell(player_x, player_y):
    """В какой клетке лабиринта стоит солдат."""
    col = int((player_x - FIELD_LEFT) // CELL_SIZE)
    row = int((player_y - FIELD_TOP) // CELL_SIZE)
    col = max(0, min(CELLS_COUNT - 1, col))
    row = max(0, min(CELLS_COUNT - 1, row))
    return (col, row)


def draw_chest(screen, cx, cy):
    """Оружейный сундук: тёмно-коричневое тело, крышка с частыми досками,
    редкие линии на теле, золотой замок ближе к крышке по центру."""
    body = (110, 70, 35)
    black = (20, 20, 20)
    gold = (218, 165, 32)
    # тело ящика
    pg.draw.rect(screen, body, (cx - 30, cy - 4, 60, 30))
    # редкие поперечные линии на теле
    for i in range(1, 4):
        pg.draw.rect(screen, black, (cx - 30 + i * 15, cy - 4, 2, 30))
    pg.draw.rect(screen, body, (cx - 30, cy - 18, 60, 14))
    # доски на крышке сундука
    for i in range(1, 11):
        pg.draw.rect(screen, black, (int(cx - 30 + i * 60 / 11) - 1, cy - 18, 2, 14))
    pg.draw.rect(screen, black, (cx - 30, cy - 5, 60, 4))
    # золотой замок на ящике
    pg.draw.rect(screen, gold, (cx - 7, cy - 6, 14, 12))
    # чёрный контур вокруг всего сундука, толщина - как у разделителя
    pg.draw.rect(screen, black, (cx - 30, cy - 18, 60, 44), width=4)


def main():
    pg.init()

    screen = pg.display.set_mode((1080, 1080))
    rng = random.Random()
    font = pg.font.Font(None, 56)
    big_font = pg.font.Font(None, 96)

    walls = build_walls(rng)
    metal_walls = []  # противоударные заплатки: пулей не разбиваются до конца игры
    holes = []  # дыры от пуль - при подборе сундука заливаются металлом

    # солдат появляется в верхнем левом углу (центр клетки (0, 0)) и
    # смотрит вправо
    player_x, player_y = cell_center((0, 0))
    direction = "right"  # "right", "left", "up", "down"
    score = 0
    ammo = 1  # патроны: изначально один
    bullets = []  # летящие пули: [x, y, vx, vy]

    # первый сундук - в случайной клетке, но не там, где стоит солдат
    chest_cell = random_cell(rng, not_cell=player_cell(player_x, player_y))
    chest_x, chest_y = cell_center(chest_cell)

    clock = pg.time.Clock()
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

            # ВЫСТРЕЛ: одиночный пробел, тратит патрон, пуля летит по взгляду
            # (стрелять можно и на бегу - пробел не блокируется зажатыми стрелками)
            if not game_over and event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if ammo > 0:
                    ammo -= 1
                    vx, vy = DIRECTION_VECTORS[direction]
                    # пуля появляется от КРАЯ ТЕЛА Персонажа (R)
                    bullets.append([player_x + vx * R, player_y + vy * R, vx, vy])

            # Засчитывается только одиночное НАЖАТИЕ (и только в игре)
            if not game_over and event.type == pg.KEYDOWN:
                something_held = (
                    keys[pg.K_LEFT]
                    or keys[pg.K_RIGHT]
                    or keys[pg.K_UP]
                    or keys[pg.K_DOWN]
                )
                if not something_held:
                    if event.key == pg.K_LEFT:
                        player_x -= 3
                        direction = "left"
                    elif event.key == pg.K_RIGHT:
                        player_x += 3
                        direction = "right"
                    elif event.key == pg.K_UP:
                        player_y -= 3
                        direction = "up"
                    elif event.key == pg.K_DOWN:
                        player_y += 3
                        direction = "down"

        # ТАЙМЕР: 60 секунд, тикают вниз дробями; сундуки добавляют 1-3 секунды
        now = pg.time.get_ticks()
        time_left -= (now - last_ticks) / 1000
        last_ticks = now
        seconds_left = max(0, int(time_left))
        if time_left <= 0:
            game_over = True

        if game_over:
            # ЭКРАН РЕЗУЛЬТАТА
            screen.fill((40, 40, 60))
            t1 = big_font.render("ВРЕМЯ ВЫШЛО!", True, (240, 220, 120))
            t2 = font.render(f"Собрано сундуков: {score}", True, (240, 240, 240))
            t3 = font.render("Нажми ESC или закрой окно", True, (180, 180, 180))
            screen.blit(t1, (screen.get_width() // 2 - t1.get_width() // 2, 380))
            screen.blit(t2, (screen.get_width() // 2 - t2.get_width() // 2, 520))
            screen.blit(t3, (screen.get_width() // 2 - t3.get_width() // 2, 620))
            pg.display.flip()
            clock.tick(60)
            continue

        screen.fill(FLOOR_COLOR)

        # стены: границы + лабиринт
        for wall in walls:
            pg.draw.rect(screen, WALL_COLOR, wall)

        # МЕТАЛЛИЧЕСКИЕ ЗАПЛАТКИ: тёмно-серые с чёрными полосками поперёк
        for wall in metal_walls:
            pg.draw.rect(screen, (90, 90, 95), wall)
            if wall.w >= wall.h:
                for sx in range(wall.left + 5, wall.right - 2, 12):
                    pg.draw.rect(
                        screen, (20, 20, 20), (sx, wall.top + 1, 2, wall.h - 2)
                    )
            else:
                for sy in range(wall.top + 5, wall.bottom - 2, 12):
                    pg.draw.rect(
                        screen, (20, 20, 20), (wall.left + 1, sy, wall.w - 2, 2)
                    )

        # сундук
        draw_chest(screen, chest_x, chest_y)

        # Персонаж: СОЛДАТ (тёмно-зелёный)
        pg.draw.circle(screen, PLAYER_COLOR, (player_x, player_y), R)

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
                screen,
                (20, 20, 20),
                directed(player_x, player_y, direction, dx, dy, w, h),
            )

        pg.draw.circle(
            screen, (20, 20, 20), eye_center(player_x, player_y, direction, 20, -15), 4
        )  # глаз
        pg.draw.rect(
            screen, (20, 20, 20), directed(player_x, player_y, direction, 3, -30, 35, 6)
        )  # бровь
        pg.draw.rect(
            screen,
            (60, 60, 70),
            directed(player_x, player_y, direction, 35, -10, 45, 20),
        )  # ствол
        pg.draw.rect(
            screen,
            (60, 60, 70),
            directed(player_x, player_y, direction, 35, -10, 17, 32),
        )  # рукоять

        # ПУЛИ: чёрный контур, серый шарик, чуть более светлый блик
        for bullet in bullets:
            bx, by = int(bullet[0]), int(bullet[1])
            pg.draw.circle(screen, (20, 20, 20), (bx, by), 8)
            pg.draw.circle(screen, (130, 130, 130), (bx, by), 6)
            pg.draw.circle(screen, (175, 175, 175), (bx - 2, by - 2), 3)

        # Насчитывается только одиночное ЗАЖАТИЕ
        if keys[pg.K_LEFT]:
            player_x -= 3
            direction = "left"
        elif keys[pg.K_RIGHT]:
            player_x += 3
            direction = "right"
        elif keys[pg.K_UP]:
            player_y -= 3
            direction = "up"
        elif keys[pg.K_DOWN]:
            player_y += 3
            direction = "down"

        # ЖЁСТКАЯ КОЛЛИЗИЯ: круг выталкивается из каждой стены (и из
        # металлических заплаток тоже), в которую залез.
        for wall in walls + metal_walls:
            near_x = max(wall.left, min(player_x, wall.right))
            near_y = max(wall.top, min(player_y, wall.bottom))
            push_x = player_x - near_x
            push_y = player_y - near_y
            dist_sq = push_x * push_x + push_y * push_y
            if dist_sq < R * R:
                if dist_sq == 0:
                    player_y = wall.top - R  # редкий случай: центр внутри стены
                else:
                    dist = dist_sq**0.5
                    player_x = near_x + push_x / dist * R
                    player_y = near_y + push_y / dist * R

        # ПОДАЧА СУНДУКА: подобрал - очко, бонус времени, патроны, респавн
        chest_dx = player_x - chest_x
        chest_dy = player_y - chest_y
        if chest_dx * chest_dx + chest_dy * chest_dy < (R + 30) * (R + 30):
            score += 1
            # бонус времени: от 1 секунды в начале раунда до 3 секунд под конец -
            # чем меньше времени осталось, тем больше прибавка
            time_bonus = 1 + 2 * (1 - time_left / GAME_TIMER)
            time_left += time_bonus
            # каждый сундук даёт случайно от 1 до 3 патронов
            ammo += rng.randint(1, 3)
            # РЕМОНТ ЛАБИРИНТА: каждый разбитый блок возвращается ровно на
            # своё место металлическим, не разрушаемым
            metal_walls.extend(holes)
            holes = []  # все бреши залиты
            chest_cell = random_cell(rng, not_cell=player_cell(player_x, player_y))
            chest_x, chest_y = cell_center(chest_cell)

        # ПУЛИ: летят по направлению выстрела. Попадание в кусок лабиринта
        # выбивает дыру 90x90 (диаметр солдата 66 - проходит свободно).
        # Первые 4 стены в списке - границы арены, они неразрушимы: пуля
        # просто исчезает. А ещё пулей можно РАЗБИТЬ СУНДУК, без очков
        for bullet in bullets:
            bullet[0] += bullet[2] * BULLET_SPEED
            bullet[1] += bullet[3] * BULLET_SPEED
        alive_bullets = []
        for bullet in bullets:
            bx, by = bullet[0], bullet[1]
            bullet_rect = pg.Rect(bx - 4, by - 4, 8, 8)
            dead = (
                bullet_rect.right < 0
                or bullet_rect.left > screen.get_width()
                or bullet_rect.bottom < 0
                or bullet_rect.top > screen.get_height()
            )
            if not dead:
                for i, wall in enumerate(walls):
                    if bullet_rect.colliderect(wall):
                        dead = True
                        if i >= 4:
                            holes.append(wall)
                            walls.pop(i)
                        break
            if not dead:
                # металлические блоки пулей НЕ пробиваются
                for wall in metal_walls:
                    if bullet_rect.colliderect(wall):
                        dead = True
                        break
            if not dead:
                # разбить сундук пулей
                chest_rect = pg.Rect(chest_x - 30, chest_y - 18, 60, 44)
                if chest_rect.colliderect(bullet_rect):
                    dead = True
                    chest_cell = random_cell(
                        rng, not_cell=player_cell(player_x, player_y)
                    )
                    chest_x, chest_y = cell_center(chest_cell)
            if not dead:
                alive_bullets.append(bullet)
        bullets = alive_bullets

        # Интерфейс: патроны в левом углу, очки и время - в правом (время под очками)
        ammo_surf = font.render(f"Патроны: {ammo}", True, (150, 60, 20))
        score_surf = font.render(f"Очки: {score}", True, (40, 60, 120))
        timer_surf = font.render(f"Время: {seconds_left}", True, (120, 40, 40))
        screen.blit(ammo_surf, (50, 40))
        screen.blit(score_surf, (screen.get_width() - score_surf.get_width() - 50, 40))
        screen.blit(timer_surf, (screen.get_width() - timer_surf.get_width() - 50, 115))

        pg.display.flip()
        clock.tick(60)  # 60 кадров в секунду


if __name__ == "__main__":
    main()

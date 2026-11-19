import random

import pygame as pg

# все константы игры - цвета, размеры, таймеры - живут в settings.py
from settings import DB_FILE, FLOOR_COLOR, GAME_TIMER, R

# классы игры разложены по своим модулям
from ammo_box import AmmoBox
from maze import Maze, cell_center, random_cell
from results_db import ResultDB
from soldier import Soldier

# ПОДСКАЗКИ: (задержка появления, сколько секунд показывать, строки текста).
# Строки короткие нарочно: панель подсказок фиксированная (500x160),
# и весь текст должен влезать в неё без переноса.
HINT_STEPS = [
    (0, 9, ["Соберите Ящик с патронами"]),
    (9, 5, ["Для выстрела из пистолета", "нажмите ПРОБЕЛ"]),
    (
        14,
        9,
        [
            "Разрушай блоки стен ВЫСТРЕЛОМ.",
            "После подбора Ящика",
            "пробоина зальётся Металлом.",
        ],
    ),
    (
        23,
        9,
        [
            "Металл разрушается от ДВУХ",
            "выстрелов и не восстанавливается.",
        ],
    ),
    (
        32,
        7,
        [
            "За каждый Ящик с патронами",
            "выполучаете: прибавка к скорости,",
            "несколько Патронов и чуть-чуть Времени",
        ],
    ),
    (39, 5, ["Соберите как можно больше", "Ящиков до истечения времени"]),
]
HINTS_TOTAL = 44  # суммарное время показа подсказок (потом блок исчезает)


def main():
    pg.init()

    screen = pg.display.set_mode((1080, 1200))
    rng = random.Random()
    clock = pg.time.Clock()
    font = pg.font.Font(None, 56)
    small_font = pg.font.Font(None, 40)  # для блока подсказок
    big_font = pg.font.Font(None, 96)

    db = ResultDB(DB_FILE)  # логи результатов в SQLite
    maze = Maze(rng)  # границы + лабиринт из блоков
    ammo_box = AmmoBox(random_cell(rng, not_cell=(0, 0)))
    soldier = Soldier(
        *cell_center((0, 0))
    )  # солдат появляется в верхнем левом углу, смотрит вправо
    bullets = []  # летящие пули

    # ВВОД НИКНЕЙМА: первый экран игры, Enter - начать раунд
    entering_nickname = True
    nickname = ""
    result_top = None  # топ-5 игроков из БД, появляется на экране результата
    game_over = False
    last_ticks = pg.time.get_ticks()
    time_left = float(GAME_TIMER)  # таймер хранит дробные секунды
    elapsed_game = 0.0  # сколько секунд игры прошло (для расписания подсказок)

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

            # РЕСТАРТ: на финальном экране Enter - сыграть ещё раз.
            # Новый лабиринт, новый ящик, солдат - в левый верхний угол.
            if game_over and event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                maze = Maze(rng)
                soldier = Soldier(*cell_center((0, 0)))
                ammo_box = AmmoBox(random_cell(rng, not_cell=soldier.cell()))
                bullets = []
                time_left = float(GAME_TIMER)
                elapsed_game = 0.0  # подсказки начинаются заново
                last_ticks = pg.time.get_ticks()
                game_over = False
                entering_nickname = True

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

            # ВЫСТРЕЛ: одиночный пробел, тратит патрон, пуля летит по направлению взгляда
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                bullet = soldier.shoot()
                if bullet:
                    bullets.append(bullet)

            # ОДИНОЧНЫЕ нажатия стрелок (без диагоналей)
            if event.type == pg.KEYDOWN:
                soldier.handle_tap(event, keys)

        # ЭКРАН ВВОДА НИКА и Таймер:
        if entering_nickname:
            screen.fill((30, 30, 50))
            t1 = font.render("Введи Имя игрока и нажми Enter:", True, (230, 230, 230))
            t2 = big_font.render(nickname + "_", True, (240, 220, 120))
            center_x = screen.get_width() // 2
            screen.blit(t1, (center_x - t1.get_width() // 2, 420))
            screen.blit(t2, (center_x - t2.get_width() // 2, 520))
            pg.display.flip()
            clock.tick(60)
            continue

        # ТАЙМЕР: 60 секунд, отсчет идет дробями
        now = pg.time.get_ticks()
        dt = (now - last_ticks) / 1000
        time_left -= dt
        elapsed_game += dt  # игровое время для подсказок
        last_ticks = now
        seconds_left = max(0, int(time_left))
        if time_left <= 0 and not game_over:
            # конец раунда: результат уходит в БД, появляется топ-5
            game_over = True
            result_top = db.save(nickname, soldier.score)

        if game_over:
            # ЭКРАН РЕЗУЛЬТАТА: очки игрока + топ-5 из БД
            screen.fill((40, 40, 60))
            t1 = big_font.render(f"ОЧКИ: {soldier.score}", True, (240, 220, 120))
            t2 = font.render("ESC - выход", True, (180, 180, 180))
            t5 = font.render("Enter - сыграть ещё раз", True, (120, 220, 120))
            center_x = screen.get_width() // 2
            screen.blit(t1, (center_x - t1.get_width() // 2, 200))
            t4 = font.render("ТОП-5 ИГРОКОВ:", True, (120, 220, 120))
            screen.blit(t4, (center_x - t4.get_width() // 2, 400))
            for i, (top_nick, top_score) in enumerate(result_top or [], 1):
                # свой результат подсвечивается золотым
                color = (240, 220, 120) if top_nick == nickname else (200, 200, 200)
                row = font.render(f"{i}. {top_nick} - {top_score}", True, color)
                screen.blit(row, (center_x - 150, 417 + i * 60))
            screen.blit(t5, (center_x - t5.get_width() // 2, 920))
            screen.blit(t2, (center_x - t2.get_width() // 2, 980))
            pg.display.flip()
            clock.tick(60)
            continue

        screen.fill(FLOOR_COLOR)

        maze.draw(screen)

        ammo_box.draw(screen)

        soldier.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        soldier.tick(keys)

        # ЖЁСТКАЯ КОЛЛИЗИЯ: круг выталкивается из каждого блока
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

        # ПОДАЧА ЯЩИКА: подобрал - очко, бонус времени, патроны,
        # лабиринт восстанавливается (с металл. стенами), ящик перепоявляется
        box_dx = soldier.x - ammo_box.x
        box_dy = soldier.y - ammo_box.y
        if box_dx * box_dx + box_dy * box_dy < (R + 30) * (R + 30):
            soldier.score += 1
            # чем меньше времени у игрока осталось - тем больше прибавка
            time_bonus = 1 + 2 * (1 - time_left / GAME_TIMER)
            time_left += time_bonus
            soldier.gain_ammo()
            soldier.speed_boost()
            maze.repair()
            ammo_box.move_to_random(rng, not_cell=soldier.cell())

        # Кусок лабиринта разбивается
        # с одного выстрела и уходит в бреши (при подборе ящика вернётся
        # металлом). Металл держит два выстрела: первый - трещины, второй -
        # блок исчезает НАВСЕГД. Границы лабиринта неразрушимы
        # Пулей можно разбить и ящик - она переродится,
        # но очков и бонусов за разбитый ящик нет.
        for bullet in bullets:
            bullet.update()
        alive_bullets = []
        for bullet in bullets:
            if bullet.off_screen(screen.get_width(), screen.get_height()):
                continue  # улетела за экран
            if maze.handle_bullet(bullet):
                continue  # погасилась о стену
            if ammo_box.rect.colliderect(bullet.rect):
                # разбил ящик: она перерождается, но без очков
                ammo_box.move_to_random(rng, not_cell=soldier.cell())
                continue
            alive_bullets.append(bullet)
        bullets = alive_bullets

        # Фиксированный блок 500x160 по центру верхней кромки
        # (влезает в свободное место между Патронами и Очками), показывает
        # правила по расписанию HINT_STEPS
        hint_lines = None
        for start, show_secs, lines in HINT_STEPS:
            if start <= elapsed_game < start + show_secs:
                hint_lines = lines
                break
        if hint_lines:
            panel_w, panel_h = 500, 160
            panel = pg.Surface((panel_w, panel_h), pg.SRCALPHA)
            panel.fill((0, 0, 0, 150))
            panel_x = screen.get_width() // 2 - panel_w // 2
            screen.blit(panel, (panel_x, 38))
            line_h = small_font.get_linesize()
            hint_y = 38 + (panel_h - len(hint_lines) * line_h) / 2
            for line in hint_lines:
                s = small_font.render(line, True, (255, 255, 255))
                screen.blit(s, (screen.get_width() // 2 - s.get_width() // 2, hint_y))
                hint_y += line_h

        # Интерфейс: патроны, очки и время
        ammo_surf = font.render(f"Патроны: {soldier.ammo}", True, (150, 60, 40))
        score_surf = font.render(f"Очки: {soldier.score}", True, (40, 60, 120))
        timer_surf = font.render(f"Время: {seconds_left}", True, (160, 40, 20))
        screen.blit(ammo_surf, (50, 40))
        screen.blit(score_surf, (screen.get_width() - score_surf.get_width() - 50, 40))
        screen.blit(timer_surf, (screen.get_width() - timer_surf.get_width() - 50, 100))

        pg.display.flip()
        clock.tick(60)  # 60 кадров в секунду


if __name__ == "__main__":
    main()

import pygame as pg


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
    if direction == "right":
        return (player_x + dx, player_y + dy, w, h)
    if direction == "left":
        return (player_x - dx - w, player_y + dy, w, h)
    if direction == "up":
        return (player_x + dy, player_y - dx - w, h, w)
    return (player_x + dy, player_y + dx, h, w)


def eye_center(player_x, player_y, direction, dx, dy):
    """Центр круглой детали (глаз) для текущего направления."""
    if direction == "right":
        return (player_x + dx, player_y + dy)
    if direction == "left":
        return (player_x - dx, player_y + dy)
    if direction == "up":
        return (player_x + dy, player_y - dx)
    return (player_x + dy, player_y + dx)


def main():
    pg.init()

    screen = pg.display.set_mode((1080, 1080))

    player_x, player_y = 300, 300
    direction = "right"  # "right", "left", "up", "down"

    clock = pg.time.Clock()
    while True:
        screen.fill((220, 220, 220))

        # СТЕНЫ-ГРАНИЦЫ
        left_wall = pg.draw.rect(screen, (170, 120, 70), (35, 35, 8, 1010))
        top_wall = pg.draw.rect(screen, (170, 120, 70), (35, 35, 1010, 8))
        bottom_wall = pg.draw.rect(screen, (170, 120, 70), (35, 1037, 1010, 8))
        right_wall = pg.draw.rect(screen, (170, 120, 70), (1037, 35, 8, 1010))

        # СОЛДАТ (тёмно-зелёный)
        pg.draw.circle(screen, (60, 130, 60), (player_x, player_y), 50)

        # ПРИЧЁСКА: 5 прядей, каждая вылезает за круг на 12 пикселей.
        # Собираем детали в позе «вправо», раскладывает directed().
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

        # ГЛАЗ, БРОВЬ, ПИСТОЛЕТ «Г» (ствол + рукоять с общим углом)
        pg.draw.circle(
            screen, (20, 20, 20), eye_center(player_x, player_y, direction, 20, -15), 6
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

        # Управление ЗАЖАТЫМИ клавишами
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            player_x -= 3
            direction = "left"
        if keys[pg.K_RIGHT]:
            player_x += 3
            direction = "right"
        if keys[pg.K_UP]:
            player_y -= 3
            direction = "up"
        if keys[pg.K_DOWN]:
            player_y += 3
            direction = "down"

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return  # выход из main()

            # Управление НАЖАТИЕМ клавиш
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    player_x -= 3
                    direction = "left"
                if event.key == pg.K_RIGHT:
                    player_x += 3
                    direction = "right"
                if event.key == pg.K_UP:
                    player_y -= 3
                    direction = "up"
                if event.key == pg.K_DOWN:
                    player_y += 3
                    direction = "down"

        # ЖЁСТКАЯ КОЛЛИЗИЯ со стенами: центр круга держится на расстоянии
        # >= 50 (радиус) от внутренней стороны каждой стены.
        if player_x < left_wall.right + 50:
            player_x = left_wall.right + 50
        if player_x > right_wall.left - 50:
            player_x = right_wall.left - 50
        if player_y < top_wall.bottom + 50:
            player_y = top_wall.bottom + 50
        if player_y > bottom_wall.top - 50:
            player_y = bottom_wall.top - 50

        pg.display.flip()  # показать нарисованный кадр на экране
        clock.tick(60)  # не быстрее 60 кадров в секунду


if __name__ == "__main__":
    main()

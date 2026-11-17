import pygame as pg


def main():
    pg.init()

    screen = pg.display.set_mode((1080, 1080))
    # прямоугольник: (x левого верхнего угла, y, ширина, высота)

    player_x, player_y = 300, 300
    facing = 1

    clock = pg.time.Clock()
    while True:
        screen.fill((220, 220, 220))

        # СТЕНЫ-ГРАНИЦЫ
        left_wall = pg.draw.rect(
            screen, (170, 120, 70), (35, 35, 8, 1010)
        )  # x, y, ширина, высота
        top_wall = pg.draw.rect(screen, (170, 120, 70), (35, 35, 1010, 8))
        bottom_wall = pg.draw.rect(screen, (170, 120, 70), (35, 1037, 1010, 8))
        right_wall = pg.draw.rect(screen, (170, 120, 70), (1037, 35, 8, 1010))

        # СОЛДАТ: лицо и пистолет зеркалятся по facing (1 = вправо, -1 = влево)
        pg.draw.circle(screen, (60, 130, 60), (player_x, player_y), 50)  # тёмно-зелёный

        # ПРИЧЁСКА
        for i in range(5):
            hair_dy = -46 + i * 6
            back_edge = -((2500 - hair_dy * hair_dy) ** 0.5)  # задний край круга
            strand_from = back_edge - 12
            strand_to = 5 - i * 4
            hair_w = strand_to - strand_from
            hair_center = (strand_from + strand_to) / 2
            pg.draw.rect(
                screen,
                (20, 20, 20),
                (
                    player_x + facing * hair_center - hair_w / 2,
                    player_y + hair_dy,
                    hair_w,
                    3,
                ),
            )

        pg.draw.circle(
            screen, (20, 20, 20), (player_x + facing * 20, player_y - 15), 6
        )  # глаз
        brow_dx, brow_w = 3, 35
        pg.draw.rect(
            screen,
            (20, 20, 20),
            (
                player_x + facing * (brow_dx + brow_w / 2) - brow_w / 2,
                player_y - 30,
                brow_w,
                6,
            ),
        )  # бровь
        gun_dx, gun_w = 35, 45
        pg.draw.rect(
            screen,
            (60, 60, 70),
            (
                player_x + facing * (gun_dx + gun_w / 2) - gun_w / 2,
                player_y - 10,
                gun_w,
                20,
            ),
        )  # ствол
        hilt_dx, hilt_w = 35, 17
        pg.draw.rect(
            screen,
            (60, 60, 70),
            (
                player_x + facing * (hilt_dx + hilt_w / 2) - hilt_w / 2,
                player_y - 10,
                hilt_w,
                32,
            ),
        )  # рукоять

        # Управление ЗАЖАТЫМИ клавишами
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            player_x -= 3
            facing = -1  # едем влево - смотрим влево
        if keys[pg.K_RIGHT]:
            player_x += 3
            facing = 1  # едем вправо - смотрим вправо
        if keys[pg.K_UP]:
            player_y -= 3
        if keys[pg.K_DOWN]:
            player_y += 3

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return  # выход из main()

            # Управление НАЖАТИЕМ клавиш
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    player_x -= 3
                    facing = -1
                if event.key == pg.K_RIGHT:
                    player_x += 3
                    facing = 1
                if event.key == pg.K_UP:
                    player_y -= 3
                if event.key == pg.K_DOWN:
                    player_y += 3

        pg.display.flip()  # показать нарисованный кадр на экране
        clock.tick(60)  # не быстрее 60 кадров в секунду


if __name__ == "__main__":
    main()

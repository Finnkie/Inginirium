#!/usr/bin/env python3

# python3 ../../log/generate_log.py --lines 1100000 --seed 42

import os
import shlex
from collections import Counter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(
    BASE_DIR, "game_server.log"
)  # сэмпл на 1000 строк - им работаем на уроке
FULL_LOG = os.path.normpath(
    os.path.join(BASE_DIR, "..", "..", "log", "game_server_full.log")
)

MY_SERVER = "Алмаз[Мир]"  # у каждого детектива свой сервер


# ---------- ФИЛЬТРЫ: список строк -> список строк ----------


def parse_file(path):
    result = []
    for line in open(path, encoding="utf-8"):
        result.append(line.strip())
    return result


def contain_word(input_lines, word):
    result = []
    for line in input_lines:
        if word in line:
            result.append(line)
    return result


def not_contain_word(input_lines, word):
    result = []
    for line in input_lines:
        if word not in line:
            result.append(line)
    return result


def contain_list_of_words(input_lines, words):
    result = []
    for line in input_lines:
        for word in words:
            if word in line:
                result.append(line)
    return result


# ---------- РАЗБОР ОДНОЙ СТРОКИ ----------


def words(line):
    """Разрезать строку по символу ' - '
    0 — дата, 1 — сервер, 2 - локация, 3 — Игрок
    4 — Действие, 5 - Цель (если есть), 6 — Сообщение (если есть)
    """
    return line.split(" - ")


# Таким образом, если нам нужно достать Дейсвтие, пишем:
# action = words(line)[4]


def nickname(line):
    # Ник игрока — слово с номером 3 (считаем с нуля!). Вместе со скобками: <ДобрыйЖук>.
    return words(line)[3]


def target(line):
    return words(line)[5]


def action(line):
    # Действие игрока — слово с номером 9. Кавычки снимаем: "сказал" -> сказал.
    return words(line)[4].strip('"')


# ---------- ПОДСЧЁТЫ ----------


def top_players(input_lines, top_of_how_many):
    # Наибольшее кол-во упоминаний игрока
    counter = Counter()
    for line in input_lines:
        counter[nickname(line)] += 1
    return counter.most_common(top_of_how_many)


def top_targets(input_lines, top_of_how_many):
    # Наибольшее кол-во упоминаний игрока
    counter = Counter()
    for line in input_lines:
        counter[target(line)] += 1
    return counter.most_common(top_of_how_many)


def show(input_lines, limit=10):
    """Показать, что осталось после фильтров — как вывод команды в терминале."""
    for line in input_lines[:limit]:
        print("  " + line)
    print(f"Всего строк на входе (в input): {len(input_lines)}")


def plural(count):
    """По-русски: 1 раз, 2 раза, 3 раза (правильно для чисел от 1 до 4)."""
    if count == 1:
        return "раз"
    return "раза"

#!/usr/bin/env python3

# python3 ../../log/generate_log.py --lines 1100000 --seed 42

import os
from collections import Counter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(
    BASE_DIR, "game_server.log"
)  # сэмпл на 1000 строк - им работаем на уроке
FULL_LOG = os.path.normpath(
    os.path.join(BASE_DIR, "..", "..", "log", "game_server_full.log")
)

MY_SERVER = "Тест[Мир]"  # у каждого детектива свой сервер
# Рил[Мир]    Детектив#1
# Голд[Мир]   Детектив#2
# Просто[Мир] Детектив#3
# Алмаз[Мир]  Детектив#4
# Добро[Мир]  Детектив#5
# Игро[Мир]   Детектив#6
# Пират[Мир]  Детектив#7
# Магия[Мир]  Детектив#8


# ---------- РАЗБОТА СО СТРОКОЙ ----------
# Строчка из Лога:
# [09/May/2026:00:14:24 +0300] - Голд[Мир] - Ладоград(город) - <xX_ЖелезныйЧеловек_Xx> - "написал_в_лс" - <Тор_Тугодум> - "пригласи в группу, я танк"


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

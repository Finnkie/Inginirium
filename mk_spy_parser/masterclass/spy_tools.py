#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Детектив «Найди шпиона» — версия на фильтрах, как в терминале Linux.

Мы делаем ровно то же, что делали бы руками в терминале:

    cat game_server.log | egrep "сказал" | egrep "золот"

Только вместо команд терминала — такие же простые функции Python.
Каждая функция берёт список строк и возвращает список строк,
поэтому их можно соединять в цепочку — как команды через |.

    cat(ЛОГ)                 все строки файла            = cat
    egrep(строки, "слово")   оставить строки со словом   = egrep -F "слово"
    egrep_v(строки, "слово") убрать строки со словом     = egrep -v "слово"
    words(строка)            разрезать строку на слова   = tr ' ' '\\n'
    nick(строка)             достать ник игрока
    action(строка)           достать действие игрока
    in_quotes(строка)        достать цель и сообщение (умный split — shlex)
    top(строки, N)           топ игроков по числу строк  = sort | uniq -c | sort -rn | head

Примечание для ведущего: в настоящем egrep квадратные скобки — спецсимволы,
поэтому egrep "Голд[Мир]" в терминале сработал бы хитро. Наш «egrep» ищет
подстроку как есть — это эквивалент egrep -F "Голд[Мир]".
"""

import shlex
from collections import Counter


LOG = "game_server.log"  # большой лог для финала: "game_server_full.log"
MY_SERVER = "Голд[Мир]"  # у каждого ученика свой сервер и свой злодей


# ---------- ФИЛЬТРЫ: список строк -> список строк ----------


def read_file(path):
    """cat файл — прочитать лог целиком и вернуть список строк."""
    result = []
    for line in open(path, encoding="utf-8"):
        result.append(line.strip())
    return result


def contain_word(lines, word):
    """egrep "слово" — оставить только строки, где это слово есть."""
    result = []
    for line in lines:
        if word in line:
            result.append(line)
    return result


def not_contain_word(lines, word):
    """egrep -v "слово" — наоборот: убрать строки, где слово есть."""
    result = []
    for line in lines:
        if word not in line:
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


def nick(line):
    # Ник игрока — слово с номером 3 (считаем с нуля!). Вместе со скобками: <ДобрыйЖук>.
    return words(line)[3]


def action(line):
    # Действие игрока — слово с номером 9. Кавычки снимаем: "сказал" -> сказал.
    return words(line)[4].strip('"')


"""
def in_quotes(line):
    # Достать из строки цель и сообщение (всё, что после действия).
    # shlex.split — «умный split» из библиотеки shlex:
    # понимает кавычки и сам убирает их.
    tail = " ".join(words(line)[10:])
    return shlex.split(tail)
"""


# ---------- ПОДСЧЁТЫ ----------


def top(lines, how_many):
    """Кто сколько раз попался в строках: топ-N игроков.

    Как: ... | sort | uniq -c | sort -rn | head -N
    Counter — счётчик из библиотеки collections: сам всё считает.
    """
    counter = Counter()
    for line in lines:
        counter[nick(line)] += 1
    return counter.most_common(how_many)


def dance_then_love(lines):
    """Найти ДВЕ строки подряд: станцевал и тут же признался_в_любви
    (и оба раза — один и тот же игрок)."""
    found = []
    for i in range(len(lines) - 1):
        this_line = lines[i]
        next_line = lines[i + 1]
        if (
            action(this_line) == "станцевал"
            and action(next_line) == "признался_в_любви"
            and nick(this_line) == nick(next_line)
        ):
            found.append(this_line)
            found.append(next_line)
    return found


def show(lines, limit=10):
    """Показать, что осталось после фильтров — как вывод команды в терминале."""
    for line in lines[:limit]:
        print("  " + line)
    print(f"Всего строк в файле: {len(lines)}")


def plural(count):
    """По-русски: 1 раз, 2 раза, 3 раза (правильно для чисел от 1 до 4)."""
    if count == 1:
        return "раз"
    return "раза"

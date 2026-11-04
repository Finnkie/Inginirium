from spy_tools import (
    read_file,
    nick,
    action,
    contain_word,
    not_contain_word,
    words,
    top,
    plural,
    show,
)
from spy_tools import LOG, MY_SERVER

# ---------- САМО РАССЛЕДОВАНИЕ ----------

"""
def main():
    all_lines = read_file(LOG)
    print(f"cat {LOG}: в логе {len(all_lines)} строк. Глазами столько не прочитать!\n")

    # ШАГ 0. Фильтр сервера: у каждого ученика свой сервер и свой злодей.
    # Работаем дальше только со строками СВОЕГО сервера.
    print("=== Шаг 0. Учимся фильтровать ===")
    lines = contain_word(all_lines, MY_SERVER)
    show(lines, f'cat {LOG} | egrep "{MY_SERVER}"', limit=5)
    print()

    # РАЗМИНКА 1. Кто больше всех танцует?
    print("=== Разминка 1. Кто больше всех станцевал? ===")
    dances = contain_word(lines, "станцевал")
    print(
        f'$ cat {LOG} | egrep "{MY_SERVER}" | egrep "станцевал" | sort | uniq -c | sort -rn | head -3'
    )
    for player, count in top(dances, 3):
        print(f"  {player} — станцевал {count} {plural(count)}")

    # РАЗМИНКА 2. Потанцевал и сразу признался в любви
    print("\n=== Разминка 2. Станцевал и СРАЗУ признался в любви? ===")
    for line in dance_then_love(lines):
        print("  " + line)

    # ШАГ 1. Кто ВСЛУХ говорит про золото
    print("\n=== Шаг 1. Кто вслух говорит про золото? ===")
    shouts = contain_word(lines, "сказал")  # пока только то, что сказано вслух
    shouts = contain_word(shouts, "золот")  # и среди этого — всё про золото
    show(
        shouts,
        f'cat {LOG} | egrep "{MY_SERVER}" | egrep "сказал" | egrep "золот"',
        limit=8,
    )
    print("\nТоп-5 болтунов про золото (подозреваемые):")
    suspects = top(shouts, 5)
    print(suspects)
    # for player, count in suspects:
    #    print(f"  {player}: {count} {plural(count)}")

    # ШАГ 2. Проверка подозреваемых: настоящему продавцу пишут в ЛС
    # и с ним делают обмен. Клянчащему игроку — не пишут и не меняются!
    print("\n=== Шаг 2. Настоящему шпиону пишут в ЛС и делают с ним обмен ===")
    private = contain_word(lines, "написал_в_лс")
    trades = contain_word(lines, "обмен")
    spy = ""
    best_score = 0
    for player, _times in suspects:
        letters = []  # письма ЕМУ: он стоит в поле цели
        for line in private:
            if words(line)[10] == player:
                letters.append(line)
        deals = contain_word(trades, player)  # он сам меняет ИЛИ с ним меняются
        score = len(letters) + len(deals)
        print(
            f"  {player}: писем ему {len(letters)}, обменов {len(deals)} -> очки: {score}"
        )
        if score > best_score:
            spy = player
            best_score = score

    # ШАГ 3. Разоблачение: достаём из лога ВСЕ строки шпиона разом
    print(f"\n=== Шаг 3. Разоблачение! Шпион: {spy} ===")
    evidence = contain_word(lines, spy)
    show(evidence, f'cat {LOG} | egrep "{MY_SERVER}" | egrep "{spy}"', limit=10)

    # ОТЧЁТ: сервер шпиона, кто ему писал и куда он звал платить
    print("\n=== ОТЧЁТ КОНТРРАЗВЕДКИ ===")
    server = words(evidence[0])[4]
    buyer = ""
    site = ""
    for line in evidence:
        if action(line) == "написал_в_лс" and nick(line) == spy:
            parts = in_quotes(line)
            buyer = parts[0]  # кому он ответил — тот и покупатель
            message = parts[1]
            if ".рф" in message:
                site = message.split(",")[0]  # адрес сайта — до первой запятой
    print(f"  Шпион:      {spy} (сервер {server})")
    print(f"  Покупатель: {buyer}")
    print(f"  Сайт:       {site}")
"""


def main():
    print("Привет!")
    print(f"Печатаю содержание {LOG}...\n\n")
    file = read_file(LOG)
    show(file, limit=10)
    # most_active_player = top(file)
    player_1 = nick(file[0])
    print(player_1)
    print(action(file[0]))
    top


if __name__ == "__main__":
    main()

# ---------- ПОПРОБУЙ САМ (домашние задания) ----------
# 1. Вывести другой сервер (начни с cat(LOG)):  egrep(cat(LOG), "Просто[Мир]")
# 2. Кто кого ударил, кроме монстров:           egrep_v(egrep(lines, "ударил"), "<вепрь>")
# 3. Кто чаще всех признаётся в любви:          top(egrep(lines, "признался_в_любви"), 3)

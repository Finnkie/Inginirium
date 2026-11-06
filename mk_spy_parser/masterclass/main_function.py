from spy_tools import (
    parse_file,
    nickname,
    action,
    contain_word,
    contain_list_of_words,
    not_contain_word,
    words,
    target,
    top_players,
    top_targets,
    show,
)
from spy_tools import LOG, FULL_LOG, MY_SERVER

# ---------- САМО РАССЛЕДОВАНИЕ ----------


def main():
    print("Привет!")
    full_log_file = parse_file(FULL_LOG)
    my_server = contain_word(full_log_file, MY_SERVER)
    #  ПУНКТ 1
    capitals_lines = contain_word(my_server, "столица")
    cities_lines = contain_word(my_server, "город")
    list_capitals_cities = capitals_lines + cities_lines

    show(list_capitals_cities, limit=50)
    gold_words = ["голда", "золот", "злато", "деньг", "прод"]
    gold_speakers = contain_list_of_words(
        contain_word(list_capitals_cities, "сказал"), gold_words
    )
    show(gold_speakers, limit=50)

    #  ПУНКТ 2 Вывод - Продавец шифруется. Сложный случай.

    print("\n\n\n")

    trade_actions = contain_word(list_capitals_cities, "обмен")
    top_10_traders = top_players(trade_actions, 10)
    result_traders = "\n".join(str(item) for item in top_10_traders)
    print(f"\nСтатистика по топ 10 обменивающихся игроков:\n{result_traders}")

    print("\n\n\n")

    ls_actions = contain_word(list_capitals_cities, "написал_в_лс")
    top_10_ls_targets = top_targets(ls_actions, 10)
    result_ls_players = "\n".join(str(item) for item in top_10_ls_targets)
    print(f"\nСтатистика по топ 10 игроков-адресатов сообщений:\n{result_ls_players}")

    PT = contain_word(ls_actions, "СерёгаСпекулянт")
    print(PT)
    PT_parsed = []
    for line in PT:
        if target(line) == "<СерёгаСпекулянт>":
            PT_parsed.append(line)
    show(PT_parsed, limit=4500)


if __name__ == "__main__":
    main()

# ---------- ПОПРОБУЙ САМ (домашние задания) ----------
# 1. Вывести другой сервер (начни с cat(LOG)):  egrep(cat(LOG), "Просто[Мир]")
# 2. Кто кого ударил, кроме монстров:           egrep_v(egrep(lines, "ударил"), "<вепрь>")
# 3. Кто чаще всех признаётся в любви:          top(egrep(lines, "признался_в_любви"), 3)

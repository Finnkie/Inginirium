# Импорты
from mk_spy_parser.masterclass.spy_tools import (
    LOG,
    FULL_LOG,
    MY_SERVER,
    parse_file,
    contain_word,
    contain_list_of_words,
    show,
    top_players,
    top_targets,
)


def main():
    print("Привет!")
    log_file = parse_file(FULL_LOG)
    my_server_lines = contain_word(log_file, MY_SERVER)
    # show(my_server_lines, limit=10)
    cities_and_capitals = ["(столица)", "(город)"]
    c_and_cap = contain_list_of_words(my_server_lines, cities_and_capitals)
    # show(c_and_cap, limit=50)
    words_of_bad_guy_trader = ["золот", "голд", "прод"]
    spy_words = contain_list_of_words(c_and_cap, words_of_bad_guy_trader)
    show(spy_words, limit=100)

    traders = contain_word(c_and_cap, "обмен")
    top_10_traders = top_players(traders, 10)
    print("\nТоп 10 игроков по обмену:")
    for trader, number in top_10_traders:
        print(f"{trader}: {number}")

    speakers = contain_word(c_and_cap, "сказал")
    print("\nТоп 10 игроков по Сказал в общем чате:")
    top_10_speakers = top_players(speakers, 10)
    for speaker, number in top_10_speakers:
        print(f"{speaker}: {number}")

    ls_lines = contain_word(c_and_cap, "написал_в_лс")
    top_10_ls_targets = top_targets(ls_lines, 10)
    print("\nТоп 10 игроков по личным сообщениям")
    for ls_listener, number in top_10_ls_targets:
        print(f"{ls_listener}: {number}")

    say = contain_word(c_and_cap, "написал_в_лс")
    suspect = contain_word(say, "<Теневой")
    show(suspect, limit=40)


if __name__ == "__main__":
    main()

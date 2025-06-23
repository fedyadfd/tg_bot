import s_taper
from s_taper.consts import*
from telebot.types import Message

user_scheme = {
    "user_id":INT+KEY,
    "name":TEXT,
    "power":TEXT,
    "hp":INT,
    "dmg":INT,
    "lvl":INT,
    "exp":INT,
    "max_hp":INT,
    "win":INT,
    "money":INT
}
eat_sheme = {
    "user_id":INT+KEY,
    "eat":TEXT
}
eat = s_taper.Taper("eat","db_tg.db").create_table(eat_sheme)

users = s_taper.Taper("users","db_tg.db").create_table(user_scheme)


def is_new_player(msg:Message):
    result = users.read_all()
    for u in result:
        if u[0] == msg.chat.id:
            return False
    return True
















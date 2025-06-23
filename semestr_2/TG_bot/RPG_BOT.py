import asyncio
import random

import datetime

import text
import telebot
from telebot.types import (Message, InlineKeyboardButton as IB, CallbackQuery, InlineKeyboardMarkup as IKM,
                           ReplyKeyboardMarkup as RKM, ReplyKeyboardRemove as RKR)
from db_tg import *
from config import TOKEN
import fight

bot = telebot.TeleBot(TOKEN)
temp = {}
clear = RKR()
stats_player = {}


class Enemy:
    enemies = {
        "Робот-самый крутой": [40, 40, 30],
        "Робот-конкурент самого крутого робота": [35, 35, 25],
        "Робот-крутой": [30, 30, 20],
        "Робот-почти крутой": [29, 29, 19],
        "Робот-относительно крутой": [25, 25, 15],
        "Робот-почти относительно крутой": [24, 24, 14],
        "Робот-не очень крутой": [20, 20, 10],
        "Робот-так себе по опыту": [20, 20, 1],
        "Робот-не крутой": [10, 10, 5],
        "Робот-который не заслужил внимания": [5, 5, 2],
        "САМЫЙ СЛАБЫЙ РОБОТ": [1, 1, 0],
        "Очень обычно-средний прям среднячок,не имеющий никакого титула,который прям в середине общества роботов,"
        "который не имеет отличительных черт-робот": [20, 20, 20],
        "Волк": [5, 5, 3],
        "Мужик": [15, 20, 10],
        "Не очень живой мужик(зомби)": [10, 15, 5],
        "Робо-мужик": [20, 20, 15],
        "Скелет": [10, 10, 10],
        "Призрак": [25, 25, 30],
        "Призрак-мужика": [30, 30, 30],
        "Паразит": [5, 20, 2]
    }

    def __init__(self, level):
        self.name = random.choice(list(self.enemies))
        self.hp = self.enemies[self.name][0] + ((level - 1) * 10)
        self.damage = self.enemies[self.name][1] + ((level - 1) * 10)
        self.exp = self.enemies[self.name][2]


def delay(sec: int):
    asyncio.run(asyncio.sleep(sec))


def read_player(msg: Message):
    return users.read("user_id", msg.chat.id)


def write_player(player: list):
    users.write(player)


@bot.message_handler(["start"])
def start(msg: Message):
    if is_new_player(msg):
        temp[msg.chat.id] = {"name": None}
        reg_1(msg)
    else:
        menu(msg)


def reg_1(msg):
    bot.send_message(msg.chat.id, text.text % msg.from_user.first_name)
    bot.register_next_step_handler(msg, reg_2)


def reg_2(msg: Message):
    if not temp[msg.chat.id]["name"]:
        temp[msg.chat.id]["name"] = msg.text
        kb = RKM(True, True)
        kb.row("земля🌍", "вода💦")
        kb.row("огонь🔥", "воздух🌬️")
        bot.send_message(msg.chat.id, "выбери стихию:", reply_markup=kb)
        bot.register_next_step_handler(msg, reg_3)


def reg_3(msg: Message):
    if msg.text == "огонь🔥":
        temp[msg.chat.id]["name"] = None
        bot.send_message(msg.chat.id, "магия огня под запретом!выбирай другую магию!")
        reg_1(msg)
    else:
        temp[msg.chat.id]["power"] = msg.text
        hp, damage = fight.powers[msg.text]
        users.write([msg.chat.id, temp[msg.chat.id]["name"],
                     temp[msg.chat.id]["power"], hp, damage, 1, 0, hp, 0, 0])
        eat.write([msg.chat.id, {}])
        print("игрок успешно добавлен в базу данных!")
        bot.send_message(msg.chat.id, text.text_2)
        delay(2)
        menu(msg)


@bot.message_handler(["menu"])
def menu(msg: Message):
    bot.send_message(msg.chat.id, text.menu, reply_markup=clear)


@bot.message_handler(commands=["home"])
def home(msg: Message):
    kb = RKM(True, True)
    kb.row("отдохнуть", "перекусить")
    kb.row("Вернуться в меню")
    bot.send_message(msg.chat.id, text="Вы находитесь в лагере", reply_markup=kb)
    bot.register_next_step_handler(msg, home_handler, kb)


def home_handler(msg: Message, kb):
    if msg.text == "отдохнуть":
        sleep(msg)
    elif msg.text == "перекусить":
        eat_food(msg)
    elif msg.text == "Вернуться в меню":
        menu(msg)
    else:
        bot.send_message(msg.chat.id, text="Ты должен выбрать одну из кнопок", reply_markup=kb)
        bot.register_next_step_handler(msg, home_handler, kb)


@bot.message_handler(commands=["stats"])
def stats(msg: Message):
    player = read_player(msg)
    y = (f"Имя:{player[1]}\n"
         f"ID:{player[0]}\n"
         f"Стихия:{player[2]}\n"
         f"Здоровье❤️:{player[3]}\n"
         f"Уровень:{player[5]}\n"
         f"Урон:{player[4]}\n"
         f"Опыт:{player[6]}\n")
    _, food = eat.read("user_id", msg.chat.id)
    for j in food:
        y += f"{j}:{food[j][1]}\n"
    bot.send_message(msg.chat.id, y)
    menu(msg)


@bot.message_handler(commands=["square"])
def square(msg: Message):
    kb = RKM(True, True)
    kb.row("испытание ловкости", "пойти в бой")
    kb.row("Вернуться в меню")
    bot.send_message(msg.chat.id, text="Вы находитесь на тренировочной площадке.", reply_markup=kb)
    bot.register_next_step_handler(msg, square_handler, kb)


def square_handler(msg: Message, kb):
    if msg.text == "испытание ловкости":
        player = read_player(msg)
        if player[8] >= 2:
            bot.send_message(msg.chat.id, text="Ты больше не можешь участвовать в испытании.")
            delay(2)
            menu(msg)
        else:
            bot.send_message(msg.chat.id, text="Сейчас начнется твое испытание,тебе необходимо 5 раз подряд отразить "
                                               "атаку и успевать за 3 секунды.")
            delay(10)
            kb = RKM(True, True)
            kb.row("Выйти", "Нет спасибо")
            bot.send_message(msg.chat.id, text="Если ты случайно нажал кнопку ты можешь выйти.", reply_markup=kb)
            bot.register_next_step_handler(msg, dls, kb)
    elif msg.text == "пойти в бой":
        find_enemy(msg)
    elif msg.text == "Вернуться в меню":
        menu(msg)
    else:
        bot.send_message(msg.chat.id, text="Ты должен выбрать одну из кнопок", reply_markup=kb)
        bot.register_next_step_handler(msg, square_handler, kb)


def dls(msg: Message, kb):
    if msg.text == "Выйти":
        square(msg)
    elif msg.text == "Нет спасибо":
        block(msg)
    else:
        bot.send_message(msg.chat.id, text="Ты должен выбрать одну из кнопок", reply_markup=kb)
        bot.register_next_step_handler(msg, dls, kb)


def block(msg: Message):
    try:
        print(temp[msg.chat.id])
    except KeyError:
        temp[msg.chat.id] = {}
    try:
        print(temp[msg.chat.id]["win"])
    except KeyError:
        temp[msg.chat.id]["win"] = 0
    bot.send_message(msg.chat.id, text="Приготовься к атаке.", reply_markup=clear)
    delay(3)
    sides = ["Слева", "Справа", "Сверху", "Снизу"]
    random.shuffle(sides)
    kb = RKM(True, True)
    kb.row(sides[0], sides[3])
    kb.row(sides[1], sides[2])
    right = random.choice(sides)
    bot.send_message(msg.chat.id, text=f"Защищайся!Удар {right}", reply_markup=kb)
    temp[msg.chat.id]["block_start"] = datetime.datetime.now().timestamp()
    bot.register_next_step_handler(msg, block_handler, right)


def block_handler(msg: Message, right):
    temp[msg.chat.id]["block_finish"] = datetime.datetime.now().timestamp()
    if temp[msg.chat.id]["block_finish"] - temp[msg.chat.id]["block_start"] < 3 and right == msg.text:
        temp[msg.chat.id]["win"] += 1
        if temp[msg.chat.id]["win"] == 5:
            temp[msg.chat.id]["win"] = 0
            level_up(msg)
            bot.send_message(msg.chat.id, text="Испытание окончено.")
            player = read_player(msg)
            player[8] += 1
            write_player(player)
            delay(3)
            menu(msg)
        else:
            bot.send_message(msg.chat.id, text="Красавчик,молодец,лучший просто")
            delay(2)
            block(msg)
    else:
        temp[msg.chat.id]["win"] = 0
        bot.send_message(msg.chat.id, text="Ты не справился.")
        kb = RKM(True, True)
        kb.row("Да", "Нет")
        bot.send_message(msg.chat.id, text="Продолжить испытание?", reply_markup=kb)
        bot.register_next_step_handler(msg, block_handler_2)


def block_handler_2(msg: Message):
    if msg.text == "Нет":
        menu(msg)
    else:
        block(msg)


def level_up(msg: Message):
    player = read_player(msg)
    player[7] = round(player[7] * 1, 5)
    player[3] = player[7]
    player[4] = round(player[4] * 2)
    player[5] += 1
    write_player(player)
    bot.send_message(msg.chat.id, text="Твой уровень повышен,у тебя всё хорошо.")


@bot.message_handler(["add_heal"])
def heal(msg: Message):
    _, food = eat.read("user_id", msg.chat.id)
    food["мясо"] = [25, 15]
    food["вода"] = [15, 30]
    eat.write([msg.chat.id, food])
    bot.send_message(msg.chat.id, text="вам выдали еду")


def find_enemy(msg: Message):
    bot.send_message(msg.chat.id, text="Ты отправился в страшный лес поискать врагов.")
    delay(3)
    new_enemy(msg)


def new_enemy(msg: Message):
    player = read_player(msg)
    enemy = Enemy(player[5])
    print(enemy.__dict__)
    kb = RKM(True, True)
    kb.row("Узнать инфо. о враге")
    kb.row("Обойдусь")
    bot.send_message(msg.chat.id, text="Я могу предоставить тебе информацию за определенную плату.", reply_markup=kb)
    bot.register_next_step_handler(msg, info, enemy)


def info(msg: Message, enemy):
    if msg.text == "Узнать инфо. о враге":
        player = read_player(msg)
        if player[9] >= 5:
            player[9] -= 5
            write_player(player)
            bot.send_message(msg.chat.id, text=f"Вот информация:"
                                               f"имя:{enemy.name},"
                                               f"здоровье:{enemy.hp},"
                                               f"урон:{enemy.damage},"
                                               f"опыт:{enemy.exp}.")
        else:
            bot.send_message(msg.chat.id, text="Не обманывай тут не 5 монет!")
    elif msg.text == "Обойдусь":
        bot.send_message(msg.chat.id, text="Ну и ладно.")
    delay(2)
    bot.send_message(msg.chat.id, text="Враг обнаружил тебя.Убей его!", reply_markup=clear)
    delay(4)
    attack(msg, enemy)


def attack(msg: Message, enemy: Enemy):
    a = random.randint(1, 2)
    if a == 1:
        if hero_attack(msg, enemy):
            if enemy_attack(msg, enemy):
                attack(msg, enemy)
            else:
                defeat(msg, enemy)
        else:
            win(msg, enemy)
    else:
        if enemy_attack(msg, enemy):
            if hero_attack(msg, enemy):
                attack(msg, enemy)
            else:
                win(msg, enemy)
        else:
            defeat(msg, enemy)


def win(msg: Message, enemy: Enemy):
    delay(3)
    bot.send_message(msg.chat.id, text=f"Ты получишь {enemy.exp} опыта")
    player = read_player(msg)
    player[6] += enemy.exp
    write_player(player)
    max_exp = 100 * (2 ** (player[5] - 1))
    if player[6] >= max_exp:
        player[6] -= max_exp
        write_player(player)
        level_up(msg)
        player = read_player(msg)
        need_exp = 100 * (2 ** (player[5] - 1)) - player[6]
        bot.send_message(msg.chat.id, text=f"До следующего уровня {need_exp} опыта.")
    else:
        bot.send_message(msg.chat.id, text=f"У тебя {player[6]} опыта")
    delay(2)
    menu(msg)


def defeat(msg: Message, enemy: Enemy):
    delay(3)
    player = read_player(msg)
    bot.send_message(msg.chat.id, text=f"У тебя отберут {enemy.exp} опыта")
    player[3] = 1
    if player[5] != 1:
        if player[6] > enemy.exp:
            player[6] -= enemy.exp
        else:
            player[6] = 0
    else:
        bot.send_message(msg.chat.id, text="У тебя 1 уровень,поэтому твой опыт не снизится.")
    write_player(player)
    delay(2)
    menu(msg)


def hero_attack(msg: Message, enemy: Enemy):
    player = read_player(msg)
    chance = random.randint(1, 100)
    delay(2)
    if chance <= 50:
        enemy.hp -= player[4]
    elif chance in range(51, 81):
        bot.send_message(msg.chat.id, text="Ты промазал.")
    else:
        enemy.hp -= player[4] * 2
        bot.send_message(msg.chat.id, text="Ты нанес крит. урон")
    if enemy.hp <= 0:
        bot.send_message(msg.chat.id, text="Ты убил врага.Ты победил,молодец.")
        return False
    else:
        bot.send_message(msg.chat.id, text=f"У врага осталось {enemy.hp}❤️")
        return True


def enemy_attack(msg: Message, enemy: Enemy):
    player = read_player(msg)
    chance = random.randint(1, 100)
    delay(2)
    if chance <= 50:
        player[3] -= enemy.damage
    elif chance in range(51, 81):
        bot.send_message(msg.chat.id, text="Враг промазал.")
    else:
        player[3] -= enemy.damage * 2
        bot.send_message(msg.chat.id, text="Враг нанес крит. урон")
    write_player(player)
    if player[3] <= 0:
        bot.send_message(msg.chat.id, text="Враг победил.Тренируйся")
        return False
    else:
        bot.send_message(msg.chat.id, text=f"У тебя осталось {player[3]}❤️")
        return True


def eat_food(msg: Message):
    player = read_player(msg)
    if player[3] >= player[7]:
        bot.send_message(msg.chat.id, text="Ты наелся")
        menu(msg)
    else:
        kb = IKM()
        _, food = eat.read("user_id", msg.chat.id)
        if food == {}:
            bot.send_message(msg.chat.id, text="У тебя нет еды")
            menu(msg)
        else:
            for key in food:
                kb.row(IB(f"{key} востановливает {food[key][0]}❤️ -- {food[key][1]} шт.",
                          callback_data=f"food_{key}_{food[key][0]}"))
            bot.send_message(msg.chat.id, text="Что будешь есть?", reply_markup=kb)


def eating(msg: Message, key, hp):
    _, food = eat.read("user_id", msg.chat.id)
    player = read_player(msg)
    if food[key][1] == 1:
        del food[key]
    else:
        food[key][1] -= 1
    eat.write([msg.chat.id, food])
    player[3] += int(hp)
    if player[3] >= player[7]:
        player[3] = player[7]
    users.write(player)
    print("игрок поел")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(callback: CallbackQuery):
    print(callback.data)
    if callback.data.startswith("food_"):
        a = callback.data.split("_")
        print(a)
        eating(callback.message, a[1], a[2])
        player = read_player(callback.message)
        bot.answer_callback_query(callback.id, f"Ты пополнил хп,теперь у тебя {player[3]}❤️", True)
        if player[3] >= player[7]:
            bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, text="Ты наелся и спишь")
            menu(callback.message)
        else:
            kb = IKM()
            _, food = eat.read("user_id", callback.message.chat.id)
            if food == {}:
                bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text="У тебя нет еды")
                menu(callback.message)
            else:
                for key in food:
                    kb.row(IB(f"{key} востановливает {food[key][0]}❤️ -- {food[key][1]} шт.",
                              callback_data=f"food_{key}_{food[key][0]}"))
                bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=kb)
    if callback.data.startswith("sleep_"):
        a = callback.data.split("_")
        t = int(a[1]) * 3
        bot.send_message(callback.message.chat.id, text=f"Твой сон займет {t}секунд.")
        delay(t)
        sleeping(callback.message, a[1])
        bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, text="Ты поспал.Иди гуляй.")
        menu(callback.message)
    if callback.data == "menu":
        bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)
        menu(callback.message)


def sleep(msg: Message):
    player = read_player(msg)
    need = player[7] - player[3]
    if need > 0:
        kb = IKM()
        kb.row(IB(f"поспать+{need}❤️", callback_data=f"sleep_{need}"))
        kb.row(IB(f"Вернуться", callback_data="menu"))
        bot.send_message(msg.chat.id, text="выбери сколько будешь отдыхать", reply_markup=kb)
    else:
        bot.send_message(msg.chat.id, text="ты не хочешь спать", reply_markup=clear)
        menu(msg)


def sleeping(msg: Message, hp):
    player = read_player(msg)
    player[3] += int(hp)
    write_player(player)
    print("игрок поспал")


bot.infinity_polling()

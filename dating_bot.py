import telebot
from typing import List, Dict, Optional
from requests import get
from random import choice


bot = telebot.TeleBot("1639458965:AAFVpID6qe_qQjC6y8XyFsiL36X2WWi9GVY")


class Profile:
    def __init__(self, name: str,
                 age: Optional[int],
                 city: Optional[str],
                 about: Optional[str],
                 user_gender: Optional[str],
                 user_find_gender: Optional[str],
                 i_like: List[int],
                 like_me: List[int],
                 match: List[int]):
        self.name = name
        self.age = age
        self.city = city
        self.about = about
        self.user_gender = user_gender
        self.user_find_gender = user_find_gender
        self.i_like = i_like
        self.like_me = like_me
        self.match = match

limbo: Dict[int, Profile] = {}

fem_users: Dict[int, Profile] = {}
male_users: Dict[int, Profile] = {}



@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if user_id not in fem_users.keys() and \
            user_id not in male_users.keys() and \
            user_id not in limbo.keys():
        name = message.from_user.first_name
        limbo[user_id] = Profile(name, None, None, None, None, None, [], [], [])
        print(limbo.keys())
    bot.send_message(user_id, 'Привет, давай знакомиться! \n'
                         'тебя зовут ' + name + ', это я уже знаю;)\n'
                         'теперь расскажи, сколько тебе лет.')
    bot.register_next_step_handler(message, get_age)


@bot.message_handler(content_types=['text'])
def any_msg(message):
    user_id = message.chat.id
    if user_id in limbo.keys():
        if not limbo[user_id].age:
            get_age(message)
        elif not limbo[user_id].city:
            get_city(message)
        elif not limbo[user_id].user_gender:
            gender(message)
        elif not limbo[user_id].user_find_gender:
            find_gender(message)
        elif not limbo[user_id].about:
            try_info(message)
        else:
            cv(message)

    elif user_id in male_users.keys():
        create_match_male(message)





def get_age(message):
    user_id = message.chat.id
    age = message.text
    if not age.isdigit():
        bot.send_message(user_id, 'Возраст должен быть числом, например, 25!')
    else:
        limbo[user_id].age = age
        bot.send_message(user_id, 'Теперь введи свой город')


def get_city(message):
    user_id = message.chat.id
    limbo[user_id].city = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    keyboard.row('Парень', 'Девушка')
    bot.send_message(user_id, 'Ты парень или девушка?', reply_markup=keyboard)



def gender(message):
    user_id = message.chat.id
    if message.text == 'Парень':
        user_gender = 'm'
    else:
        user_gender = 'f'
    limbo[user_id].user_gender = user_gender
    keyboard = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    keyboard.row('Парней', 'Девушек', 'Все равно')
    bot.send_message(user_id, 'Кого ты ищешь?', reply_markup=keyboard)


def find_gender(message):
    user_id = message.chat.id
    user_find_gender = None
    if message.text == 'Парней':
        user_find_gender = 'm'
    elif message.text == 'Девушек':
        user_find_gender = 'f'
    else:
        user_find_gender = 'u'
    limbo[user_id].user_find_gender = user_find_gender
    bot.send_message(user_id, 'Хорошо, а теперь напиши что-нибудь о себе')

def try_info(message):
    user_id = message.chat.id
    about = message.text
    limbo[user_id].about = about
    photo = bot.get_user_profile_photos(user_id,limit=1)
    lensizes = len(photo.photos[0])-1
    x = bot.get_file_url(photo.photos[0][lensizes].file_id)
    user = limbo[user_id]
    bot.send_photo(user_id, get(x).content, user.name + ', ' + user.age + ', '
                   + user.city + '\n' +user.about)

    keyboard = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    keyboard.row('Да', 'Нет')
    bot.send_message(user_id, 'Это твоя анкета?', reply_markup=keyboard)


def cv(message):
    user_id = message.chat.id
    cv = message.text
    if cv == "Да":
        if limbo[user_id].user_gender == 'm':
            male_users[user_id] = limbo[user_id]
        else:
            fem_users[user_id] = limbo[user_id]

    del limbo[user_id]

    if cv == 'Нет':
        bot.send_message(message.chat.id, 'Чтож, давай начнем с начала...')
        message.text = '/start'
        start(message)

    keyboard = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    keyboard.row('Да')
    bot.send_message(user_id, 'Готов начать искать пары?', reply_markup=keyboard)



def create_match_male(message):
    list_of_id = []
    act_user = None
    if male_users[message.chat.id].user_find_gender == 'm':
        for i in list(male_users.keys()):
            if male_users[i].user_find_gender != 'f':
                list_of_id.append(i)
        x = choice(list_of_id)
        act_user = male_users[x]

    elif male_users[message.chat.id].user_find_gender == 'f':
        for i in list(fem_users.keys()):
            if fem_users[i].user_find_gender != 'f':
                list_of_id.append(i)
        x = choice(list_of_id)
        act_user = fem_users[x]

    else:
        for i in list(fem_users.keys()):
            if fem_users[i].user_find_gender != 'f':
                list_of_id.append(i)
        for i in list(male_users.keys()):
            if male_users[i].user_find_gender != 'f':
                list_of_id.append(i)
        x = choice(list_of_id)
        if x in fem_users.keys():
            act_user = fem_users[x]
        else:
            act_user = male_users[x]

    if act_user:
        photo = bot.get_user_profile_photos(x,limit=1)
        lensizes = len(photo.photos[0])-1
        ready_photo = bot.get_file_url(photo.photos[0][lensizes].file_id)
        bot.send_photo(message.chat.id, get(ready_photo).content, act_user.name + ', ' + act_user.age
                       + ', ' + act_user.city + '\n' + act_user.about)

        keyboard = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
        keyboard.row('👍Лайк👍', '👎Дислайк👎')
        bot.send_message(message.chat.id, 'Я тут кое-кого нашел для тебя. Что скажешь?', reply_markup=keyboard)
        bot.register_next_step_handler(message, adder)

    else:
        bot.send_message(message.chat.id, 'Пока что новых людей нет, приходи позже!')


def adder(message):
    if message.text == '👍Лайк👍':
        if message.chat.id in list(male_users.keys()):
            male_users[message.chat.id].i_like.append(x)
        else:
            fem_users[message.chat.id].i_like.append(x)
        somebody_like(x, message)



def somebody_like(id, message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=True)
    keyboard.row('Да', 'Нет')
    bot.send_message(message.chat.id, 'У тебя новый лайк, хочешь посмотреть?', reply_markup=keyboard)


def matcher(message):
    if message.text == 'Да':
        if message.chat.id in fem_users:
            for i in fem_users[x].like_me:
                pass






def create_match_female():
    pass







bot.polling()
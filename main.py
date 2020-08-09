import telebot
from telebot import types
import requests
import json
import sqlite3
import time
from threading import Timer
import googletrans
from googletrans import Translator
from geopy.geocoders import Nominatim

bot = telebot.TeleBot('1073948237:AAGKs3HzRBZwBZGkoQ5moJIakWQn39nQtX4')

conn = sqlite3.connect('data.db')
curs = conn.cursor()

table = """ CREATE TABLE IF NOT EXISTS notes (
                id integer PRIMARY KEY,
                name text NOT NULL,
                message_id integer NOT NULL
            ); """
curs.execute(table)

table = """ CREATE TABLE IF NOT EXISTS new_users (
                id integer PRIMARY KEY,
                user_id text NOT NULL,
                chat_id text NOT NULL,
                start_time integer NOT NULL
            ); """
curs.execute(table)
conn.close()

translator = Translator()

geolocator = Nominatim(user_agent="sanya_pilot_telegram_bot")

timers = {}


@bot.message_handler(commands=['start'])
def command_handler(message):
    bot.send_message(message.chat.id, 'Приветствую) Я бот-админ для чата.\nСправку по'
                                      ' командам можно получить по команде /help@sanya_pilot_bot\nЕсли что-то не '
                                      'работает, пните @alexander_baransky496\n')


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(chat_id=message.chat.id,
                     text='Список команд:\n'
                          '/tr - Перевести сообщение. /tr <код языка, на который надо перевести>'
                          '/notes - Показать список заметок\n'
                          '/note - Просмотр заметки\n'
                          '/addnote - Добавить заметку\n'
                          '/delnote - Удалить заметку\n'
                          '/mute - Мут навсегда (до размута)\n'
                          '/tmute - Мут на время. Время прописывается в формате <кол-во><s/m/h/d>\n'
                          '/unmute - Размут\n'
                          '/ban - Забанить пользователя навсегда (до разбана)\n'
                          '/banme - Забанить пользователя, написавшего команду\n'
                          '/tban - Забанить пользователя на время. Формат такой же как в /tmute\n'
                          '/unban - Разбан\n'
                          '/kick - Кикнуть пользователя\n'
                          '/kickme - Кикнуть пользователя, написавшего команду\n'
                          '/restrict - Лишение пользователя всех прав\n'
                          '/permit - Выдача пользователю всех прав\n'
                          '/dpermit - Выдача пользователю дефолтных прав чата\n'
                          '/demote - Лишение пользователя всех административных прав (пока не работает)\n'
                          '/promote - Выдача пользователю всех административных прав (пока не работает)\n'
                          'Чтобы применить все эти команды, необходимо ответить командой на сообщение пользователя, '
                          'которого вы хотите кикнуть, забанить и т. д.')


# Мут навсегда
@bot.message_handler(commands=['mute'])
def mute(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            chat = bot.get_chat(chat_id=message.chat.id)
            bot.restrict_chat_member(chat_id=message.chat.id,
                                     user_id=message.reply_to_message.from_user.id,
                                     can_send_messages=False,
                                     until_date=0)

            bot.send_message(chat_id=message.chat.id,
                             text='Мут был дан пользователю @' +
                                  str(message.reply_to_message.from_user.username) + ' навсегда')

        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


# Мут на время
@bot.message_handler(commands=['tmute'])
def tmute(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            timeout = message.text[7:]
            timeout_units = timeout[-1:]
            timeout_numbers = timeout[:-1]
            final_timeout = None
            timeout_text = None
            if timeout_units == 's':
                final_timeout = int(timeout_numbers)
                if int(timeout_numbers[-1:]) == 1:
                    text = ' секунду'
                elif 2 <= int(timeout_numbers) <= 4:
                    text = ' секунды'
                else:
                    text = ' секунд'
                timeout_text = timeout_numbers + text
            elif timeout_units == 'm':
                final_timeout = int(timeout_numbers) * 60
                if int(timeout_numbers[-1:]) == 1:
                    text = ' минуту'
                elif 2 <= int(timeout_numbers) <= 4:
                    text = ' минуты'
                else:
                    text = ' минут'
                timeout_text = timeout_numbers + text
            elif timeout_units == 'h':
                final_timeout = int(timeout_numbers) * 3600
                if int(timeout_numbers) == 1:
                    text = ' час'
                elif 2 <= int(timeout_numbers) <= 4:
                    text = ' часа'
                else:
                    text = ' часов'
                timeout_text = timeout_numbers + text
            elif timeout_units == 'd':
                final_timeout = int(timeout_numbers) * 86400
                if int(timeout_numbers) == 1:
                    text = ' день'
                elif 2 <= int(timeout_numbers[-1:]) <= 4:
                    text = ' дня'
                else:
                    text = ' дней'
                timeout_text = timeout_numbers + text

            chat = bot.get_chat(chat_id=message.chat.id)
            bot.restrict_chat_member(chat_id=message.chat.id,
                                     user_id=message.reply_to_message.from_user.id,
                                     can_send_messages=False,
                                     until_date=int(time.time()) + final_timeout)

            bot.send_message(chat_id=message.chat.id,
                             text='Мут был дан пользователю @' + str(
                                 message.reply_to_message.from_user.username) + ' на ' + timeout_text)

        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


# Размут
@bot.message_handler(commands=['unmute'])
def unmute(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            chat = bot.get_chat(chat_id=message.chat.id)
            perms = chat.permissions
            bot.restrict_chat_member(chat_id=message.chat.id,
                                     user_id=message.reply_to_message.from_user.id,
                                     can_send_messages=True,
                                     can_send_media_messages=perms.can_send_media_messages,
                                     can_send_polls=perms.can_send_polls,
                                     can_send_other_messages=perms.can_send_other_messages,
                                     can_add_web_page_previews=perms.can_add_web_page_previews,
                                     until_date=0)
            bot.send_message(chat_id=message.chat.id,
                             text='Мут был снят с пользователя @' + str(
                                 message.reply_to_message.from_user.username))
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['restrict'])
def restrict(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.restrict_chat_member(chat_id=message.chat.id,
                                     user_id=message.reply_to_message.from_user.id,
                                     until_date=0)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователь @' + str(message.reply_to_message.from_user.username) +
                                  ' был лишен прав')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['permit'])
def permit(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.restrict_chat_member(chat_id=message.chat.id,
                                     user_id=message.reply_to_message.from_user.id,
                                     can_send_messages=True,
                                     can_send_media_messages=True,
                                     can_send_polls=True,
                                     can_send_other_messages=True,
                                     can_add_web_page_previews=True,
                                     can_change_info=True,
                                     can_invite_users=True,
                                     can_pin_messages=True,
                                     until_date=0)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователю @' + str(message.reply_to_message.from_user.username) +
                                  ' были выданы полные пользовательские права (не путать с админкой)')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['dpermit'])
def permit_default(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            chat = bot.get_chat(chat_id=message.chat.id)
            perms = chat.permissions
            bot.restrict_chat_member(chat_id=message.chat.id,
                                     user_id=message.reply_to_message.from_user.id,
                                     can_send_messages=perms.can_send_messages,
                                     can_send_media_messages=perms.can_send_media_messages,
                                     can_send_polls=perms.can_send_polls,
                                     can_send_other_messages=perms.can_send_other_messages,
                                     can_add_web_page_previews=perms.can_add_web_page_previews,
                                     can_change_info=perms.can_change_info,
                                     can_invite_users=perms.can_invite_users,
                                     can_pin_messages=perms.can_pin_messages,
                                     until_date=0)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователю @' + str(message.reply_to_message.from_user.username) +
                                  ' были выданы дефолтные права')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


# Убрать все права
@bot.message_handler(commands=['demote'])
def demote(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.promote_chat_member(chat_id=message.chat.id,
                                    user_id=message.reply_to_message.from_user.id,
                                    can_pin_messages=0,
                                    can_change_info=0,
                                    can_edit_messages=0,
                                    can_invite_users=0,
                                    can_post_messages=0,
                                    can_delete_messages=0,
                                    can_promote_members=0,
                                    can_restrict_members=0
                                    )
            bot.send_message(chat_id=message.chat.id,
                             text='Пользователь @' + str(message.reply_to_message.from_user.username) +
                                  ' был лишен всех админских прав')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


# Дать все права
@bot.message_handler(commands=['promote'])
def promote(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.promote_chat_member(chat_id=message.chat.id,
                                    user_id=message.reply_to_message.from_user.id,
                                    can_pin_messages=1,
                                    can_change_info=1,
                                    can_edit_messages=1,
                                    can_invite_users=1,
                                    can_post_messages=1,
                                    can_delete_messages=1,
                                    can_promote_members=1,
                                    can_restrict_members=1
                                    )
            bot.send_message(chat_id=message.chat.id,
                             text='Пользователю @' + str(message.reply_to_message.from_user.username) +
                                  ' были выданы полные админские права')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['kick'])
def kick(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.kick_chat_member(chat_id=message.chat.id,
                                 user_id=message.reply_to_message.from_user.id,
                                 until_date=0)
            bot.unban_chat_member(chat_id=message.chat.id,
                                  user_id=message.reply_to_message.from_user.id)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователь @' + str(message.reply_to_message.from_user.username) +
                                  ' был кикнут\nОн сможет вернуться в чат в будущем')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['kickme'])
def kick(message):
    try:
        bot.kick_chat_member(chat_id=message.chat.id,
                             user_id=message.from_user.id,
                             until_date=0)
        bot.unban_chat_member(chat_id=message.chat.id,
                              user_id=message.from_user.id)

        bot.send_message(chat_id=message.chat.id,
                         text='Пользователь @' + str(message.from_user.username) +
                              ' был кикнут\nОн сможет вернуться в чат в будущем')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['ban'])
def ban(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.kick_chat_member(chat_id=message.chat.id,
                                 user_id=message.reply_to_message.from_user.id,
                                 until_date=0)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователь @' + str(message.reply_to_message.from_user.username) +
                                  ' был забанен\nОн больше НЕ сможет вернуться в чат в будущем')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['banme'])
def kick(message):
    try:
        bot.kick_chat_member(chat_id=message.chat.id,
                             user_id=message.from_user.id,
                             until_date=0)

        bot.send_message(chat_id=message.chat.id,
                         text='Пользователь @' + str(message.from_user.username) +
                              ' был забанен\nОн больше НЕ сможет вернуться в чат в будущем')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['tban'])
def tban(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            timeout = message.text[6:]
            timeout_units = timeout[-1:]
            timeout_numbers = timeout[:-1]
            final_timeout = None
            timeout_text = None
            if timeout_units == 's':
                final_timeout = int(timeout_numbers)
                if int(timeout_numbers[-1:]) == 1:
                    text = ' секунда'
                elif 2 <= int(timeout_numbers) <= 4:
                    text = ' секунды'
                else:
                    text = ' секунд'
                timeout_text = timeout_numbers + text
            elif timeout_units == 'm':
                final_timeout = int(timeout_numbers) * 60
                if int(timeout_numbers[-1:]) == 1:
                    text = ' минута'
                elif 2 <= int(timeout_numbers) <= 4:
                    text = ' минуты'
                else:
                    text = ' минут'
                timeout_text = timeout_numbers + text
            elif timeout_units == 'h':
                final_timeout = int(timeout_numbers) * 3600
                if int(timeout_numbers) == 1:
                    text = ' час'
                elif 2 <= int(timeout_numbers) <= 4:
                    text = ' часа'
                else:
                    text = ' часов'
                timeout_text = timeout_numbers + text
            elif timeout_units == 'd':
                final_timeout = int(timeout_numbers) * 86400
                if int(timeout_numbers) == 1:
                    text = ' день'
                elif 2 <= int(timeout_numbers[-1:]) <= 4:
                    text = ' дня'
                else:
                    text = ' дней'
                timeout_text = timeout_numbers + text

            bot.kick_chat_member(chat_id=message.chat.id,
                                 user_id=message.reply_to_message.from_user.id,
                                 until_date=int(time.time()) + final_timeout)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователь @' + str(message.reply_to_message.from_user.username) +
                                  ' был забанен на ' + timeout_text +
                                  '\nОн сможет вернуться в чат после истечения времени')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['unban'])
def unban(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            bot.unban_chat_member(chat_id=message.chat.id,
                                  user_id=message.reply_to_message.from_user.id)

            bot.send_message(chat_id=message.chat.id,
                             text='Пользователь @' + str(message.reply_to_message.from_user.username) +
                                  ' был разбанен\nТеперь он может вернуться в чат')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['notes'])
def notes(message):
    try:
        cmd = """ SELECT name FROM notes """

        conn = sqlite3.connect('data.db')
        curs = conn.cursor()
        curs.execute(cmd)
        rows = curs.fetchall()
        conn.close()
        text = '┏━━━━━━━━━━━━━━━━━━━━━━\n┣Список заметок:\n┃\n'
        for row in rows:
            text += '┣['
            text += row[0]
            text += '\n'

        text += '┗━━━━━━━━━━━━━━━━━━━━━━\n'
        text += 'Вы можете просмотреть заметку командой /note <имя-заметки> либо при помощи #<имя-заметки>'
        bot.reply_to(message, text)

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['note'])
def note(message):
    try:
        name = message.text[6:]
        conn = sqlite3.connect('data.db')
        curs = conn.cursor()
        cmd = """ SELECT message_id FROM notes
                  WHERE name = ? """
        curs.execute(cmd, (name,))

        rows = curs.fetchall()

        conn.close()

        row = rows[0]
        bot.forward_message(message.chat.id, message.chat.id, row[0])

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['addnote'])
def addnote(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            name = message.text[9:]
            conn = sqlite3.connect('data.db')
            curs = conn.cursor()
            cmd = """ INSERT INTO notes(name, message_id)
                      VALUES(?,?) """
            params = (name, message.reply_to_message.message_id)
            curs.execute(cmd, params)
            conn.commit()
            conn.close()

            bot.reply_to(message, 'Заметка была добавлена')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['delnote'])
def delnote(message):
    try:
        member = bot.get_chat_member(chat_id=message.chat.id,
                                     user_id=message.from_user.id)
        if member.status == 'creator' or member.status == 'administrator':
            name = message.text[9:]
            conn = sqlite3.connect('data.db')
            curs = conn.cursor()
            cmd = """ DELETE FROM notes WHERE name = ? """
            curs.execute(cmd, (name,))
            conn.commit()
            conn.close()

            bot.reply_to(message, 'Заметка была удалена')
        else:
            bot.reply_to(message, 'Для этого нужны админские права')

    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['tr'])
def tr(message):
    try:
        lang_code = message.text[4:]
        result = translator.translate(message.reply_to_message.text, dest=lang_code)

        langs = googletrans.LANGUAGES
        text = '<i>Перевод с <b>' + langs[result.src] + '</b> на <b>' + langs[lang_code] + '</b>\n'
        text += 'Translate from <b>' + langs[result.src] + '</b> to <b>' + langs[
            lang_code] + '</b></i>\n\n' + result.text
        bot.send_message(chat_id=message.chat.id,
                         reply_to_message_id=message.message_id,
                         parse_mode='HTML',
                         text=text)
    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(commands=['weather'])
def weather(message):
    try:
        city_name = message.text[9:]
        loc = geolocator.geocode(city_name)
        if loc is None:
            bot.reply_to(message, 'Такой город не найден')
        else:
            response = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat=' + str(loc.latitude) +
                                    '&lon=' + str(loc.longitude) + '&appid=c1c0032b6ff3be83e44ab641e780fc3d&lang=RU' +
                                    '&units=metric')

            data = json.loads(response.content)
            destination = loc.address.split(',')

            text = '<b><i>Погода в '
            for i in destination:
                if i == destination[0]:
                    text += i
                else:
                    text += ',' + i

            text += '</i></b>\n'
            text += '━━━━━━━━━━━━━━━━━━━━━━━\n'
            text += '<b>Текущая погода</b>\n'
            text += '━━━━━━━━━━━━━━━━━━━━━━━\n'
            text += '<b>' + str(data['current']['temp']) + ' °C <i>' + data['current']['weather'][0]['description'].capitalize() + '</i></b>\n'
            text += '<i>Чувствуется как:</i> <b>' + str(data['current']['feels_like']) + ' °C</b>\n'
            text += '<i>Влажность:</i> <b>' + str(data['current']['humidity']) + '%</b>\n'
            text += '<i>Давление:</i> <b>' + str(data['current']['pressure']) + ' гПа</b>\n'
            text += '<i>Скорость ветра:</i> <b>' + str(data['current']['wind_speed']) + ' м/с</b>\n'
            text += '<i>Облачность:</i> <b>' + str(data['current']['clouds']) + '%</b>\n'
            text += '<i>UV индекс:</i> <b>' + str(data['current']['uvi']) + '</b>\n'

            bot.send_message(chat_id=message.chat.id,
                             text=text,
                             reply_to_message_id=message.message_id,
                             parse_mode='HTML')
    except Exception:
        bot.reply_to(message, 'Упс... Что-то пошло не так')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    try:
        if message.text[0] == '#':
            name = message.text[1:]
            conn = sqlite3.connect('data.db')
            curs = conn.cursor()
            cmd = """ SELECT message_id FROM notes
                      WHERE name = ? """
            curs.execute(cmd, (name,))
            rows = curs.fetchall()
            conn.close()

            row = rows[0]
            bot.forward_message(message.chat.id, message.chat.id, row[0])

    except Exception:
        pass


# Триггер на нового юзера в чате
@bot.message_handler(content_types=['new_chat_members'])
def greeting(message):
    if not message.from_user.is_bot:
        text = 'Привет, как дела?\nЗдесь мы осуждаем телефон LeEco Le 2 (ну или не совсем)\nВ общем не '
        text += 'разжигай холивары и все будет ок)\n\nНо перед тем как ты вступишь в чат, нам нужно проверить,'
        text += ' действительно ли ты не бот. Для этого нужно нажать на кнопку, я думаю ты справишся\n\n'
        text += '<i><b>Ограничение по времени: 5 минут.\n'
        text += 'Если по истечении времени не была нажата кнопка, ты получаешь кик</b></i>'

        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton(text='Я хочу общатся!', callback_data='captcha_ok')
        keyboard.add(key)

        bot.send_message(chat_id=message.chat.id,
                         reply_to_message_id=message.message_id,
                         parse_mode='HTML',
                         text=text,
                         reply_markup=keyboard)

        global timers
        timers[message.from_user.id] = Timer(300.0, kick_bot, [message.chat.id, message.from_user.id])
        timers[message.from_user.id].start()


# Триггер на уход юзера из чата
@bot.message_handler(content_types=['left_chat_member'])
def greeting(message):
    bot.reply_to(message, text='Ну ладно, пока( *хнык*')


@bot.callback_query_handler(func=lambda call: True)
def button_callback_handler(call):
    try:
        if call.data == 'captcha_ok':
            global timers
            try:
                timers[call.from_user.id].cancel()
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text='Вы успешно прошли проверку!')
                timers.pop(call.from_user.id)
            except KeyError:
                bot.answer_callback_query(callback_query_id=call.id,
                                          text='Нельзя проходить проверку за другого пользователя')

    except Exception:
        bot.reply_to(call.message, 'Упс... Что-то пошло не так')


def kick_bot(chat_id, user_id):
    try:
        bot.kick_chat_member(chat_id=chat_id,
                             user_id=user_id,
                             until_date=0)

        bot.unban_chat_member(chat_id=chat_id,
                              user_id=user_id)

        chat_member = bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        user = chat_member.user
        bot.send_message(chat_id=chat_id,
                         text='Пользователь @' + str(user.username) +
                              ' не прошел проверку на бота\nОн был кикнут')
        global timers
        timers.pop(user_id)

    except Exception:
        bot.send_message(chat_id=chat_id, text='Упс... Что-то пошло не так')


bot.polling()
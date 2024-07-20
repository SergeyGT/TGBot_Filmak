import json
import telebot
import requests
import sqlite3
import markup
from telebot import types
bot = telebot.TeleBot('7306096819:AAGnw11JUUqDTKp3Mn13Y-VPtOx1csofUqM')
kinoApi = '7afdc576-db4b-4d3d-b0b2-26e0b6468301'

@bot.message_handler(commands=['start'])
def welcome(message):
    conn = sqlite3.connect('db_genres_and_id_films.sql')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_genre INTEGER,
        name_genre VARCHAR(50)

    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_country INTEGER,
    name_country VARCHAR(50)
    )
    """ )

    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Привет, давай посмотрим фильмы или сериалы! Напиши жанр и я случайно подберу тебе фильм')


    #bot.register_next_step_handler(message, get_genre)

@bot.message_handler(commands=['show'])
def show_movies(message):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Показать жанры и страны", callback_data='view'))
        bot.send_message(message.chat.id, "Показать?", reply_markup=markup)




@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('db_genres_and_id_films.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM genres")
    genres = cur.fetchall()
    info_genres = ""
    for g in genres:
        info_genres += f'<em>ID жанра</em> - <b>{g[1]}</b>. <em>Жанр</em> - <b>{g[2]}</b>\n'

    bot.send_message(call.message.chat.id, info_genres, parse_mode='html')

    cur.execute("SELECT * FROM countries")
    countries = cur.fetchall()
    info_countries = ""
    for c in countries:
        info_countries += f'<em>ID страны</em> - <b>{c[1]}</b>. <em>Страна</em> - <b>{c[2]}</b>\n'

    bot.send_message(call.message.chat.id, info_countries, parse_mode='html')
    cur.close()
    conn.close()





bot.polling(none_stop=True)



#TODO 1. Поиск трейлера фильма
#TODO 2. Поиск похожих фильмов
#?TODO 3. Поиск сиквелов и приквелов?





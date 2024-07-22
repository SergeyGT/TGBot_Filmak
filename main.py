import json
import random

import telebot
import requests
import sqlite3
import markup
from telebot import types
bot = telebot.TeleBot('7306096819:AAGnw11JUUqDTKp3Mn13Y-VPtOx1csofUqM')
kinoApi = '7afdc576-db4b-4d3d-b0b2-26e0b6468301'
headers = {
    'X-API-KEY': kinoApi,
    'Content-Type': 'application/json'
}


# Словарь фильм_ru: фильм_en
genres_dict = {
    'фильм': "FILM",
    'сериал': "TV_SERIES",
    'мини': "MINI_SERIES",
}

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
    bot.send_message(message.chat.id, 'Привет, давай посмотрим фильмы или сериалы! Выбери в меню или с помощью '
                                      'кнопок, что хочешь сделать!')


    #bot.register_next_step_handler(message, get_genre)

@bot.message_handler(commands=['show'])
def show_info(message):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Показать жанры и страны", callback_data='view'))
        bot.send_message(message.chat.id, "Нажми кнопку, если хочешь посмотреть информацию", reply_markup=markup)




@bot.callback_query_handler(func=lambda call: call.data == 'view')
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

    bot.send_message(call.message.chat.id, "Теперь ты можешь найти фильмы, которые тебе нужны :)")


@bot.message_handler(commands=['movies'])
def get_movies(message):
    bot.send_message(message.chat.id, "Чтобы найти фильм тебе нужно написать сообщение в таком формате:\n"
                                      "<b>жанр</b> <b>страна</b><em>(если страна не важна, это можно пропустить)</em> <b>тип кино</b>"
                                      "(фильм, сериал, мини)", parse_mode='html')
    bot.register_next_step_handler(message, show_movies)


def show_movies(message):
    userInputInfoMovie = message.text.strip().lower().split()
    numParams = len(userInputInfoMovie) # < Отвечает за кол-во параметров введенных пользователем для проверки учета страны

    conn = sqlite3.connect('db_genres_and_id_films.sql')
    cur = conn.cursor()

    cur.execute("SELECT id_genre FROM genres WHERE name_genre = ?", (userInputInfoMovie[0], ))
    genreUn = cur.fetchall()
    infoGenre = genreUn[0][0]

    if numParams == 3:
        cur.execute("SELECT id_country FROM countries WHERE name_country = ?", (userInputInfoMovie[1],))
        countryUn = cur.fetchall()
        infoCountry = countryUn[0][0]
        urlWith = f'https://kinopoiskapiunofficial.tech/api/v2.2/films?countries={infoCountry.capitalize()}&genres={infoGenre}&order=RATING&type={genres_dict[userInputInfoMovie[1]]}&ratingFrom=4&ratingTo=10&yearFrom=1000&yearTo=3000&page={random.randint(1, 20)}'


    elif numParams == 2:
            urlWith = f'https://kinopoiskapiunofficial.tech/api/v2.2/films?genres={infoGenre}&order=RATING&type={genres_dict[userInputInfoMovie[1]]}&ratingFrom=4&ratingTo=10&yearFrom=1000&yearTo=3000&page={random.randint(1, 20)}'

    else:
        bot.send_message(message.chat.id, "Некорректный формат вводимых данных. Попробуйте снова!", get_movies(message))
    cur.close()
    conn.close()

    urlMovie = 'https://kinopoiskapiunofficial.tech/api/v2.2/films'

    resShowMovie = requests.get(urlMovie, headers=headers)

    if resShowMovie.status_code == 200:
        movieList = resShowMovie.json()
        if "items" in movieList:
            for item in movieList["items"]:
                kinoId = item.get("kinopoiskId", "N/A")
                kinoName = item.get("nameRu", "N/A")
                kinoNameEn = item.get("nameOriginal", "N/A")
                genres = [genre["genre"] for genre in item.get("genres", [])]
                countryInfo = ', '.join([country["country"] for country in item.get("countries", [])])
                rateKino = item.get("ratingKinopoisk", "N/A")
                rateImdb = item.get("ratingImdb", "N/A")
                year = item.get("year", "N/A")
                poster = item.get("posterUrl")
                caption = (f"<b>{kinoName} / {kinoNameEn}</b>\n"
                           f"Жанр: <b>{', '.join(genres)}</b>\n"
                           f"Страна: <b>{countryInfo}</b>\n"
                           f"Год выпуска: <b>{year}</b>\n"
                           f"Рейтинг Кинопоиска: <b>{rateKino}</b>\n"
                           f"Рейтинг в мире: <b>{rateImdb}</b>")

                if poster:
                    bot.send_photo(message.chat.id, poster, caption=caption, parse_mode="html")
                else:
                    bot.send_message(message.chat.id, caption, parse_mode="html")
        # movieList = json.loads(resShowMovie.text)
        # for item in movieList["items"]:
        #     kinoId = item["kinopoiskId"]
        #     kinoName = item["nameRu"]
        #     kinoNameEn = item["nameOriginal"]
        #     countryInfo = item["genres"]["genre"]
        #     rateKino = item["ratingKinopoisk"]
        #     rateImdb = item["ratingImdb"]
        #     year = item["year"]
        #     poster = item["posterUrl"]

            # if poster:
            #     bot.send_photo(message.chat.id, poster, caption=f"<h1>{kinoName}/{kinoNameEn}</h1>\n"
            #                                                     f"Страна: <b>{countryInfo}</b>\n"
            #                                                     f"Год выпуска: <b>{year}</b>\n"
            #                                                     f"Рейтинг Кинопоиска: <b>{rateKino}</b>\n"
            #                                                     f"Рейтинг в мире: <b>{rateImdb}", parse_mode="html")
            # else:
            #     bot.send_message(message.chat.id, f"<h1>{kinoName}/{kinoNameEn}</h1>\n"
            #                                                     f"Страна: <b>{countryInfo}</b>\n"
            #                                                     f"Год выпуска: <b>{year}</b>\n"
            #                                                     f"Рейтинг Кинопоиска: <b>{rateKino}</b>\n"
            #                                                     f"Рейтинг в мире: <b>{rateImdb}", parse_mode="html")

    else:
            bot.send_message(message.chat.id, "Ошибка кинопоиска попробуйте снова")


bot.polling(none_stop=True)



#TODO 1. Поиск трейлера фильма
#TODO 2. Поиск похожих фильмов
#?TODO 3. Поиск сиквелов и приквелов?





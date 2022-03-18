import os
import telebot
import logging
import psycopg2
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def update_messages_count(user_id):
    db_object.execute(f'UPDATE users SET messages = messages + 1 WHERE id = {user_id}')
    db_connection.commit()


def fullname(user_id):
    db_object.execute("INSERT INTO info_for_users(id, Name) VALUES (%s,%s,%s)", (id, Name, Surname, 0))
    db_connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, f'Привет, {username}!')

    db_object.execute(f"SELECT id FROM users WHERE id = {id}")
    result = db_object.fetchone()  # Возвращает в кач-ве рез-та одну строчку с рез-том запроса

    if not result:
        db_object.execute("INSERT INTO users(id, username, messages) VALUES (%s, %s, %s)", (id, username, 0))
        db_connection.commit()

    update_messages_count(user_id)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_from_users(message):
    user_id = message.from_user.id
    update_messages_count(user_id)


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, 'Как тебя зовут?')
        # bot.register_next_step_handler(message, get_name)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши Привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

    fullname(user_id)


@server.route(f"/{BOT_TOKEN}", methods=["POST"])  # Перенаправление информации с сервера "HIROKU" в бота
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=(os.environ.get("PORT", 5000)))

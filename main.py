import os
import telebot
import logging
import psycopg2
from config import *
from flask import Flask, request
from telebot import types

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def update_messages_count(user_id):
    db_object.execute(f"UPDATE users SET messages = messages + 1 WHERE id = {user_id}")
    db_connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, f'Привет, {username}, для получения инструкции нажмите /help')

    db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = db_object.fetchone()  # Возвращает в кач-ве рез-та одну строчку с рез-том запроса

    if not result:
        db_object.execute("INSERT INTO users(id, username, messages) VALUES (%s, %s, %s)", (user_id, username, 0))
        db_connection.commit()

    update_messages_count(user_id)


@bot.message_handler(commands=["help"])
def _help_(message):
    bot.reply_to(message, f'Какая- то полезная информация')
    user_id = message.from_user.id
    update_messages_count(user_id)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_from_users(message):
    user_id = message.from_user.id
    update_messages_count(user_id)


@bot.message_handler(commands=["table"])
def table_(message):
    user_id = message.from_user.id
    db_object.execute = """
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL, 
      age INTEGER,
      gender TEXT,
      nationality TEXT
    )
    """
    update_messages_count(user_id)


@server.route(f"/{BOT_TOKEN}", methods=["POST"])  # Перенаправление информации с сервера "HIROKU" в бота
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


def next_step_func():
    pass


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=(os.environ.get("PORT", 5000)))

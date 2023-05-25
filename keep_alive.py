# To keep the webserver on replit alive, it is used with uptimeRobot
# @Author: Beau Carnes
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/

from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "Hello. I am alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()

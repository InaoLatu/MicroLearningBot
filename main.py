# Author: Inao Latourrette Garcia
# Contact: inao.latourrette@gmail.com
# GitHub: https://github.com/InaoLatu
import logging
import types

import telegram
from telegram import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Filters
import requests
import re
import urllib
import json
import time

URL_AT = "http://178.79.170.232:8000/json?content="

TOKEN = "729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0"
URL_bot = "https://api.telegram.org/bot{}/".format(TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


Q1, Q2, Q3, END_QUIZ = range(4)

def pic(bot, update):
    contents = requests.get('https://random-d.uk/api/v2/random').json()
    url = contents['url']
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL_bot + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def q2(update, context):
    contents = requests.get('http://178.79.170.232:8000/json?content=1').json()
    reply_keyboard = ['A', 'B', 'C']
    update.message.reply_text(
        "Question " + str(2) + ": " + contents['quiz'][1]['question'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return Q3


def q3(update, context):
    contents = requests.get('http://178.79.170.232:8000/json?content=1').json()
    reply_keyboard = ['A', 'B', 'C']
    update.message.reply_text(
        "Question " + str(3) + ": " + contents['quiz'][2]['question'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return END_QUIZ


def end_quiz(update, context):
    update.message.reply_text("CONGRATS! You have completed the micro content!")
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def get_mc(update, context):  # Get the micro content json
    contents = requests.get('http://178.79.170.232:8000/json?content=1').json()
    reply_keyboard = ['A', 'B', 'C']

    title = contents['title']
    author = contents['meta_data']['author']
    explanation = contents['text'][0]
    # chat_id = update.message.chat_id
    markup = telegram.ReplyKeyboardRemove(selective=False)  # To remove the keyboard buttons from the previous interaction
    # bot.send_message(chat_id, "Hi! You are going to start the micro content! ", reply_markup=markup)
    chat_id = update.message.chat_id

    update.message.reply_text("Hi! You are going to start the micro content! ")
    update.message.reply_text("Micro content: "+title)
    update.message.reply_text(explanation)
    update.message.reply_text("Author: "+author)
    update.message.reply_text("Loading video...")

    video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')
    update.message.reply_video(video)

    update.message.reply_text(
        "Question "+str(1) + ": " + contents['quiz'][0]['question'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return Q2


def main():
    updater = Updater('729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('pic', pic))
    contents = requests.get('http://178.79.170.232:8000/json?content=1').json()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('mc', get_mc)],

        states={
            Q2: [MessageHandler(Filters.text, q2)],

            Q3: [MessageHandler(Filters.text, q3)],

            END_QUIZ: [MessageHandler(Filters.text, end_quiz)],


        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # dp.add_error_handler(error)


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

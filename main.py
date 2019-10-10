from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re
import urllib
import json
import time

URL_AT = "http://178.79.170.232:8000/json?content="

TOKEN = "729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0"
URL_bot = "https://api.telegram.org/bot{}/".format(TOKEN)


def bop(bot, update):
    url = get_image_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)

def get_image_url():
    allowed_extensions = ['jpg', 'png']
    file_extension = ''
    url = ''
    while file_extension not in allowed_extensions:
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def pic(bot, update):
    contents = requests.get('https://random-d.uk/api/v2/random').json()
    url = contents['url']
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL_bot + "getUpdates?timeout=10"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

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


def handle_updates(updates, index, contents, chat_id, keyboard):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        send_message("Question " + str(index) + ": " + contents['quiz'][index]['question'], chat_id, keyboard)



def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def build_quiz(contents, bot, update, chat_id):
    keyboard = build_keyboard(['A', 'B', 'C'])
    send_message("Question " + str(0) + ": " + contents['quiz'][0]['question'], chat_id, keyboard)
    for index, item in enumerate(contents["quiz"]):
        last_update_id = None
        index = 0
        while True:
            updates = get_updates(last_update_id)
            if (len(updates["result"])) > 0:
                last_update_id = get_last_update_id(updates) + 1
                time.sleep(0.5)
                if index+1 >= 3:
                    break
                else:
                    index = index + 1
                    send_message("Question " + str(index) + ": " + contents['quiz'][index]['question'], chat_id, keyboard)




def get_mc(bot, update):  #Get the micro content json
    contents = requests.get('http://178.79.170.232:8000/json?content=1').json()
    title = contents['title']
    author = contents['meta_data']['author']
    explanation = contents['text'][0]

    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="Micro content: "+title)
    bot.send_message(chat_id=chat_id, text=explanation)
    bot.send_message(chat_id=chat_id, text="Author: "+author)
    build_quiz(contents, bot, update, chat_id)


def main():
    updater = Updater('729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('pic', pic))
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('mc', get_mc))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
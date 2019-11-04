# Author: Inao Latourrette Garcia
# Contact: inao.latourrette@gmail.com
# GitHub: https://github.com/InaoLatu
# LinkedIn: https://www.linkedin.com/in/inaolatourrette

import logging

from telegram import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Filters, \
    CallbackQueryHandler
import requests
import json
import utils


URL_AT = "http://178.79.170.232:8000/json?content="

TOKEN = "729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0"
URL_bot = "https://api.telegram.org/bot{}/".format(TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# MENU1, MENU2 = range(2)
U1, U2, U3, U4, U5, BACK = range(6)
MENU1, MENU2, Q1, Q2, Q3, END_QUIZ, RESULTS = range(7)  # Stages of the quiz

micro_content = requests.get('http://178.79.170.232:8000/json?content=1').json()

selections = []
solutions = []


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def q2(update, context):
    user = update.message.from_user  # User who has answered
    logger.info("Answer for Question 1 of %s: %s", user.first_name, update.message.text)
    selections.append(update.message.text)
    reply_keyboard = ['A', 'B', 'C']
    update.message.reply_text(
        "Question " + str(2) + ": " + micro_content['quiz'][1]['question'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return Q3


def q3(update, context):
    user = update.message.from_user  # User who has answered
    logger.info("Answer for Question 2 of %s: %s", user.first_name, update.message.text)
    selections.append(update.message.text)
    reply_keyboard = ['A', 'B', 'C']
    update.message.reply_text(
        "Question " + str(3) + ": " + micro_content['quiz'][2]['question'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return END_QUIZ


def end_quiz(update, context):
    user = update.message.from_user  # User who has answered
    logger.info("Answer for Question 3 of %s: %s", user.first_name, update.message.text)
    selections.append(update.message.text)
    logger.info("Selections of user %s", selections)
    update.message.reply_text("CONGRATS! You have completed the micro content!")
    update.message.reply_text("Now it is time to see your results")

    correct = 0
    index = 0
    for q in micro_content['quiz']:
        update.message.reply_text("Question "+str(index)+": "+micro_content['quiz'][index]['question'])
        update.message.reply_text("Option selected by you: "+selections[index])
        if micro_content['quiz'][index]['answer'] == selections[index]:
            update.message.reply_text("CORRECT!")
            correct = correct +1
        else:
            update.message.reply_text("Ups, wrong "+"\U0001F641")
            update.message.reply_text("Correct answer: "+micro_content['quiz'][index]['answer'])
        update.message.reply_text("Explanation: " + micro_content['quiz'][index]['explanation'])
        index = index + 1

    update.message.reply_text("YOUR FINAL RESULT: "+str(correct)+"/"+str(len(micro_content['quiz'])))

    return ConversationHandler.END


def show_results(update, context):
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def get_mc(update, context):  # Get the micro content json
    query = update.callback_query
    bot = context.bot
    solutions.clear()  # Clear the answer from the previous micro content
    selections.clear()
    reply_keyboard = ['A', 'B', 'C']
    logger.info("micro content %s", micro_content)

    for i in micro_content['quiz']:
        solutions.append(i['answer'])
    logger.info("Solutions %s", solutions)

    title = micro_content['title']  # Info about the micro content

    author = micro_content['meta_data']['author']
    explanation = micro_content['text'][0]

    # update.message.reply_text("Hi! You are going to start the micro content! ")
    # update.message.reply_text("Micro content: "+title)
    # update.message.reply_text(explanation)
    # update.message.reply_text("Author: "+author)
    # update.message.reply_text("Loading video...")

    # video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')
    # update.message.reply_video(video)

    video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')
    chat_id = update.message.chat_id
    bot.send_video(chat_id, video)

    update.message.reply_text(
        "Question "+str(1) + ": " + micro_content['quiz'][0]['question'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    #bot.edit_message_text(
    #    chat_id=query.message.chat_id,
    #    message_id=query.message.message_id,
    #    text="Choose an option",
    #    reply_markup=reply_keyboard
    #)
    return Q2


def mc(update, context):
    query = update.callback_query
    bot = context.bot
    chat_id = query.message.chat_id
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Time to start the micro content!",
    )
    bot.send_message(chat_id, text="Micro content: "+micro_content['title'])
    bot.send_message(chat_id, text=micro_content['text'][0])
    bot.send_message(chat_id, text="Author: "+micro_content['meta_data']['author'])
    bot.send_message(chat_id, text="Loading video...")

    video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')
    bot.send_video(chat_id, video)
    reply_keyboard = build_keyboard(['A', 'B', 'C'])
    bot.send_message(chat_id, text="Question "+str(1) + ": " + micro_content['quiz'][0]['question'], reply_markup=reply_keyboard)

    return Q2


def unit1(update, context):
    query = update.callback_query
    bot = context.bot

    button_list = [
        InlineKeyboardButton("mc 1", callback_data="mc1"),
        InlineKeyboardButton("mc 2", callback_data="mc2"),
        InlineKeyboardButton("mc 3", callback_data="mc3"),
        InlineKeyboardButton("mc 4", callback_data="mc4")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose a micro content in Unit 1",
        reply_markup=reply_markup
    )

    return MENU2


def unit2(update, context):
    query = update.callback_query
    bot = context.bot
    button_list = [
        InlineKeyboardButton("mc 1", callback_data="mc1"),
        InlineKeyboardButton("mc 2", callback_data="mc2"),
        InlineKeyboardButton("mc 3", callback_data="mc3"),
        InlineKeyboardButton("mc 4", callback_data="mc4")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose a micro content in Unit 2",
        reply_markup=reply_markup
    )

    return MENU2


def menu1(update, context):

    button_list = [
        InlineKeyboardButton("Unit 1", callback_data="unit1"),
        InlineKeyboardButton("Unit 2", callback_data="unit2"),
        InlineKeyboardButton("Unit 3", callback_data="unit3"),
        InlineKeyboardButton("Unit 4", callback_data="unit4")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))
    update.message.reply_text("Choose a unit of micro content: ", reply_markup=reply_markup)
    return MENU1


def menu1_back(update, context):
    query = update.callback_query
    bot = context.bot

    button_list = [
        InlineKeyboardButton("Unit 1", callback_data="unit1"),
        InlineKeyboardButton("Unit 2", callback_data="unit2"),
        InlineKeyboardButton("Unit 3", callback_data="unit3"),
        InlineKeyboardButton("Unit 4", callback_data="unit4")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose a unit of micro content",
        reply_markup=reply_markup
    )

    return MENU2



def main():
    updater = Updater('729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0', use_context=True)
    dp = updater.dispatcher



    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('mc', get_mc), CommandHandler('menu', menu1)],

        states={

            MENU1: [CallbackQueryHandler(unit1, pattern='^unit1$'),
                    CallbackQueryHandler(unit2, pattern='^unit2$'),
                    CallbackQueryHandler(unit1, pattern='^unit3$'),
                    CallbackQueryHandler(unit2, pattern='^unit4$')],
            MENU2: [CallbackQueryHandler(mc, pattern='^mc1$'),
                    CallbackQueryHandler(mc, pattern='^mc2$'),
                    CallbackQueryHandler(mc, pattern='^mc3$'),
                    CallbackQueryHandler(mc, pattern='^mc4$'),
                    CallbackQueryHandler(menu1_back, pattern='^back$')],


            Q2: [MessageHandler(Filters.text, q2)],

            Q3: [MessageHandler(Filters.text, q3)],

            END_QUIZ: [MessageHandler(Filters.text, end_quiz)],

            RESULTS: [MessageHandler(Filters.text, show_results)],

            

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    # dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

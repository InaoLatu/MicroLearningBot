# Author: Inao Latourrette Garcia
# Contact: inao.latourrette@gmail.com
# GitHub: https://github.com/InaoLatu
# LinkedIn: https://www.linkedin.com/in/inaolatourrette

import logging

import telegram
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

    correct = 0
    index = 0
    results = []
    for q in micro_content['quiz']:
        block = ""
        question = "Question "+str(index)+": "+micro_content['quiz'][index]['question'] + "\n"
        question = question.upper()
        selection = "You chose: "+selections[index] + "\n"
        block = block + question + selection
        if micro_content['quiz'][index]['answer'] == selections[index]:
            solution_message = "CORRECT! "+"\U0001F603" + "\n"
            block = block + solution_message
            correct = correct +1
        else:
            solution_message = "Ups, wrong "+"\U0001F641" + "\n"
            correct_answer = "Correct answer: "+micro_content['quiz'][index]['answer']+"\n"
            block = block + solution_message + correct_answer
        explanation = "Explanation: " + micro_content['quiz'][index]['explanation']
        block = block + explanation
        index = index + 1
        results.append(block)

    update.message.reply_text("YOUR FINAL RESULT: "+str(correct)+"/"+str(len(micro_content['quiz'])))
    for r in results:  # To print the block of each question
        update.message.reply_text(r)
    selections.clear()

    update.message.reply_text("You can keep doing micro content with the following command:\n\n"
                              "/menu - It will show you the available Units.")
    return ConversationHandler.END


def show_results(update, context):
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
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
        text="Start the micro content!",
    )
    bot.send_message(chat_id, text="Micro content: "+micro_content['title']+"\n"+micro_content['text'][0]+"\nAuthor: "+micro_content['meta_data']['author'])
    #  bot.send_message(chat_id, text=micro_content['text'][0])
    #  bot.send_message(chat_id, text="Author: "+micro_content['meta_data']['author'])
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
        InlineKeyboardButton("mc 4", callback_data="mc4"),
        InlineKeyboardButton("Back to Units", callback_data="back")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*UNIT 1* \n"
             "Choose a micro content:",
        parse_mode=telegram.ParseMode.MARKDOWN,
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
        InlineKeyboardButton("mc 4", callback_data="mc4"),
        InlineKeyboardButton("Back to Units", callback_data="back")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*UNIT 2* \n"
             "Choose a micro content:",
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    return MENU2


def unit3(update, context):
    query = update.callback_query
    bot = context.bot

    button_list = [
        InlineKeyboardButton("mc 1", callback_data="mc1"),
        InlineKeyboardButton("mc 2", callback_data="mc2"),
        InlineKeyboardButton("mc 3", callback_data="mc3"),
        InlineKeyboardButton("mc 4", callback_data="mc4"),
        InlineKeyboardButton("Back to Units", callback_data="back")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*UNIT 3* \n"
             "Choose a micro content:",
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    return MENU2


def unit4(update, context):
    query = update.callback_query
    bot = context.bot

    button_list = [
        InlineKeyboardButton("mc 1", callback_data="mc1"),
        InlineKeyboardButton("mc 2", callback_data="mc2"),
        InlineKeyboardButton("mc 3", callback_data="mc3"),
        InlineKeyboardButton("mc 4", callback_data="mc4"),
        InlineKeyboardButton("Back to Units", callback_data="back")
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*UNIT 4* \n"
             "Choose a micro content:",
        parse_mode=telegram.ParseMode.MARKDOWN,
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
    update.message.reply_text("Choose a Unit of micro content: ", reply_markup=reply_markup)
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

    return MENU1

def start(update, context):
    update.message.reply_text("Welcome to Elemend micro learning bot! \n"
                              "You have the following commands available:\n\n"
                              "/menu - It will show you the available Units.\n"
                              "/cancel - To cancel the conversation whenever you want.")




def main():
    updater = Updater('729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0', use_context=True)
    dp = updater.dispatcher



    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('mc', get_mc), CommandHandler('menu', menu1), CommandHandler('start', start)],

        states={

            MENU1: [CallbackQueryHandler(unit1, pattern='^unit1$'),
                    CallbackQueryHandler(unit2, pattern='^unit2$'),
                    CallbackQueryHandler(unit3, pattern='^unit3$'),
                    CallbackQueryHandler(unit4, pattern='^unit4$')],
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
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

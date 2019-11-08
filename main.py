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

MENU1, MENU2, Q1, Q2, Q3, END_QUIZ, RESULTS, RESULTS2 = range(8)  # Stages of the quiz

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

    correct = 0
    index = 0
    all_answers = []
    correct_answers = []
    wrong_answers = []

    for q in micro_content['quiz']:
        block = ""
        question = "*Question " + str(index) + "*: " + micro_content['quiz'][index]['question'] + "\n"
        question = question.upper()
        selection = "You chose: " + selections[index] + "\n"
        block = block + question + selection
        explanation = "Explanation: " + micro_content['quiz'][index]['explanation']
        if micro_content['quiz'][index]['answer'] == selections[index]:
            solution_message = "CORRECT! " + "\U0001F603" + "\n"
            block = block + solution_message
            block = block + explanation
            correct_answers.append(block)
            correct = correct + 1
        else:
            solution_message = "Ups, wrong " + "\U0001F641" + "\n"
            correct_answer = "Correct answer: " + micro_content['quiz'][index]['answer'] + "\n"
            block = block + solution_message + correct_answer
            block = block + explanation
            wrong_answers.append(block)
        index = index + 1
        all_answers.append(block)

    update.message.reply_text("CONGRATS! You have completed the micro content!")
    update.message.reply_text("YOUR FINAL RESULT: " + str(correct) + "/" + str(len(micro_content['quiz'])))
    selections.clear()
    #  for r in results:  # To print the block of each question
    #    update.message.reply_text(text=r, parse_mode=telegram.ParseMode.MARKDOWN)
    #  selections.clear()

    context.user_data['correct_answers'] = correct_answers
    context.user_data['wrong_answers'] = wrong_answers
    context.user_data['all_answers'] = all_answers

    button_list = [
        InlineKeyboardButton("Only the wrong ones", callback_data="wrong"),
        InlineKeyboardButton("Only the correct ones", callback_data="correct"),
        InlineKeyboardButton("All", callback_data="all"),
        InlineKeyboardButton("None", callback_data="none"),
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
    update.message.reply_text("Check your answers: ",
                              reply_markup=reply_markup)

    return RESULTS


def show_wrong_answers(update, context):
    bot = context.bot
    query = update.callback_query

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*WRONG ANSWERS:*",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    for r in context.user_data['wrong_answers']:  # To print the block of each question
        bot.send_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=r,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing micro content with the following command:\n\n"
             "/menu - It will show you the available Units.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return RESULTS


def show_correct_answers(update, context):
    bot = context.bot
    query = update.callback_query

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*CORRECT ANSWERS:*",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    for r in context.user_data['correct_answers']:  # To print the block of each question
        bot.send_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=r,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing micro content with the following command:\n\n"
             "/menu - It will show you the available Units.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return RESULTS


def show_all_answers(update, context):
    bot = context.bot
    query = update.callback_query

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*ALL ANSWERS:*",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    for r in context.user_data['all_answers']:  # To print the block of each question
        bot.send_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=r,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing micro content with the following command:\n\n"
             "/menu - It will show you the available Units.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return RESULTS


def show_none_answers(update, context):
    bot = context.bot
    query = update.callback_query

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing micro content with the following command:\n\n"
             "/menu - It will show you the available Units.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def get_micro_content(update, context):
    query = update.callback_query
    bot = context.bot
    chat_id = query.message.chat_id
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Start the micro content!",
    )
    bot.send_message(chat_id,
                     text="Micro content: " + micro_content['title'] + "\n" + micro_content['text'][0] + "\nAuthor: " +
                          micro_content['meta_data']['author'])
    bot.send_message(chat_id, text="Loading video...")

    video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')
    bot.send_video(chat_id, video)
    reply_keyboard = build_keyboard(['A', 'B', 'C'])
    bot.send_message(chat_id, text="Question " + str(1) + ": " + micro_content['quiz'][0]['question'],
                     reply_markup=reply_keyboard)

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
        text="Choose a Unit of micro content",
        reply_markup=reply_markup
    )

    return MENU1


def start(update, context):
    update.message.reply_text("Welcome to Elemend micro learning bot! \n"
                              "You have the following commands available:\n\n"
                              "/start - Show the commands available.\n"
                              "/menu - It will show you the available Units.\n"
                              "/cancel - To cancel the conversation whenever you want.")


def main():
    updater = Updater('729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0', use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu1), CommandHandler('start', start)],

        states={

            MENU1: [CallbackQueryHandler(unit1, pattern='^unit1$'),
                    CallbackQueryHandler(unit2, pattern='^unit2$'),
                    CallbackQueryHandler(unit3, pattern='^unit3$'),
                    CallbackQueryHandler(unit4, pattern='^unit4$')],
            MENU2: [CallbackQueryHandler(get_micro_content, pattern='^mc1$'),
                    CallbackQueryHandler(get_micro_content, pattern='^mc2$'),
                    CallbackQueryHandler(get_micro_content, pattern='^mc3$'),
                    CallbackQueryHandler(get_micro_content, pattern='^mc4$'),
                    CallbackQueryHandler(menu1_back, pattern='^back$')],

            Q2: [MessageHandler(Filters.text, q2)],  # Receives in the filter the Q1

            Q3: [MessageHandler(Filters.text, q3)],

            END_QUIZ: [MessageHandler(Filters.text, end_quiz)],

            RESULTS: [CallbackQueryHandler(show_wrong_answers, pattern='^wrong$'),
                      CallbackQueryHandler(show_correct_answers, pattern='^correct$'),
                      CallbackQueryHandler(show_all_answers, pattern='^all$'),
                      CallbackQueryHandler(show_none_answers, pattern='^none$')],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

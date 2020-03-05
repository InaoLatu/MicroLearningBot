# Author: Inao Latourrette Garcia
# Contact: inao.latourrette@gmail.com
# GitHub: https://github.com/InaoLatu
# LinkedIn: https://www.linkedin.com/in/inaolatourrette

import logging
from time import sleep

import telegram
from telegram import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, \
    CallbackQueryHandler
import requests
import json
import utils


TOKEN = "729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0"  # Obtained from BotFather in Telegram app
URL_bot = "https://api.telegram.org/bot{}/".format(TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

MENU1, MENU2, START_QUIZ, Q2, Q3, END_QUIZ, RESULTS, RESULTS2 = range(8)  # Stages of the quiz

micro_content = []
selections = []
solutions = []

updater = Updater('729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0', use_context=True)
dp = updater.dispatcher


def start(update, context):
    update.message.reply_text("Welcome to Elemend micro learning bot! \n"
                              "You have the following commands available:\n\n"
                              "/help - Show the commands available.\n"
                              "/menu - Show you the available Units.\n"
                              "/cancel - Cancel the conversation whenever you want.")


def help(update, context):
    update.message.reply_text("You have the following commands available:\n\n"
                              "/help - Show the commands available.\n"
                              "/menu - Show you the available Units.\n"
                              "/cancel - Cancel the conversation.")


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


# Initial declaration of the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={

        MENU1: [],

        MENU2: []

    },

    fallbacks=[CommandHandler('cancel', cancel), CommandHandler('help', help)]
)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def q2(update, context):  # Shows the second question of the quiz and returns to the third question state
    user = update.message.from_user  # User who has answered
    logger.info("Answer for Question 1 of %s: %s", user.first_name, update.message.text)
    selections.append(update.message.text)

    choices = micro_content['quiz'][1]['choices']
    reply_keyboard = build_keyboard([choices[0]['choice_text'], choices[1]['choice_text'], choices[2]['choice_text']])

    update.message.reply_text(
        "Question " + str(2) + ": " + micro_content['quiz'][1]['question'],
        reply_markup=reply_keyboard)
    return Q3


def q3(update, context):
    user = update.message.from_user  # User who has answered
    logger.info("Answer for Question 2 of %s: %s", user.first_name, update.message.text)
    selections.append(update.message.text)

    choices = micro_content['quiz'][2]['choices']
    reply_keyboard = build_keyboard([choices[0]['choice_text'], choices[1]['choice_text'], choices[2]['choice_text']])

    update.message.reply_text(
        "Question " + str(3) + ": " + micro_content['quiz'][2]['question'],
        reply_markup=reply_keyboard)
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

    # Create the blocks of strings related to correct, wrong or all answers. These blocks will be displayed depending of
    # the selection of the user in this state. Each block include one question with the selection and the correct answer.
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

    context.user_data['correct_answers'] = correct_answers
    context.user_data['wrong_answers'] = wrong_answers
    context.user_data['all_answers'] = all_answers

    button_list = [
        InlineKeyboardButton("Only the wrong ones", callback_data="wrong"),
        InlineKeyboardButton("Only the correct ones", callback_data="correct"),
        InlineKeyboardButton("All", callback_data="all"),
        InlineKeyboardButton("Back to Units", callback_data="back"),
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
    update.message.reply_text(text="*Check your answers:* ",
                              parse_mode=telegram.ParseMode.MARKDOWN,
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
        sleep(4)  # To give the user time to read the text one at a time

    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing other micro content with the following command:\n\n"
             "/menu - Show you the available Units.",
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
        sleep(4)  # To give the user time to read the text one at a time

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing other micro content with the following command:\n\n"
             "/menu - Show you the available Units.",
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
        sleep(4)  # To give the user time to read the text one at a time

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="You can keep doing other micro content with the following command:\n\n"
             "/menu - Show you the available Units.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return RESULTS


def get_micro_content(update, context):  # Gets the selected micro-content
    query = update.callback_query
    bot = context.bot
    chat_id = query.message.chat_id
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Start the micro content!",
    )

    match = context.match
    micro_content_id = match.group(0)  # Id of the micro content selected in the display
    context.user_data['mc_id'] = micro_content_id

    global micro_content  # Edit the global value of micro_content so the rest of the functions see the same value
    micro_content = requests.get('http://127.0.0.1:7000/microcontent?id=' + str(micro_content_id)).json()

    bot.send_message(chat_id,
                     text="Micro content: " + micro_content['title'] + "\n" + micro_content['text'][0] + "\nAuthor: " +
                          micro_content['meta_data']['author'])


    bot.send_message(chat_id, text="Loading video...")
    video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')

    bot.send_video(chat_id, video)
    # sleep(15)

    button_list = [
        InlineKeyboardButton("Yes!", callback_data="yes"),
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=1))

    bot.send_message(chat_id, text="Ready for questions?", reply_markup=reply_markup)

    return START_QUIZ


def get_unit_micro_contents(update, context):  # Get the micro-content included in the selected Unit
    query = update.callback_query
    bot = context.bot
    match = context.match

    unit = match.group(0)  # Unit selected in the display
    micro_content_list = requests.get("http://127.0.0.1:7000/units/" + str(unit)).json()

    button_list = []
    for mc in micro_content_list:
        button_list += [InlineKeyboardButton(mc['title'], callback_data=str(mc['id']))]
        conv_handler.states[MENU2].append(
            CallbackQueryHandler(get_micro_content, pattern='^' + str(mc['id']) + '$'))  # Update states

    button_list += [InlineKeyboardButton("Back to Units", callback_data="back")]

    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*" + unit.capitalize() + "* \n" + "Choose a micro content: \n",
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    # bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return MENU2


def start_quiz(update, context):  # Shows the first question of the quiz and returns to the second question state
    query = update.callback_query
    bot = context.bot
    chat_id = query.message.chat_id

    choices = micro_content['quiz'][0]['choices']
    reply_keyboard = build_keyboard([choices[0]['choice_text'], choices[1]['choice_text'], choices[2]['choice_text']])
    bot.send_message(chat_id, text="Question " + str(1) + ": " + micro_content['quiz'][0]['question'],
                     reply_markup=reply_keyboard)

    return Q2


def get_units(update, context):
    units = requests.get('http://127.0.0.1:7000/units').json()  # Call Authoring Tool API to get the Units available
    button_list = []
    conv_handler.states[MENU1] = []  # Clean previous states

    for u in units:
        button_list += [InlineKeyboardButton(u['name'], callback_data=u['name'])]
        conv_handler.states[MENU1].append(CallbackQueryHandler(get_unit_micro_contents, pattern='^' + u['name'] + '$'))  # Update states

    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))
    update.message.reply_text("Choose a Unit of micro content: ", reply_markup=reply_markup)
    return MENU1


def back_to_units(update, context):
    query = update.callback_query
    bot = context.bot

    units = requests.get('http://127.0.0.1:7000/units').json()  # Call Authoring Tool API to get the Units available
    button_list = []
    conv_handler.states[MENU1] = []  # Clean previous states

    for u in units:
        button_list += [InlineKeyboardButton(u['name'], callback_data=u['name'])]
        conv_handler.states[MENU1].append(CallbackQueryHandler(get_unit_micro_contents, pattern='^' + u['name'] + '$'))  # Update states

    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.send_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose a Unit of micro content",
        reply_markup=reply_markup
    )

    return MENU1


def init_conv_handler():
    # Add entry points
    conv_handler.entry_points.append(CommandHandler('menu', get_units))
    # Add fallbacks
    conv_handler.fallbacks.append(CommandHandler('menu', get_units))
    # Add states
    conv_handler.states[MENU2] = [CallbackQueryHandler(back_to_units, pattern='^back$')]
    conv_handler.states[START_QUIZ] = [CallbackQueryHandler(start_quiz, pattern='^yes$'),
                                       CallbackQueryHandler(back_to_units, pattern='^back$')]
    conv_handler.states[Q2] = [MessageHandler(Filters.text, q2)]
    conv_handler.states[Q3] = [MessageHandler(Filters.text, q3)]
    conv_handler.states[END_QUIZ] = [MessageHandler(Filters.text, end_quiz)]
    conv_handler.states[RESULTS] = [CallbackQueryHandler(show_wrong_answers, pattern='^wrong$'),
                                    CallbackQueryHandler(show_correct_answers, pattern='^correct$'),
                                    CallbackQueryHandler(show_all_answers, pattern='^all$'),
                                    CallbackQueryHandler(back_to_units, pattern='^back$')]


def main():
    init_conv_handler()
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('help', help))

    updater.start_polling()  # Starts the bot
    updater.idle()


if __name__ == '__main__':
    main()

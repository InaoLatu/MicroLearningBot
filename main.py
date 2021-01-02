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

#BOT_TOKEN = "729590852:AAFHIQhSbUcLzXyXhh7ieaSheWtD1IU1wT0"  # ElemendMicrolearningBot
BOT_TOKEN = "1482182869:AAH7lnHnhpvAoi4o0lDkyGQ-f4iYIP7d9pQ" # InclusiBot
URL_bot = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

AUTH, MENU1, MENU2, START_QUIZ, Q2, Q3, END_QUIZ, RESULTS, RESULTS2 = range(9)  # Stages of the quiz

micro_content = []
selections = []
solutions = []

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
id_telegram_user = ""
auth_username = ""  # Username previously registered in the Auth Server

# General Manager API where all the request of the Bot are directed to
GENERAL_MANAGER_IP = "http://192.168.0.20:7030/general_manager/"
AUTH_TOOL_UNITS_IP = 'http://192.168.0.20:7020/units'


def start(update, context):
    # update.message.reply_text("Welcome to Elemend micro learning bot! \n"
    #                           "You have the following commands available:\n\n"
    #                           "/help - Show the commands available.\n"
    #                           "/menu - Show you the available Units.\n"
    #                           "/cancel - Cancel the conversation whenever you want.")

    global id_telegram_user
    id_telegram_user = update.effective_user.id

    update.message.reply_text("Por favor, introduce el siguiente comando para acceder: /auth")


def help(update, context):
    update.message.reply_text("Comandos disponibles:\n\n"
                              "/help - Muestra los comandos disponibles\n"
                              "/menu - Muestra la lista de unidades\n"
                              "/cancel - Cancela la conversación")


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('¡Hasta otra! Espero que hablemos pronto.',
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
        question = "*Pregunta " + str(index) + "*: " + micro_content['quiz'][index]['question'] + "\n"
        question = question.upper()
        selection = "Has elegido: " + selections[index] + "\n"
        block = block + question + selection
        #MOD si no hay explicación, mostramos texto por defecto.
        mc_explanation = micro_content['quiz'][index]['explanation']
        if mc_explanation == '':
            mc_explanation = 'No disponible.'

        explanation = "Explicación: " + mc_explanation
        
        if micro_content['quiz'][index]['answer'] == selections[index]:
            solution_message = "¡CORRECTO! " + "\U0001F603" + "\n"
            block = block + solution_message
            block = block + explanation
            correct_answers.append(block)
            correct = correct + 1
        else:
            solution_message = "Incorrecto " + "\U0001F641" + "\n"
            correct_answer = "Respuesta correcta: " + micro_content['quiz'][index]['answer'] + "\n"
            block = block + solution_message + correct_answer
            block = block + explanation
            wrong_answers.append(block)
        index = index + 1
        all_answers.append(block)

    request_string = GENERAL_MANAGER_IP + "store_mark"
    print(request_string)
    data = {
        'student_id': str(update.effective_user.id),
        'unit_name': str(context.user_data["current_unit"]),
        'microcontent_id': str(context.user_data["mc_id"]),
        'mark': str((correct/len(micro_content['quiz']))*100),
    }
    print(data)
    requests.post(request_string, data=data)
    update.message.reply_text("¡ENHORABUENA! Has completado el micro contenido!")
    update.message.reply_text("TU RESULTADO FINAL: " + str(correct) + "/" + str(len(micro_content['quiz'])))
    selections.clear()

    context.user_data['correct_answers'] = correct_answers
    context.user_data['wrong_answers'] = wrong_answers
    context.user_data['all_answers'] = all_answers

    button_list = [
        InlineKeyboardButton("Sólo las incorrectas", callback_data="wrong"),
        InlineKeyboardButton("Sólo las correctas", callback_data="correct"),
        InlineKeyboardButton("Todas", callback_data="all"),
        InlineKeyboardButton("Volver a Unidades", callback_data="back"),
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=1))
    update.message.reply_text(text="*Comprueba tus respuestas:* ",
                              parse_mode=telegram.ParseMode.MARKDOWN,
                              reply_markup=reply_markup)

    return RESULTS


def show_wrong_answers(update, context):
    bot = context.bot
    query = update.callback_query

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id,
        text="*RESPUESTAS INCORRECTAS:*",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    for r in context.user_data['wrong_answers']:  # To print the block of each question
        bot.send_message(
            chat_id=query.message.chat_id,
            reply_to_message_id=query.message.message_id,
            text=r,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        sleep(4)  # To give the user time to read the text one at a time

    bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id,
        text="Puedes hacer otros micro contenidos con el siguiente comando:\n\n"
             "/menu - Muestra la lista de unidades.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return RESULTS


def show_correct_answers(update, context):
    bot = context.bot
    query = update.callback_query

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id,
        text="*RESPUESTAS CORRECTAS:*",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    for r in context.user_data['correct_answers']:  # To print the block of each question
        bot.send_message(
            chat_id=query.message.chat_id,
            reply_to_message_id=query.message.message_id,
            text=r,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        sleep(4)  # To give the user time to read the text one at a time

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id,
        text="Puedes hacer otros micro contenidos con el siguiente comando:\n\n"
             "/menu - Muestra la lista de unidades.",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    return RESULTS


def show_all_answers(update, context):
    bot = context.bot
    query = update.callback_query
    #print(query)

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id,
        text="*TODAS LAS RESPUESTAS:*",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    for r in context.user_data['all_answers']:  # To print the block of each question
        bot.send_message(
            chat_id=query.message.chat_id,
            reply_to_message_id=query.message.message_id,
            text=r,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        sleep(4)  # To give the user time to read the text one at a time

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id, #MOD: message_id not working (send_message changed). Now reply_to_...
        text="Puedes hacer otros micro contenidos con el siguiente comando:\n\n"
             "/menu - Muestra la lista de unidades.",
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
        text="¡Comienza el micro contenido!",
    )

    match = context.match
    micro_content_id = match.group(0)  # Id of the micro content selected in the display
    context.user_data['mc_id'] = micro_content_id

    print("MICROCONTENT " + micro_content_id)

    global micro_content  # Edit the global value of micro_content so the rest of the functions see the same value
    micro_content = requests.get(GENERAL_MANAGER_IP + 'microcontent?id=' + str(micro_content_id)).json()

    bot.send_message(chat_id,
                     text="Micro contenido: " + micro_content['title'] + "\n" + micro_content['text'][0] + "\nAutor/a: " +
                          micro_content['meta_data']['author'])

    bot.send_message(chat_id, text="Cargando vídeo...")
    
    #MOD esto estaba hardcoded
    #video = open('/home/inao/Trabajo/ElemendBot/media/videos/microlearning.mp4', 'rb')#OJO CORREGIR!!!
    #bot.send_video(chat_id, video)
    #sleep(15)


    #youtube video
    video = micro_content['media'][0]['url']
    bot.send_message(chat_id, text=video, parse_mode = "HTML")#cargando con autoplay no reproduce automáticamente ( + "?autoplay=1")
    #bot.send_video(chat_id, video)

    #videofile not working
    #video = open('/home/mario/dev/MicroLearningPlatform/media/Lenguaje_inclusivo_3.mp4','rb')
    #bot.send_video(chat_id, video, supports_streaming = TRUE)
    
    button_list = [
        InlineKeyboardButton("¡Sí!", callback_data="yes"),
    ]
    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=1))

    bot.send_message(chat_id, text="¿Preparado para las preguntas?", reply_markup=reply_markup)

    return START_QUIZ


def get_unit_micro_contents(update, context):  # Get the micro-content included in the selected Unit
    query = update.callback_query
    bot = context.bot
    match = context.match
    unit = match.group(0)  # Unit selected in the display
    print("UNIDADE " + unit)  # DEBUG
    context.user_data["current_unit"] = str(unit)
    request_string = GENERAL_MANAGER_IP + "units/" + str(unit) + "/" + str(update.effective_user.id)
    #DEBUG
    print(request_string)
    micro_content_list = requests.get(request_string).json()

    button_list = []
    for mc in micro_content_list:
        if mc['completed']:
            button_list += [InlineKeyboardButton(mc['title']+" - completado", callback_data=str(mc['micro_id']))] #TRANS
        else:
            button_list += [InlineKeyboardButton(mc['title'], callback_data=str(mc['micro_id']))]
        conv_handler.states[MENU2].append(
            CallbackQueryHandler(get_micro_content, pattern='^' + str(mc['micro_id']) + '$'))  # Update states

    button_list += [InlineKeyboardButton("Volver a unidades", callback_data="back")] 
    #button_list += [InlineKeyboardButton(request_string, callback_data="back")]

    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*" + unit.capitalize() + "* \n" + "Elige un micro contenido: \n",
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
    bot.send_message(chat_id, text="Pregunta " + str(1) + ": " + micro_content['quiz'][0]['question'],
                     reply_markup=reply_keyboard)

    return Q2


def get_units(update, context):
    # First, check if the user has been authenticated, only if he is authenticated the user can access to the units
    req_string = GENERAL_MANAGER_IP + "check_user/telegram/" + str(update.effective_user.id)
    re = requests.get(req_string)
    if re.status_code == 404:
        update.message.reply_text("Debes identificarte primero.")
        #authenticate(update, context ,re.text) #MOD estaba comentado?
        update.message.reply_text("Introduce tu nombre de usuario: ")
        return AUTH
    else:
        req_string = GENERAL_MANAGER_IP + "get_units/"
        units = requests.get(req_string).json()  # Call Authoring Tool API to get the Units available
        button_list = []
        conv_handler.states[MENU1] = []  # Clean previous states

        for u in units:
            button_list += [InlineKeyboardButton(u['name'], callback_data=u['name'])]
            conv_handler.states[MENU1].append(
                CallbackQueryHandler(get_unit_micro_contents, pattern='^' + u['name'] + '$'))  # Update states

        reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))
        update.message.reply_text("Elige una unidad: ", reply_markup=reply_markup)
    return MENU1


#ERROR: File "main.py", line 428, in back_to_units
#       reply_markup=reply_markup
#       TypeError: send_message() got an unexpected keyword argument 'message_id'
def back_to_units(update, context):
    query = update.callback_query
    bot = context.bot
    #revisar
    #units = requests.get('http://127.0.0.1:7000/units').json()  # Call Authoring Tool API to get the Units available
    units = requests.get(AUTH_TOOL_UNITS_IP).json()  # Call Authoring Tool API to get the Units available
    button_list = []
    conv_handler.states[MENU1] = []  # Clean previous states

    for u in units:
        button_list += [InlineKeyboardButton(u['name'], callback_data=u['name'])]
        conv_handler.states[MENU1].append(
            CallbackQueryHandler(get_unit_micro_contents, pattern='^' + u['name'] + '$'))  # Update states

    reply_markup = InlineKeyboardMarkup(utils.build_menu(button_list, n_cols=2))

    bot.send_message(
        chat_id=query.message.chat_id,
        reply_to_message_id=query.message.message_id,
        text="Elige una unidad",
        reply_markup=reply_markup
    )

    return MENU1

# Metinlle "" ao parámetro received_text
def authenticate(update, context, received_text=""):
    try:
        if not context.user_data['auth_check']:  # If the user data fails the authentication this message is shown
            update.message.reply_text(received_text)
    except KeyError as e:
        pass
    update.message.reply_text("Introduce tu nombre de usuario: ")
    return AUTH

# Check if there is a User with the given username and it assigns the update.effective_user.id value to the telegram_id field in the Auth Server that is accessed via General Manager
def check_credentials(update, context):
    username = update.message.text    
    request_string = GENERAL_MANAGER_IP + "identification_telegram/" + username + "/" + str(update.effective_user.id)
    #update.message.reply_text(request_string) #DEBUG
    re = requests.get(request_string)
    #SEGUIR: no parece que legue a hacer correctamente el request.
    #update.message.reply_text(re.text) #DEBUG
    if re.status_code == 200:
        context.user_data['auth_check'] = True
        update.message.reply_text("Te has identificado correctamente.")
        update.message.reply_text("¡Bienvenido/a a InclusiBot! \n"
                                  "Comandos disponibles:\n\n"
                                  "/help - Muestra los comandos disponibles\n"
                                  "/menu - Muestra la lista de unidades\n"
                                  "/cancel - Cancela la conversación")

    else:
        context.user_data['auth_check'] = False
     #   update.message.reply_text('llegó'+re.text[0:20]+'aquí') #DEBUG
        authenticate(update, context, re.text)


# Initialize the conversation handler with the necessary states
def init_conv_handler():
    # Add entry points
    conv_handler.entry_points.append(CommandHandler('menu', get_units))
    conv_handler.entry_points.append(CommandHandler('auth', authenticate))
    # Add fallbacks
    conv_handler.fallbacks.append(CommandHandler('menu', get_units))
    # Add states
    conv_handler.states[AUTH] = [MessageHandler(Filters.text, check_credentials)]
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

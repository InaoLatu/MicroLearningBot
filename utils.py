# Author: Inao Latourrette Garcia
# Contact: inao.latourrette@gmail.com
# GitHub: https://github.com/InaoLatu
# LinkedIn: https://www.linkedin.com/in/inaolatourrette

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


# conv_handler = ConversationHandler(
#     entry_points=[CommandHandler('menu', menu1), CommandHandler('start', start)],
#
#     states={
#
#         MENU1: [CallbackQueryHandler(unit1, pattern='^jaa$'),
#                 CallbackQueryHandler(unit1, pattern='^asd$'),
#
#         MENU2: [CallbackQueryHandler(get_micro_content, pattern='^5$'),
#                 CallbackQueryHandler(get_micro_content, pattern='^4$'),
#                 CallbackQueryHandler(menu1_back, pattern='^back$')],
#
#         START_QUIZ: [CallbackQueryHandler(start_quiz, pattern='^yes$'),
#                      CallbackQueryHandler(menu1_back, pattern='^back$')],
#
#         Q2: [MessageHandler(Filters.text, q2)],  # Receives in the filter the answer for Q1
#
#         Q3: [MessageHandler(Filters.text, q3)],
#
#         END_QUIZ: [MessageHandler(Filters.text, end_quiz)],
#
#         RESULTS: [CallbackQueryHandler(show_wrong_answers, pattern='^wrong$'),
#                   CallbackQueryHandler(show_correct_answers, pattern='^correct$'),
#                   CallbackQueryHandler(show_all_answers, pattern='^all$'),
#                   CallbackQueryHandler(back_to_units, pattern='^back$')],
#
#     },
#
#     fallbacks=[CommandHandler('cancel', cancel), CommandHandler('help', help), CommandHandler('menu', menu1)]
# )
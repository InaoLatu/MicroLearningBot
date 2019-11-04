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
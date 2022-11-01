from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def start_keyboard(u) -> ReplyKeyboardMarkup:
    registered = hasattr(u, "student") and u.student

    if registered:
        buttons = [
            [KeyboardButton("/get_code")],
            [KeyboardButton("/share_code")],
            [KeyboardButton("/help")],
        ]
    else:
        buttons = [[KeyboardButton("/register")], [KeyboardButton("/help")]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def help_keyboard():
    buttons = [
        [KeyboardButton("/support")],
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def share_code_keyboard():
    buttons = [
        [KeyboardButton("/share_code")],
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# это нигде не юзается, но мб понадобится
def confirm_ticket_share():
    buttons = [[KeyboardButton("Да"), KeyboardButton("Нет")]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

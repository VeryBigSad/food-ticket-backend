from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.food_tickets.manage_data import CONFIRM_DECLINE_SHARE, CONFIRM_SHARE, DECLINE_SHARE
from tgbot.handlers.food_tickets.static_text import confirm_ticket_share, decline_ticket_share


def start_keyboard(registered=False) -> ReplyKeyboardMarkup:
    if registered:
        buttons = [
            [KeyboardButton('/get_code')],
            [KeyboardButton('/share_code')],
            [KeyboardButton('/help')]
        ]
    else:
        buttons = [
            [KeyboardButton('/register')],
            [KeyboardButton('/help')]
        ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def help_keyboard():
    buttons = [
        [KeyboardButton('/support')],
        [KeyboardButton('/back')]
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def share_code_keyboard():
    buttons = [
        [KeyboardButton('/share_code')],
        [KeyboardButton('/help')]
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

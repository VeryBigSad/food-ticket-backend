from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.food_tickets.manage_data import CONFIRM_DECLINE_SHARE, CONFIRM_SHARE, DECLINE_SHARE
from tgbot.handlers.food_tickets.static_text import confirm_ticket_share, decline_ticket_share


def start(registered=False) -> ReplyKeyboardMarkup:
    if registered:
        buttons = [
            [KeyboardButton('/get_code')],
            [KeyboardButton('/share_code')]
        ]
    else:
        buttons = [[
            KeyboardButton('/register')
        ]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
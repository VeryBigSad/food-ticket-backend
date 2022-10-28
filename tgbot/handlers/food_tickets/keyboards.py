from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.food_tickets.manage_data import CONFIRM_DECLINE_SHARE, CONFIRM_SHARE, DECLINE_SHARE
from tgbot.handlers.food_tickets.static_text import confirm_ticket_share, decline_ticket_share


def keyboard_confirm_decline_sharing(student_id: int) -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(confirm_ticket_share,
                             callback_data=f'{CONFIRM_DECLINE_SHARE}{CONFIRM_SHARE}{student_id}'),
        InlineKeyboardButton(decline_ticket_share,
                             callback_data=f'{CONFIRM_DECLINE_SHARE}{DECLINE_SHARE}{student_id}')
    ]]

    return InlineKeyboardMarkup(buttons)


def start() -> ReplyKeyboardMarkup:
    buttons = [[
        ReplyKeyboardMarkup('/register'),
        ReplyKeyboardMarkup('чзх')
    ]]

    return ReplyKeyboardMarkup(buttons)
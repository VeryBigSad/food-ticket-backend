
from functools import wraps
from typing import Callable

from food_tickets.models import Student
from tgbot.main import bot
from users.models import TelegramUser

SORRY_NOT_CONNECTED_ACCOUNT = 'Сорян, твой аккаунт не законечкен. Напиши /register <код, который тебе выдали>'


def registered_only(func: Callable):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        u, created = TelegramUser.get_user_and_created(update, context)
        if hasattr(u, 'student'):
            return func(update, context, *args, **kwargs)
        bot.send_message(chat_id=update.effective_message.chat_id, text=SORRY_NOT_CONNECTED_ACCOUNT)

    return command_func


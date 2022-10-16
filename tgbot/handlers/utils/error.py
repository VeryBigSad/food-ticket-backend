import logging
import traceback
import html

import telegram
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import TELEGRAM_LOGS_CHAT_ID
from users.models import TelegramUser


def send_stacktrace_to_tg_chat(update: Update, context: CallbackContext) -> None:
    u = TelegramUser.get_user(update, context)

    logging.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    user_message = """
😔 Сорян, внутри бота что-то сломалось(
Разработчики уже оповещены, и скоро этот баг пофиксят! Если у тебя что-то критичное, пиши в /support
"""
    komaru_panick_sticker = 'CAACAgIAAxkBAAIRi2NMbNZu0Gk6d3vqsmSYpMbzhhLeAALIEgACJkrRS7YUmvotbKiiKgQ'

    context.bot.send_sticker(chat_id=u.user_id, sticker=komaru_panick_sticker)
    context.bot.send_message(
        chat_id=u.user_id,
        text=user_message,
    )

    admin_message = f"⚠️⚠️⚠️ for {u.tg_str}:\n{message}"[:4090]
    if TELEGRAM_LOGS_CHAT_ID:
        context.bot.send_message(
            chat_id=TELEGRAM_LOGS_CHAT_ID,
            text=admin_message,
            parse_mode=telegram.ParseMode.HTML,
        )
    else:
        logging.error(admin_message)

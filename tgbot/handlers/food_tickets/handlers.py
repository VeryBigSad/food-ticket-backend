import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from food_tickets.models import Student
from tgbot.handlers.food_tickets import static_text
from tgbot.handlers.utils.decorators import registered_only
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import TelegramUser


@registered_only
def command_get_code(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_text(static_text.get_qr_code_success)


@registered_only
def command_share_code(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    cmd = update.message.text.split()

    # TODO: здесь чекнуть, что он сегодня еще не ел

    if len(cmd) != 2:
        update.message.reply_text(static_text.share_qr_code_usage)
        return

    tg_username = cmd[1][1:]
    share_to_account = TelegramUser.get_user_by_username_or_user_id(tg_username)
    if not share_to_account:
        update.message.reply_text(static_text.unknown_account_to_share_to)
        return

    # TODO: ... actually sharing ...

    update.message.reply_text(static_text.share_qr_code_success.format(telegram_account=share_to_account.tg_str))


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


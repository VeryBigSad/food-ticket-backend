import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from food_tickets.models import Student
from tgbot.handlers.onboarding import static_text, stickers
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import TelegramUser


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    if hasattr(u, 'student'):
        text = static_text.start_registered.format(first_name=u.student.first_name)
    else:
        text = static_text.start_not_registered

    update.message.reply_html(text=text)


def command_help(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_html(static_text.help_command)
    update.message.reply_sticker(stickers.KOMARU_PACK['DO_NOT_CARE'])


def command_support(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_html(static_text.support_command)


def command_register(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    if hasattr(u, 'student'):
        update.message.reply_html(static_text.register_already_done)
        return

    if len(update.message.text.split()) != 2:
        update.message.reply_text(static_text.register_command_usage)
        return
    else:
        code = update.message.text.split(' ')[1]
        student_obj = Student.objects.filter(secret_code=code)
        if student_obj.exists():
            student_obj = student_obj[0]
            text = static_text.register_successful.format(
                full_name=student_obj.full_name,
                date_of_birth=student_obj.date_of_birth
            )
            student_obj.telegram_account = u
            student_obj.save()
        else:
            text = static_text.register_code_bad
        update.message.reply_html(text)




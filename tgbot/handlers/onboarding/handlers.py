import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from food_tickets.models import Student
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import TelegramUser


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    update.message.reply_text(text=text)


def command_register(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

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
            text = static_text.register_failed
        update.message.reply_text(text)




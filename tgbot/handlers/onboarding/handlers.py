import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from food_tickets.models import Student
from tgbot.handlers.onboarding import static_text, stickers
from tgbot.handlers.utils.info import extract_user_data_from_update, send_typing_action
from users.models import TelegramUser
from tgbot.handlers.onboarding.keyboards import start_to_register


# KOMARU_STICKER_HELP_COMMAND = 'CAACAgIAAxkBAAEGHNxjTEiepf7K1JhAzOsiOSjfs02UtAAC5BcAApI90EslNSSrAZreXyoE'


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    if hasattr(u, 'student'):
        text = static_text.start_registered.format(first_name=u.student.first_name)
    else:
        text = static_text.start_not_registered

    # рот ебал этой блядской реплай клавиатуры пошла она нахуй
    update.message.reply_text(text=text, reply_markup=start_to_register)


@send_typing_action
def command_help(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_html(static_text.help_command)
    update.message.reply_sticker(stickers.KOMARU_PACK['DO_NOT_CARE'])


@send_typing_action
def command_support(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_html(static_text.support_command)


@send_typing_action
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
            if student_obj.telegram_account is not None:
                text = static_text.code_already_in_use
            else:
                text = static_text.register_successful.format(
                    full_name=student_obj.full_name,
                    date_of_birth=student_obj.date_of_birth,
                    grade=student_obj.grade
                )
                student_obj.telegram_account = u
                student_obj.save()
        else:
            text = static_text.register_code_bad
        update.message.reply_html(text)


def command_info(update: Update, context: CallbackContext) -> None:
    u = TelegramUser.get_user(update, context)
    if not (hasattr(u, 'student') and u.student is not None):
        update.message.reply_text(static_text.info_command_dont_know_you)
    else:
        last_time_eaten = u.student.foodticket_set.filter(foodaccesslog__isnull=False).order_by('-foodaccesslog__datetime_created').first()
        if last_time_eaten is None:
            last_time_eaten_text = static_text.you_have_not_eaten_yet
        else:
            last_time_eaten_text = f'{last_time_eaten.foodaccesslog.datetime_created.strftime("%d.%m.%Y %H:%M:%S")}, ' \
                                   f'{last_time_eaten.get_type_display()}'
        update.message.reply_html(static_text.info_command.format(
            full_name=u.student.full_name,
            grade=u.student.grade,
            date_of_birth=u.student.date_of_birth,
            last_time_eaten=last_time_eaten_text,
            has_food_right='есть🎉' if u.student.has_food_right else 'нет'
        ))

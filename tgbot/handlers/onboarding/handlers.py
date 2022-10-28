from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from food_tickets.models import Student
from tgbot.handlers.onboarding import static_text
from tgbot import stickers
from tgbot.handlers.utils.info import send_typing_action
from users.models import TelegramUser
from tgbot.handlers.onboarding.keyboards import start_keyboard, help_keyboard
import tgbot.handlers.conversations.states_constants as states


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    if hasattr(u, "student") and u.student:
        text = static_text.start_registered.format(first_name=u.student.first_name)
    else:
        text = static_text.start_not_registered

    update.message.reply_html(text=text, reply_markup=start_keyboard(u))


def command_wait(update: Update, context: CallbackContext) -> int:
    u, created = TelegramUser.get_user_and_created(update, context)

    update.message.reply_html(text=static_text.wait, reply_markup=start_keyboard(u))
    update.message.reply_sticker(stickers.KOMARU_PACK["WHAT_TO_DO"])
    return ConversationHandler.END


@send_typing_action
def command_help(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_text(
        static_text.help_command, reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_sticker(stickers.KOMARU_PACK["1000_WORDS"])


@send_typing_action
def command_support(update: Update, context: CallbackContext) -> int:
    u, created = TelegramUser.get_user_and_created(update, context)
    update.message.reply_html(
        static_text.support_command, reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_sticker(stickers.KOMARU_PACK["TELL_MORE"])

    return states.GET_REPORT


@send_typing_action
def get_report(update: Update, context: CallbackContext) -> int:
    # тут потом надо будет сделать штуку, которая отправляет отчёт админам
    u = TelegramUser.get_user(update, context)

    update.message.reply_html(static_text.got_report)
    update.message.reply_sticker(
        stickers.KOMARU_PACK["ADMIN_WORKING"], reply_markup=start_keyboard(u)
    )

    return ConversationHandler.END


@send_typing_action
def command_register(update: Update, context: CallbackContext) -> int:
    u, created = TelegramUser.get_user_and_created(update, context)

    if hasattr(u, "student"):
        update.message.reply_html(static_text.register_already_done)
        return ConversationHandler.END

    # TODO: переделать на conversation
    # context.chat_data['register'] = True
    update.message.reply_html(
        static_text.register_in_process, reply_markup=ReplyKeyboardRemove()
    )
    return states.GET_USERNAME


def register(update: Update, context: CallbackContext):
    u = TelegramUser.get_user(update, context)
    code = update.message.text

    successful = False
    registered = False

    student_obj = Student.objects.filter(secret_code=code)
    if student_obj.exists():
        student_obj = student_obj[0]
        if student_obj.telegram_account is not None:
            text = static_text.code_already_in_use
            registered = True
        else:
            student_obj.telegram_account = u
            student_obj.save()

            text = static_text.register_successful.format(
                full_name=student_obj.full_name,
                date_of_birth=student_obj.date_of_birth,
                grade=student_obj.grade,
            )
            successful = True
            registered = True
    else:
        text = static_text.register_code_bad

    update.message.reply_html(text)

    if successful:
        update.message.reply_sticker(stickers.KOMARU_PACK["SYNCHRONIZATION"])

    if registered:
        return ConversationHandler.END
    else:
        return 0


def handle_unknown(update: Update, context: CallbackContext) -> None:
    text = static_text.unknown_command
    update.message.reply_text(text)


def command_info(update: Update, context: CallbackContext) -> None:
    u = TelegramUser.get_user(update, context)
    if not (hasattr(u, "student") and u.student is not None):
        update.message.reply_text(static_text.info_command_dont_know_you)
    else:
        last_time_eaten = (
            u.student.foodticket_set.filter(foodaccesslog__isnull=False)
            .order_by("-foodaccesslog__datetime_created")
            .first()
        )
        if last_time_eaten is None:
            last_time_eaten_text = static_text.you_have_not_eaten_yet
        else:
            last_time_eaten_text = (
                f'{last_time_eaten.foodaccesslog.datetime_created.strftime("%d.%m.%Y %H:%M:%S")}, '
                f"{last_time_eaten.get_type_display()}"
            )
        update.message.reply_html(
            static_text.info_command.format(
                full_name=u.student.full_name,
                grade=u.student.grade,
                date_of_birth=u.student.date_of_birth,
                last_time_eaten=last_time_eaten_text,
                has_food_right="есть🎉" if u.student.has_food_right else "нет",
            )
        )

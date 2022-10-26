from telegram import Update
from telegram.ext import CallbackContext

from food_tickets.models import Student
from tgbot.handlers.food_tickets.exceptions import CodeAlreadyUsed, WrongCodeException
from tgbot.handlers.onboarding import static_text
from users.models import TelegramUser


def handle_message(update: Update, context: CallbackContext) -> None:
    u = TelegramUser.get_user(update, context)

    if context.chat_data.get('register'):
        code = update.message.text

        try:
            student_obj = register(code, u)

            text = static_text.register_successful.format(
                full_name=student_obj.full_name,
                date_of_birth=student_obj.date_of_birth,
                grade=student_obj.grade
            )
        except CodeAlreadyUsed:
            text = static_text.code_already_in_use
        except WrongCodeException:
            text = static_text.register_code_bad

        context.chat_data['register'] = False
    else:
        text = static_text.unknown_command

    update.message.reply_html(text)


def register(code: str, u):
    student_obj = Student.objects.filter(secret_code=code)
    if student_obj.exists():
        student_obj = student_obj[0]
        if student_obj.telegram_account is not None:
            raise CodeAlreadyUsed
        else:
            student_obj.telegram_account = u
            student_obj.save()
            return student_obj
    else:
        raise WrongCodeException

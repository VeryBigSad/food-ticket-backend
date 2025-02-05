import datetime
from typing import Tuple

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import tgbot.handlers.conversations.states_constants as states
import tgbot.handlers.onboarding.keyboards as keyboards
from dtb.settings import EXPIRATION_TIME
from food_tickets.models import Student, FoodTicket
from tgbot.handlers.food_tickets import static_text
from tgbot.handlers.food_tickets.exceptions import (
    NoFoodRightException,
    RightAlreadyExecutedException,
)
from tgbot.handlers.food_tickets.keyboards import keyboard_confirm_decline_sharing
from tgbot.handlers.food_tickets.manage_data import (
    CONFIRM_DECLINE_SHARE,
    DECLINE_SHARE,
    CONFIRM_SHARE,
)
from tgbot.handlers.food_tickets.qr_codes import generate_qr
from tgbot.handlers.food_tickets.utils import get_ft_type_by_time
from tgbot.handlers.utils.decorators import registered_only
from tgbot.handlers.utils.info import send_typing_action
from tgbot.main import bot
from users.models import TelegramUser


def create_or_get_existing_ticket(
        sponsor: Student, owner: Student
) -> Tuple[FoodTicket, bool]:
    """creates a food ticket for a student (if he has the rights to do so) or gets him one he already has"""

    ticket_type = get_ft_type_by_time(datetime.datetime.now())
    date_usable_at = datetime.date.today()

    # get the ticket that we are going to pass on
    existing_ticket = FoodTicket.objects.filter(
        ticket_sponsor=sponsor,
        owner=owner,
        type=ticket_type,
        date_usable_at=date_usable_at,
        foodaccesslog__isnull=True,
    ).first()
    if existing_ticket is not None:
        return existing_ticket, False

    if not sponsor.has_food_right:
        raise NoFoodRightException

    ft = FoodTicket.objects.filter(
        ticket_sponsor=sponsor, type=ticket_type, date_usable_at=date_usable_at
    )
    if ft.exists():
        raise RightAlreadyExecutedException(ft.first())

    new_food_ticket = FoodTicket(
        owner=owner,
        type=ticket_type,
        ticket_sponsor=sponsor,
        date_usable_at=date_usable_at,
    )
    new_food_ticket.save()
    return new_food_ticket, True


@send_typing_action
@registered_only
def command_get_code(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    # TODO: make an "accept" plaque, so that it doesn't insta send the ticket,
    #  but rather asks do are you sure you wanna do that
    #  same for command_share_code()
    #  it'd delete the confirmation message after you say yes/no

    try:
        ticket, is_new = create_or_get_existing_ticket(
            sponsor=u.student, owner=u.student
        )
    except RightAlreadyExecutedException as e:
        t = e.ticket
        if t.owner == u.student:
            # сказать что ты уже пожрал
            update.message.reply_text(
                static_text.you_already_used_food_ticket.format(id=t.id)
            )
        else:
            # сказать что ты его отдал
            update.message.reply_text(
                static_text.you_gave_food_ticket_away.format(
                    id=t.id, owner=t.owner.first_name
                )
            )
        return
    except NoFoodRightException:
        update.message.reply_text(static_text.no_food_right)
        return
    text = static_text.get_qr_code_success

    expire_time = datetime.datetime.now() + EXPIRATION_TIME
    qr = generate_qr(expire_time, ticket.owner.id)

    update.message.reply_text(text)
    update.message.reply_photo(photo=qr, reply_markup=keyboards.share_code_keyboard())


@send_typing_action
@registered_only
def start_share(update: Update, context: CallbackContext) -> int:
    u = TelegramUser.get_user(update, context)
    ft_type = get_ft_type_by_time(datetime.datetime.now())

    # checking whether we can create a code
    if (
            not u.student.can_create_ticket_for_today
            and u.student.get_ticket_for_today(ft_type=ft_type) is None
    ):
        update.message.reply_text(static_text.no_food_right_and_no_ticket)
        return ConversationHandler.END

    text = static_text.share_qr_code_usage
    update.message.reply_html(text)
    return states.GET_USER_TO_SHARE


@send_typing_action
@registered_only
def command_share_code(update: Update, context: CallbackContext) -> int:
    u, created = TelegramUser.get_user_and_created(update, context)

    tg_username = update.message.text
    share_to_account = TelegramUser.get_user_by_username_or_user_id(tg_username)
    if not share_to_account:
        update.message.reply_text(
            static_text.unknown_account_to_share_to.format(username=tg_username)
        )
        return states.GET_USER_TO_SHARE
    if not hasattr(share_to_account, "student"):
        update.message.reply_text(
            static_text.account_share_to_not_registered.format(
                username=share_to_account.tg_str
            )
        )
        return ConversationHandler.END

    share_to_student = share_to_account.student
    ft_type = get_ft_type_by_time(datetime.datetime.now())

    # checking whether the share_to_student can get the ticket
    if share_to_student.get_ticket_for_today(ft_type=ft_type):
        # the student we are trying to share with already has a ticket, ignore the fucker
        update.message.reply_text(
            static_text.share_to_student_already_has_a_ticket.format(
                first_name=share_to_student.first_name, ft_type=ft_type
            )
        )
        return ConversationHandler.END
    if share_to_student.can_create_ticket_for_today:
        # the student we are trying to share with can create his own ticket, ignore the fucker
        update.message.reply_text(static_text.share_to_student_can_create_a_ticket)
        return ConversationHandler.END

    # logic here
    # if user has a ticket himself AND no right, ask him whether he wants to give away the current

    if u.student.can_create_ticket_for_today:
        update.message.reply_text(
            static_text.you_sure_you_want_to_create_ticket_and_share_it.format(
                ft_type=ft_type, first_name=share_to_student.first_name
            ),
            reply_markup=keyboard_confirm_decline_sharing(
                student_id=share_to_student.id
            ),
        )
        return ConversationHandler.END
    else:
        ticket = u.student.get_ticket_for_today(ft_type=ft_type)
        update.message.reply_text(
            static_text.you_sure_you_want_to_giveaway_your_ticket.format(
                ft_type=ft_type,
                first_name=share_to_student.first_name,
                usable_at_date=ticket.date_usable_at,
            ),
            reply_markup=keyboard_confirm_decline_sharing(
                student_id=share_to_student.id
            ),
        )
        return ConversationHandler.END


@send_typing_action
def share_callback_handler(update: Update, context: CallbackContext) -> None:
    u = TelegramUser.get_user(update, context)

    data = update.callback_query.data
    data = data.replace(CONFIRM_DECLINE_SHARE, "")
    update.callback_query.message.delete()

    if DECLINE_SHARE in data:
        update.callback_query.answer("Окей! Отменили действие")
        return

    update.callback_query.answer()
    data = data.replace(CONFIRM_SHARE, "")
    share_to_student = Student.objects.get(id=int(data))

    food_ticket = u.student.get_ticket_for_today(
        ft_type=get_ft_type_by_time(datetime.datetime.now())
    )
    if food_ticket is not None:
        food_ticket.owner = share_to_student
        food_ticket.save()
    else:
        food_ticket, is_new = create_or_get_existing_ticket(
            sponsor=u.student, owner=share_to_student
        )

    bot.send_message(
        chat_id=share_to_student.telegram_account.user_id,
        text=static_text.someone_shared_ticket_with_you.format(
            first_name=u.student.first_name,
            type=food_ticket.get_type_display(),
            date_usable_at=food_ticket.date_usable_at,
        ),
    )

    bot.send_message(
        chat_id=u.user_id,
        text=static_text.share_qr_code_success.format(
            telegram_account=share_to_student.telegram_account.tg_str
        ),
    )

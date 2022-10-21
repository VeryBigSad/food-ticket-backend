import datetime
from typing import Tuple

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from food_tickets.models import Student, FoodTicket
from tgbot.handlers.food_tickets import static_text
from tgbot.handlers.food_tickets.exceptions import NoFoodRightException, RightAlreadyExecutedException
from tgbot.handlers.food_tickets.keyboards import keyboard_confirm_decline_sharing
from tgbot.handlers.food_tickets.manage_data import CONFIRM_DECLINE_SHARE, DECLINE_SHARE, CONFIRM_SHARE
from tgbot.handlers.food_tickets.utils import get_ft_type_by_time
from tgbot.handlers.utils.decorators import registered_only
from tgbot.handlers.utils.info import extract_user_data_from_update, send_typing_action
from tgbot.main import bot
from users.models import TelegramUser


def create_or_get_existing_ticket(sponsor: Student, owner: Student) -> Tuple[FoodTicket, bool]:
    """ creates a food ticket for a student (if he has the rights to do so) or gets him one he already has """

    ticket_type = get_ft_type_by_time(datetime.datetime.now())
    date_usable_at = datetime.date.today()

    # get the ticket that we are going to pass on
    existing_ticket = FoodTicket.objects.filter(
        ticket_sponsor=sponsor, owner=owner, type=ticket_type, date_usable_at=date_usable_at, foodaccesslog__isnull=True
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

    new_food_ticket = FoodTicket(owner=owner, type=ticket_type, ticket_sponsor=sponsor, date_usable_at=date_usable_at)
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
        ticket, is_new = create_or_get_existing_ticket(sponsor=u.student, owner=u.student)
    except RightAlreadyExecutedException as e:
        t = e.ticket
        if t.owner == u.student:
            # сказать что ты уже пожрал
            update.message.reply_text(static_text.you_already_used_food_ticket.format(id=t.id))
        else:
            # сказать что ты его отдал
            update.message.reply_text(static_text.you_gave_food_ticket_away.format(id=t.id, owner=t.owner.first_name))
        return
    except NoFoodRightException:
        update.message.reply_text(static_text.no_food_right)
        return
    text = static_text.get_qr_code_success.format(
        id=ticket.id, type=ticket.type, date_usable_at=ticket.date_usable_at,
        owner=ticket.owner, sponsor=ticket.ticket_sponsor
    )

    # maybe use the is_new info to tell the dude that it's the same token?
    update.message.reply_text(text)


@send_typing_action
@registered_only
def command_share_code(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)
    args = update.message.text.split()

    if len(args) != 2:
        update.message.reply_text(static_text.share_qr_code_usage)
        return

    tg_username = args[1]
    share_to_account = TelegramUser.get_user_by_username_or_user_id(tg_username)
    if not share_to_account:
        update.message.reply_text(static_text.unknown_account_to_share_to.format(username=tg_username))
        return
    if not hasattr(share_to_account, 'student'):
        update.message.reply_text(static_text.account_share_to_not_registered.format(username=share_to_account.tg_str))
        return

    share_to_student = share_to_account.student
    ft_type = get_ft_type_by_time(datetime.datetime.now())

    # checking whether we can create a code
    print(u.student.can_create_ticket_for_today)
    print(u.student.get_ticket_for_today(ft_type=ft_type))
    if not u.student.can_create_ticket_for_today and u.student.get_ticket_for_today(ft_type=ft_type) is None:
        update.message.reply_text(static_text.no_food_right_and_no_ticket)
        return

    # checking whether the share_to_student can get the ticket
    if share_to_student.get_ticket_for_today(ft_type=ft_type):
        # the student we are trying to share with already has a ticket, ignore the fucker
        update.message.reply_text(static_text.share_to_student_already_has_a_ticket.format(
            first_name=share_to_student.first_name,
            ft_type=ft_type
        ))
        return
    if share_to_student.can_create_ticket_for_today:
        # the student we are trying to share with can create his own ticket, ignore the fucker
        update.message.reply_text(static_text.share_to_student_can_create_a_ticket)
        return

    # logic here
    # if user has a ticket himself AND no right, ask him whether he wants to give away the current

    if u.student.can_create_ticket_for_today:
        update.message.reply_text(static_text.you_sure_you_want_to_create_ticket_and_share_it.format(
            ft_type=ft_type, first_name=share_to_student.first_name
        ), reply_markup=keyboard_confirm_decline_sharing(student_id=share_to_student.id))
        return
    else:
        ticket = u.student.get_ticket_for_today(ft_type=ft_type)
        update.message.reply_text(static_text.you_sure_you_want_to_giveaway_your_ticket.format(
            ft_type=ft_type, first_name=share_to_student.first_name, usable_at_date=ticket.date_usable_at
        ), reply_markup=keyboard_confirm_decline_sharing(student_id=share_to_student.id))
        return


@send_typing_action
def share_callback_handler(update: Update, context: CallbackContext) -> None:
    u = TelegramUser.get_user(update, context)

    data = update.callback_query.data
    data = data.replace(CONFIRM_DECLINE_SHARE, '')
    update.callback_query.message.delete()
    if DECLINE_SHARE in data:
        update.callback_query.answer('Окей! Отменили действие')
        return
    update.callback_query.answer()
    data = data.replace(CONFIRM_SHARE, '')
    share_to_student = Student.objects.get(id=int(data))

    food_ticket = u.student.get_ticket_for_today(ft_type=get_ft_type_by_time(datetime.datetime.now()))
    if food_ticket is not None:
        food_ticket.owner = share_to_student
        food_ticket.save()
    else:
        food_ticket, is_new = create_or_get_existing_ticket(sponsor=u.student, owner=share_to_student)

    bot.send_message(chat_id=share_to_student.telegram_account.user_id, text=static_text.someone_shared_ticket_with_you.format(
        first_name=u.student.first_name,
        type=food_ticket.type,
        date_usable_at=food_ticket.date_usable_at
    ))

    bot.send_message(chat_id=u.user_id, text=static_text.share_qr_code_success.format(
        telegram_account=share_to_student.telegram_account.tg_str
    ))


def command_info(update: Update, context: CallbackContext) -> None:
    # TODO: сюда вставить инфу о челе
    #  типа фио дата рождения класс has_food_right когда последние пару раз ел
    pass

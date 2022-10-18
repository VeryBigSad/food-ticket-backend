import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from food_tickets.models import Student, FoodTicket
from tgbot.handlers.food_tickets import static_text
from tgbot.handlers.food_tickets.exceptions import NoFoodRightException, TicketExistsException
from tgbot.handlers.utils.decorators import registered_only
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import TelegramUser


def create_or_get_existing_ticket(student: Student) -> FoodTicket:
    """ creates a food ticket for a student, if he has the rights to do so """
    if not student.has_food_right:
        raise NoFoodRightException

    # not found, creating one
    end_of_today = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    ticket_type = 'breakfast' if datetime.datetime.now().time() < FoodTicket.BREAKFAST_END_TIME else 'lunch'
    # checking for existing ticket by same sponsor
    expiry_date = end_of_today if ticket_type == 'lunch' else FoodTicket.BREAKFAST_END_TIME
    possible_current_ticket = FoodTicket.objects.filter(ticket_sponsor=student, type=ticket_type, expiry_date=expiry_date).first()
    if possible_current_ticket:
        # if it exists & not used & owner is the student himself,
        # give it to him. otherwise we whine about him being a bitch
        if not hasattr(possible_current_ticket, 'foodaccesslog') and possible_current_ticket.owner == student:
            return possible_current_ticket
        else:
            raise TicketExistsException(possible_current_ticket)

    new_food_ticket = FoodTicket(owner=student, type=ticket_type, ticket_sponsor=student, expiry_date=expiry_date)
    new_food_ticket.save()
    return new_food_ticket


@registered_only
def command_get_code(update: Update, context: CallbackContext) -> None:
    u, created = TelegramUser.get_user_and_created(update, context)

    if not u.student.has_food_right:
        update.message.reply_text(static_text.no_food_right)
        return
    try:
        ticket = create_or_get_existing_ticket(u.student)
    except TicketExistsException as e:
        t = e.ticket
        if t.owner == u.student:
            # сказать что ты уже пожрал
            update.message.reply_text(static_text.you_already_used_food_ticket.format(id=t.id))
        else:
            # сказать что ты его отдал
            update.message.reply_text(static_text.you_gave_food_ticket_away.format(id=t.id, owner=t.owner.first_name))
        return

    update.message.reply_text(static_text.get_qr_code_success.format(
        id=ticket.id, type=ticket.type, expiry_date=ticket.expiry_date, owner=ticket.owner
    ))

    # checking for existing owned tickets
    # possible_existing_ticket = u.student.foodticket_set.filter(expiry_date__gt=datetime.datetime.now(),
    #                                                          foodaccesslog__isnull=True).first()
    # if possible_existing_ticket:
    #     # TODO: also check for the ticket type
    #     # setting it for the owner to own
    #     possible_existing_ticket.owner = u.student
    #     possible_existing_ticket.save()
    #     return possible_existing_ticket




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


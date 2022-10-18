from food_tickets.models import FoodTicket


class NoFoodRightException(Exception):
    pass


class TicketExistsException(Exception):
    def __init__(self, existing_ticket_object: FoodTicket):
        self.ticket = existing_ticket_object


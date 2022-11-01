import datetime

from food_tickets.models import FoodTicket


def get_ft_type_by_time(datetime_obj: datetime.datetime):
    return (
        "breakfast" if datetime_obj.time() < FoodTicket.BREAKFAST_END_TIME else "lunch"
    )

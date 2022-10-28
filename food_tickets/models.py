import datetime

from django.db import models

from food_tickets.managers import FoodTicketManager, FoodAccessLogManager
from food_tickets.utils import random_secret_code
from utils.models import nb


class Student(models.Model):
    full_name = models.CharField(max_length=256)  # ФИО
    date_of_birth = models.CharField(max_length=256)

    grade = models.CharField(max_length=8, **nb)  # 8А, 11Б

    # мб переделать штуку с secret_code на что-то получше, хотя бы каждую неделю/месяц их обновлять чтобы не крали коды?
    secret_code = models.CharField(max_length=256, default=random_secret_code, **nb)
    telegram_account = models.OneToOneField(
        "users.TelegramUser", on_delete=models.CASCADE, **nb
    )

    has_food_right = models.BooleanField(
        "Есть ли право на еду (он льготник/платит за нее?)", default=False
    )

    @property
    def first_name(self):
        if len(self.full_name.split()) >= 2:
            return self.full_name.split()[1]
        return self.full_name

    @property
    def can_create_ticket_for_today(self):
        """returns whether he can create a code rn"""

        from tgbot.handlers.food_tickets.utils import get_ft_type_by_time

        ft_type = get_ft_type_by_time(datetime.datetime.today())
        if (
            self.has_food_right
            and not FoodTicket.objects.filter(
                ticket_sponsor=self, date_usable_at=datetime.date.today(), type=ft_type
            ).exists()
        ):
            return True
        return False

    def get_ticket_for_today(self, ft_type):
        try:
            return FoodTicket.objects.get_existing_ticket(
                date=datetime.date.today(), ft_type=ft_type, student=self
            )
        except FoodTicket.DoesNotExist:
            return None

    def __str__(self):
        return self.full_name


class FoodTicket(models.Model):

    # Можно завтракать ток после 1 пары, т.е. с 10 40 до 11 00,
    # ставим некоторый запас + если кто-то пришел пораньше, пусть обедают
    BREAKFAST_END_TIME = datetime.time(hour=11, minute=25)

    TYPE_CHOICE = (("breakfast", "Завтрак"), ("lunch", "Обед"))

    ticket_sponsor = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name="Спонсор тикета"
    )
    time_created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        Student,
        related_name="foodticket_owner",
        on_delete=models.CASCADE,
        verbose_name="Пользователь тикета",
    )
    date_usable_at = models.DateField("День, когда этот тикет можно использовать")
    type = models.CharField("Тип тикета", max_length=16, choices=TYPE_CHOICE)

    objects = FoodTicketManager()

    @property
    def is_available(self):
        """returns whether the ticket had been used or not"""
        if (
            hasattr(self, "foodaccesslog") and self.foodaccesslog is not None
        ) or self.date_usable_at != datetime.date.today():
            return False
        return True


class FoodAccessLog(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    food_ticket = models.OneToOneField(FoodTicket, on_delete=models.CASCADE)

    objects = FoodAccessLogManager()

    @property
    def eater(self):
        return self.food_ticket.owner

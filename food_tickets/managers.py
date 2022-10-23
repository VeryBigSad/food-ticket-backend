import datetime

from django.db import models


class FoodTicketManager(models.Manager):
    def get_existing_ticket(self, student, ft_type: str, date: datetime.date):
        return self.get_queryset().filter(
            owner=student, foodaccesslog__isnull=True,
            type=ft_type, date_usable_at=date
        ).first()


class FoodAccessLogManager(models.Manager):
    pass

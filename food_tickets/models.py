from django.db import models

from food_tickets.utils import random_secret_code
from users.models import TelegramUser


class Student(models.Model):
    full_name = models.CharField(max_length=256)  # ФИО
    date_of_birth = models.CharField(max_length=256)

    grade = models.CharField(max_length=8)  # 8А, 11Б

    secret_code = models.CharField(max_length=256, default=random_secret_code)

    telegram_account = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)


class FoodAccessLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

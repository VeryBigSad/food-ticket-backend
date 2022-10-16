from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from dtb.settings import DEBUG

from .models import Student, FoodAccessLog


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'date_of_birth', 'grade', 'secret_code', 'telegram_account',
    ]
    search_fields = ('full_name', 'telegram_account')


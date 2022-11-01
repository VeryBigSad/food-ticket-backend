import datetime
import os

import pandas as pd
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.urls import path, reverse

from .forms import UploadExcelForm
from .models import Student, FoodAccessLog, FoodTicket
from .tasks import excel_update
from .utils import parse_excel_file


@admin.action(description='Экспортировать секретные коды в Excel')
def export_codes(modeladmin, request, queryset: QuerySet):
    """ returns Excel file with secret_codes for students in queryset """
    keys = ['full_name', 'grade', 'secret_code']
    pretty_keys = {'full_name': 'ФИО', 'grade': 'Класс', 'secret_code': 'Код'}
    students = list(queryset.all().values(*keys))
    data = {pretty_keys[k]: [data_dict[k] for data_dict in students] for k in keys}
    df = pd.DataFrame(data)
    file_path = f'{len(students)} кодов, {datetime.date.today()}.xlsx'
    df.to_excel(file_path, index=False)
    resp = FileResponse(open(file_path, 'rb'))
    os.remove(file_path)
    return resp


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'grade', 'secret_code', 'telegram_account', 'has_food_right',
    ]
    list_filter = ['has_food_right', 'grade']
    search_fields = ('full_name', 'telegram_account')
    sortable_by = ('has_food_right', 'grade')
    actions = [export_codes]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.upload_excel),
        ]
        return my_urls + urls

    def upload_excel(self, request):
        # TODO: add docstring
        """ Creates/updates students based on whether they can eat or not FROM EXCEL FILE"""
        if request.POST:
            form = UploadExcelForm(request.POST, request.FILES)
            if form.is_valid():
                # can't send the file via celery so processing it here
                # probably should save it AND send to celery the path but ehhh who cares
                # it will probably work regardless
                student_list = parse_excel_file(request.FILES['file'])
                excel_update.delay(student_list)
                messages.add_message(request, messages.INFO, 'Процесс импортирования через excel запущен! '
                                                             'Попробуйте перезагрузить страницу и вы увидите результат')
                return HttpResponseRedirect(reverse('admin:food_tickets_student_changelist'))
        else:
            form = UploadExcelForm()
            return render(
                request, "admin/upload_excel_form.html", {'form': form, 'title': u'Загрузить файл питания excel'}
            )


@admin.register(FoodTicket)
class FoodTicketAdmin(admin.ModelAdmin):
    list_display = [
        "owner",
        "ticket_sponsor",
        "date_usable_at",
        "type",
        "time_created_at",
    ]
    search_fields = ("owner", "ticket_sponsor")
    sortable_by = (
        "ticket_sponsor",
        "owner",
        "date_usable_at",
        "type",
        "time_created_at",
    )


@admin.register(FoodAccessLog)
class FoodAccessLogAdmin(admin.ModelAdmin):
    list_display = [
        "datetime_created",
        "eater",
        "food_ticket",
    ]
    sortable_by = ("time",)
    search_fields = ("food_ticket",)

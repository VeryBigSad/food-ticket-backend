from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from .forms import UploadExcelForm
from .models import Student, FoodAccessLog, FoodTicket
from .utils import parse_excel_file


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'grade', 'secret_code', 'telegram_account', 'has_food_right',
    ]
    list_filter = ['has_food_right', 'grade']
    search_fields = ('full_name', 'telegram_account')
    sortable_by = ('has_food_right', 'grade')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.upload_excel),
        ]
        return my_urls + urls

    def upload_excel(self, request):
        # TODO: add docstring
        """"""
        if request.POST:
            form = UploadExcelForm(request.POST, request.FILES)
            if form.is_valid():
                # TODO: transfer this to celery & notify people that they got the right to eat this week
                student_list = parse_excel_file(request.FILES['file'])
                Student.objects.all().update(has_food_right=False)
                for i in student_list:
                    Student.objects.update_or_create(full_name=i[0], grade=i[1], defaults={'has_food_right': True})
            return HttpResponseRedirect(request.get_full_path())
        else:
            form = UploadExcelForm()
            return render(
                request, "admin/upload_excel_form.html", {'form': form, 'title': u'Загрузить файл питания excel'}
            )


@admin.register(FoodTicket)
class FoodTicketAdmin(admin.ModelAdmin):
    list_display = [
        'owner', 'ticket_sponsor', 'date_usable_at', 'type', 'time_created_at'
    ]
    search_fields = ('owner', 'ticket_sponsor')
    sortable_by = ('ticket_sponsor', 'owner', 'date_usable_at', 'type', 'time_created_at')


@admin.register(FoodAccessLog)
class FoodAccessLogAdmin(admin.ModelAdmin):
    list_display = [
        'datetime_created', 'eater', 'food_ticket',
    ]
    sortable_by = ('time',)
    search_fields = ('food_ticket',)

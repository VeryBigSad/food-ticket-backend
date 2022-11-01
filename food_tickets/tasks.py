from dtb.celery import app
from food_tickets.models import Student


@app.task(ignore_result=True)
def excel_update(student_list):
    Student.objects.all().update(has_food_right=False)
    for i in student_list:
        Student.objects.update_or_create(full_name=i[0], grade=i[1], defaults={'has_food_right': True})

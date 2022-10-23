from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/food-access-log', views.FoodAccessLogCreate.as_view())
]

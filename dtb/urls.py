import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("tgadmin/", admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
    path("", include("food_tickets.urls")),
    path("", views.index, name="index"),
    path("super_secter_webhook/", csrf_exempt(views.TelegramBotWebhookView.as_view())),
]

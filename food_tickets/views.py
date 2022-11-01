from rest_framework import generics
from rest_framework.response import Response

from dtb import settings
from food_tickets.models import FoodAccessLog
from food_tickets.serializers import FoodAccessLogSerializer


class FoodAccessLogCreate(generics.CreateAPIView):
    queryset = FoodAccessLog.objects.all()
    serializer_class = FoodAccessLogSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get("secret_key") != settings.API_SECRET_KEY:
            return Response({"error": "Bad password"})
        return super().post(request, *args, **kwargs)

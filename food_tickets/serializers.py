from rest_framework import serializers

from food_tickets.models import FoodAccessLog


class FoodAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAccessLog
        fields = [
            "id",
            "datetime_created",
            "food_ticket",
        ]

from rest_framework import serializers
from .models import Booking
from datetime import timedelta, datetime
from django.db import transaction
from apps.users.models import Client

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "client",
            "service",
            "date",
            "start_time",
            "end_time",
            "status",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "client",
            "status",
            "total_price",
            "end_time",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            cosmetologist = Client.objects.select_for_update().get(
                role=Client.Role.COSMETOLOGIST,
            )
            service = validated_data["service"]
            cost = service.cost
            duration_minutes = service.duration_minutes
            start_time = validated_data["start_time"]
            date = validated_data["date"]
            start_datetime = datetime.combine(date, start_time)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            end_time = end_datetime.time()
            conflicting_bookings = Booking.objects.filter(
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exclude(
                status__in=[
                    Booking.Status.CANCELLED,
                ]
            )

            if conflicting_bookings.exists():
                raise serializers.ValidationError(
                    "Conflict with another booking"
                )
            validated_data.update({
                "total_price": cost,
                "end_time": end_time,
            })
            booking = Booking.objects.create(**validated_data)

            return booking

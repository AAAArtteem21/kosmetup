from rest_framework import serializers
from .models import Booking
from datetime import timedelta, datetime
from django.db import transaction
from apps.users.models import Client
from django.utils import timezone
from apps.schedule.models import Schedule, ScheduleException


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
            duration_minutes = service.duration_minutes
            start_time = validated_data["start_time"]
            date = validated_data["date"]
            start_datetime = datetime.combine(date, start_time)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            end_time = end_datetime.time()
            exception = ScheduleException.objects.filter(date=date).first()

            if exception:
                if exception.is_day_off:
                    raise serializers.ValidationError(
                        "Cosmetologist does not work on this date."
                    )

                working_intervals = [
                    (exception.start_time, exception.end_time)
                ]
            else:
                working_intervals = list(
                    Schedule.objects.filter(
                        weekday=date.weekday(),
                        is_active=True
                    ).values_list("start_time", "end_time")
                )

            if not any(
                working_start <= start_time and end_time <= working_end
                for working_start, working_end in working_intervals
            ):
                raise serializers.ValidationError(
                    "Booking time is outside working hours."
                )
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
                "total_price": service.cost,
                "end_time": end_time,
            })
            booking = Booking.objects.create(**validated_data)

            return booking

    def validate_service(self, service):
        if not service.is_active:
            raise serializers.ValidationError(
                "This service is inactive."
            )
        return service

    def validate(self, attrs):
        date = attrs.get("date")
        start_time = attrs.get("start_time")

        if date < timezone.localdate():
            raise serializers.ValidationError({
                "date": "Cannot book a date in the past."
            })

        if date == timezone.localdate():
            if start_time <= timezone.localtime().time():
                raise serializers.ValidationError({
                    "start_time": "Cannot book a time in the past."
                })

        return attrs

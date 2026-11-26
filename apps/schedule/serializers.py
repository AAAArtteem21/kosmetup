from rest_framework import serializers
from .models import Schedule, ScheduleException
from rest_framework.exceptions import ValidationError
from django.utils import timezone


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = [
            "id",
            "weekday",
            "start_time",
            "end_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_time = attrs.get(
            "start_time",
            self.instance.start_time if self.instance else None
        )

        end_time = attrs.get(
            "end_time",
            self.instance.end_time if self.instance else None
        )

        if start_time is not None and end_time is not None:
            if end_time <= start_time:
                raise serializers.ValidationError(
                    "End time must be later than start time."
                )

        is_active = attrs.get(
            "is_active",
            self.instance.is_active if self.instance else True
        )

        existing = Schedule.objects.filter(
            weekday=attrs.get("weekday", self.instance.weekday if self.instance else None),
            is_active=True,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if is_active:
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    "Time is conflicting with schedule"
                )

        return attrs


class ScheduleExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleException
        fields = [
            "id",
            "date",
            "is_day_off",
            "start_time",
            "end_time",
            "reason",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        date = attrs.get("date", self.instance.date if self.instance else None)
        is_day_off = attrs.get("is_day_off", self.instance.is_day_off if self.instance else True)

        start_time = attrs.get(
            "start_time",
            self.instance.start_time if self.instance else None
        )
        end_time = attrs.get(
            "end_time",
            self.instance.end_time if self.instance else None
        )

        if date < timezone.localdate():
            raise serializers.ValidationError({
                "date": "Date cannot be in the past."
            })

        if is_day_off and (start_time is not None or end_time is not None):
            raise serializers.ValidationError(
                "A day off cannot have working hours.s"
            )

        if not is_day_off and (start_time is None or end_time is None):
            raise serializers.ValidationError(
                "Working hours are required when it is not a day off."
            )

        if not is_day_off and end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be later than start time."
            })

        return attrs

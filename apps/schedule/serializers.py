from rest_framework import serializers
from .models import Schedule
from rest_framework.exceptions import ValidationError

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

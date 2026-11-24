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

        return attrs

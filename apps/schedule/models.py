from django.db import models
import uuid

class Schedule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["weekday", "start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="schedule_end_after_start",
            )
        ]


class ScheduleException(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    date = models.DateField(unique=True)
    is_day_off = models.BooleanField(default=True)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="schedule_exception_end_after_start",
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(
                        is_day_off=True,
                        start_time__isnull=True,
                        end_time__isnull=True,
                    )
                    |
                    models.Q(
                        is_day_off=False,
                        start_time__isnull=False,
                        end_time__isnull=False,
                    )
                ),
                name="schedule_exception_valid_times",
            ),
        ]

from django.db import models
import uuid
from apps.users.models import Client
from apps.bookings.models import Booking

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        BOOKING_CREATED = "booking_created", "Booking created"
        BOOKING_CONFIRMED = "booking_confirmed", "Booking confirmed"
        BOOKING_CANCELLED = "booking_cancelled", "Booking cancelled"
        BOOKING_REMINDER = "booking_reminder", "Booking reminder"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    recipient = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="notifications")
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="notifications")
    notification_type=models.CharField(max_length=20, choices=NotificationType.choices)
    message = models.TextField()
    last_error = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        ordering = ["-created_at"]

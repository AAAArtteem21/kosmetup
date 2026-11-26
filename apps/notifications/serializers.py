from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "status",
            "recipient",
            "booking",
            "notification_type",
            "message",
            "last_error",
            "is_read",
            "attempts",
            "next_retry_at",
            "created_at",
            "sent_at"
        ]
        read_only_fields = fields

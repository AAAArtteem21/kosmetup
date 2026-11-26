from .models import Notification
from apps.users.models import Client
from apps.bookings.models import Booking

def create_notification(recipient: Client, booking: Booking, notification_type: Notification.NotificationType, message: str) -> Notification:
    notification = Notification.objects.create(
        recipient=recipient,
        booking=booking,
        notification_type=notification_type,
        message=message,
    )

    return notification

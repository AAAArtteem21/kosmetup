from rest_framework.viewsets import ModelViewSet
from .serializers import BookingSerializer
from apps.services.permissions import IsCosmetologist
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.notifications.services import create_notification
from apps.notifications.models import Notification
from django.db import transaction


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [IsCosmetologist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.role == "cosmetologist"
        ):
            return Booking.objects.all()

        return Booking.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            booking = serializer.save(client=self.request.user)

            create_notification(
                recipient=self.request.user,
                booking=booking,
                notification_type=Notification.NotificationType.BOOKING_CREATED,
                message="Ваша запись создана",
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],)
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == Booking.Status.COMPLETED:
            raise serializers.ValidationError(
                "Your booking is completed"
            )
        if booking.status == Booking.Status.CANCELLED:
            raise serializers.ValidationError(
                "Your booking is already cancelled"
            )

        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

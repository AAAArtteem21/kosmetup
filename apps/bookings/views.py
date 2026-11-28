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
from django.db.models import Sum, Count
from decimal import Decimal
from apps.users.models import Client


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

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

    @action(detail=True, methods=['post'], permission_classes=[IsCosmetologist])
    def confirm(self, request, pk=None):
        with transaction.atomic():
            booking = self.get_queryset().select_for_update().get(pk=pk)
            if booking.status != Booking.Status.PENDING:
                raise serializers.ValidationError(
                    "You cannot confirm a booking that is not pending."
                )
            booking.status = Booking.Status.CONFIRMED
            booking.save(update_fields=["status", "updated_at"])
            create_notification(
                recipient=booking.client,
                booking=booking,
                notification_type=Notification.NotificationType.BOOKING_CONFIRMED,
                message="Ваша запись подтведжена."
            )

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            booking = self.get_queryset().select_for_update().get(pk=pk)
            if booking.status == Booking.Status.COMPLETED or booking.status == Booking.Status.CANCELLED:
                raise serializers.ValidationError(
                    "You cannot cancel a booking in status completed or cancelled"
                )
            booking.status = Booking.Status.CANCELLED
            booking.save(update_fields=["status", "updated_at"])
            create_notification(
                recipient=booking.client,
                booking=booking,
                notification_type=Notification.NotificationType.BOOKING_CANCELLED,
                message="Ваша запись отменена."
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsCosmetologist])
    def complete(self, request, pk=None):
        with transaction.atomic():
            booking = self.get_queryset().select_for_update().get(pk=pk)
            if booking.status != Booking.Status.CONFIRMED:
                raise serializers.ValidationError(
                    "You can complete only a confirmed booking."
                )
            booking.status = Booking.Status.COMPLETED
            booking.save(update_fields=["status", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_history(self, request):
        if request.user.role == Client.Role.COSMETOLOGIST:
            raise serializers.ValidationError(
                "Only clients can view their history."
            )

        bookings = Booking.objects.filter(
            client=request.user
        ).order_by("-date", "-start_time")

        status_filter = request.query_params.get("status")

        if status_filter:
            valid_statuses = Booking.Status.values

            if status_filter not in valid_statuses:
                raise serializers.ValidationError({
                    "status": "Invalid booking status."
                })

            bookings = bookings.filter(status=status_filter)

        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsCosmetologist])
    def statistics(self, request):
        booking = Booking.objects.all()
        total_bookings = booking.count()
        completed_bookings = booking.filter(status=Booking.Status.COMPLETED).count()
        canceled_bookings = booking.filter(status=Booking.Status.CANCELLED).count()
        pending_bookings = booking.filter(status=Booking.Status.PENDING).count()
        confirmed_bookings = booking.filter(status=Booking.Status.CONFIRMED).count()
        total_revenue = booking.filter(
            status=Booking.Status.COMPLETED
        ).aggregate(
            total_sum=Sum("total_price")
        )["total_sum"] or Decimal("0.00")

        return Response({
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "canceled_bookings": canceled_bookings,
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "total_revenue": total_revenue,
            }
        )

    @action(detail=False, methods=["get"], permission_classes=[IsCosmetologist])
    def popular_services(self, request):
        top_booking = Booking.objects.filter(
            status=Booking.Status.COMPLETED
        ).values(
            "service__name"
        ).annotate(
            booking_count=Count("id")
        ).order_by("-booking_count")[:5]

        return Response(top_booking)
            
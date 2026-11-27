from .models import Schedule, ScheduleException
from .serializers import ScheduleSerializer, ScheduleExceptionSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.services.permissions import IsCosmetologist
from django.utils import timezone
from rest_framework import serializers, status
from apps.services.models import Service
from datetime import date as date_type
from rest_framework.response import Response
from datetime import datetime, timedelta
from apps.bookings.models import Booking


class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsCosmetologist()]

    def destroy(self, request, *args, **kwargs):
        schedule= self.get_object()
        schedule.is_active = False
        schedule.save(update_fields=["is_active", "updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.role == "cosmetologist"
        ):
            return Schedule.objects.all()

        return Schedule.objects.filter(is_active=True)


class ScheduleExceptionViewSet(ModelViewSet):
    serializer_class = ScheduleExceptionSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsCosmetologist()]

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.role == "cosmetologist"
        ):
            return ScheduleException.objects.all()

        return ScheduleException.objects.filter(
            date__gte=timezone.localdate()
        )


class AvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.query_params.get("date")
        service_id = request.query_params.get("service")

        if not service_id:
            raise serializers.ValidationError({
                "service": "Service is required."
            })

        if not date:
            raise serializers.ValidationError({
                "date": "Date is required."
            })

        try:
            date = date_type.fromisoformat(date)
        except ValueError:
            raise serializers.ValidationError({
                "date": "Invalid date format. Use YYYY-MM-DD."
            })

        try:
            service = Service.objects.get(
                id=service_id,
                is_active=True
            )
        except (Service.DoesNotExist, ValueError):
            raise serializers.ValidationError({
                "service": "Service does not exist or is inactive."
            })

        if date < timezone.localdate():
            raise serializers.ValidationError({
                "date": "Cannot check availability for a past date."
            })

        exception = ScheduleException.objects.filter(
            date=date
        ).first()

        working_intervals = []

        if exception:
            if exception.is_day_off:
                return Response({"slots": []})

            working_intervals.append((
                exception.start_time,
                exception.end_time
            ))
        else:
            schedule = Schedule.objects.filter(
                weekday=date.weekday(),
                is_active=True
            )

            for item in schedule:
                working_intervals.append((
                    item.start_time,
                    item.end_time
                ))

            if not working_intervals:
                return Response({"slots": []})

        slots = []

        for start_time, end_time in working_intervals:
            current_time = datetime.combine(date, start_time)
            interval_end = datetime.combine(date, end_time)

            while (
                current_time + timedelta(
                    minutes=service.duration_minutes
                ) <= interval_end
            ):
                slots.append(current_time)
                current_time += timedelta(minutes=30)

        if date == timezone.localdate():
            now = timezone.localtime().time()
            slots = [
                slot for slot in slots
                if slot.time() > now
            ]

        bookings = Booking.objects.filter(
            date=date
        ).exclude(
            status=Booking.Status.CANCELLED
        ).values_list(
            "start_time",
            "end_time"
        )

        available_slots = []

        for slot in slots:
            slot_end = slot + timedelta(
                minutes=service.duration_minutes
            )

            is_available = True

            for booking_start, booking_end in bookings:
                booking_start = datetime.combine(date, booking_start)
                booking_end = datetime.combine(date, booking_end)

                if slot < booking_end and slot_end > booking_start:
                    is_available = False
                    break

            if is_available:
                available_slots.append(slot.strftime("%H:%M"))

        return Response({"slots": available_slots})

from django.shortcuts import render
from .models import Schedule
from .serializers import ScheduleSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from apps.services.permissions import IsCosmetologist

class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsCosmetologist()]

    def destroy(self, request, *args, **kwargs):
        schedule= self.get_object()
        schedule.is_active = False
        schedule.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.role == "cosmetologist"
        ):
            return Schedule.objects.all()

        return Schedule.objects.filter(is_active=True)

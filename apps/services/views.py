from django.shortcuts import render
from .serializers import ServiceSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Service
from .permissions import IsCosmetologist



class ServiceViewset(ModelViewSet):
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsCosmetologist()]

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        service.is_active = False
        service.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        if (
            self.request.user.is_authenticated
            and self.request.user.role == "cosmetologist"
        ):
            return Service.objects.all()

        return Service.objects.filter(is_active=True)

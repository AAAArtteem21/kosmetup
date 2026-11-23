from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Client


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = Client
        fields = ("username", "email", "password", "first_name", "last_name")

    def validate_password(self, value):
        user = Client(
            username=self.initial_data.get("username", ""),
            email=self.initial_data.get("email", ""),
        )
        try:
            validate_password(value, user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value

    def create(self, validated_data):
        return Client.objects.create_user(**validated_data)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("id", "username", "email", "first_name", "last_name", "role", "created_at")
        read_only_fields = fields

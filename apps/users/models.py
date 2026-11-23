from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class Client(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        COSMETOLOGIST = "cosmetologist", "Cosmetologist"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

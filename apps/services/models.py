from django.db import models
from apps.users.models import Client
import uuid
from django.db.models import Q


class Service(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(cost__gte=0),
                name="service_cost_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(duration_minutes__gt=0),
                name="service_duration_positive",
            ),
        ]

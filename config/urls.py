from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users.views import MeView, RegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/services/", include("apps.services.urls")),
    path("api/schedule/", include("apps.schedule.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]

from rest_framework.routers import DefaultRouter
from .views import NotificationViewset

router = DefaultRouter()
router.register("notification", NotificationViewset, basename="notification")

urlpatterns = router.urls

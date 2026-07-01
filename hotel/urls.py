from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, BookingViewSet, check_availability

router = DefaultRouter()
router.register("rooms", RoomViewSet, basename="room")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("check-availability/", check_availability, name="check-availability"),
    path("", include(router.urls)),
]

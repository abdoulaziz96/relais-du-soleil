from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer, AvailabilityCheckSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture seule côté public : les chambres se gèrent depuis /admin."""
    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer


def _overlapping_bookings_count(room, check_in, check_out):
    """Compte les réservations confirmées/en attente qui chevauchent la période demandée."""
    overlapping = Booking.objects.filter(
        room=room,
        status__in=["pending", "confirmed"],
    ).filter(
        Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
    )
    return overlapping.count()


@api_view(["POST"])
def check_availability(request):
    serializer = AvailabilityCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    room = serializer.validated_data["room"]
    check_in = serializer.validated_data["check_in"]
    check_out = serializer.validated_data["check_out"]

    booked_units = _overlapping_bookings_count(room, check_in, check_out)
    available_units = room.total_units - booked_units
    is_available = available_units > 0

    return Response({
        "room": room.id,
        "room_name": room.name,
        "check_in": check_in,
        "check_out": check_out,
        "available": is_available,
        "available_units": max(available_units, 0),
        "price_per_night": room.price_per_night,
    })


class BookingViewSet(viewsets.ModelViewSet):
    """
    Création + consultation des réservations.
    En production, restreindre list/retrieve avec une authentification (le gérant uniquement).
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    http_method_names = ["get", "post", "head"]  # pas de delete/patch publics pour l'instant

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.validated_data["room"]
        check_in = serializer.validated_data["check_in"]
        check_out = serializer.validated_data["check_out"]

        booked_units = _overlapping_bookings_count(room, check_in, check_out)
        if booked_units >= room.total_units:
            return Response(
                {"detail": "Plus de disponibilité pour cette chambre sur ces dates."},
                status=status.HTTP_409_CONFLICT,
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

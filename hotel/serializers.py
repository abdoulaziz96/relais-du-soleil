from rest_framework import serializers
from .models import Room, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "type_code", "name", "description", "price_per_night", "total_units", "is_active"]


class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "room", "room_name", "guest_name", "guest_phone",
            "guests_count", "check_in", "check_out", "status", "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError(
                "La date de départ doit être après la date d'arrivée."
            )
        return data


class AvailabilityCheckSerializer(serializers.Serializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError(
                "La date de départ doit être après la date d'arrivée."
            )
        return data

from django.db import models
from django.core.validators import MinValueValidator


class Room(models.Model):
    """A room type/category (Standard, Confort, Suite...), not a single physical room."""

    ROOM_TYPES = [
        ("Standard", "Standard"),
        ("Confort", "Confort climatisée"),
        ("Suite", "Suite Fleuve"),
    ]

    type_code = models.CharField(max_length=30, choices=ROOM_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=0)
    total_units = models.PositiveIntegerField(
        default=1, help_text="Nombre de chambres de ce type disponibles à l'hôtel."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price_per_night"]

    def __str__(self):
        return f"{self.name} ({self.price_per_night} FCFA/nuit)"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("confirmed", "Confirmée"),
        ("cancelled", "Annulée"),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    guest_name = models.CharField(max_length=150)
    guest_phone = models.CharField(max_length=30)
    guests_count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.guest_name} — {self.room.name} ({self.check_in} → {self.check_out})"

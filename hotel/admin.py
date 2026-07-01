from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "type_code", "price_per_night", "total_units", "is_active")
    list_editable = ("price_per_night", "total_units", "is_active")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "guest_phone", "room", "check_in", "check_out", "status", "created_at")
    list_filter = ("status", "room")
    list_editable = ("status",)
    search_fields = ("guest_name", "guest_phone")

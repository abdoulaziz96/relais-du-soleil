from django.core.management.base import BaseCommand
from hotel.models import Room, Booking
from datetime import date


class Command(BaseCommand):
    help = "Insère les chambres et réservations de test"

    def handle(self, *args, **kwargs):

        # Chambres
        rooms_data = [
            dict(type_code="Standard", name="Standard",
                 price_per_night=15000,
                 description="Lit double, ventilateur, salle de bain privée.",
                 total_units=8),
            dict(type_code="Confort", name="Confort climatisée",
                 price_per_night=22000,
                 description="Climatisation, télévision, eau chaude.",
                 total_units=6),
            dict(type_code="Suite", name="Suite Fleuve",
                 price_per_night=35000,
                 description="Espace salon, vue dégagée, idéale pour familles ou séjours d'affaires.",
                 total_units=3),
        ]
        for r in rooms_data:
            obj, created = Room.objects.get_or_create(
                type_code=r["type_code"], defaults=r
            )
            if created:
                self.stdout.write(f"  ✓ Chambre créée : {obj.name}")
            else:
                self.stdout.write(f"  → Chambre déjà existante : {obj.name}")

        # Réservations de test
        standard = Room.objects.get(type_code="Standard")
        confort = Room.objects.get(type_code="Confort")
        suite = Room.objects.get(type_code="Suite")

        bookings_data = [
            dict(room=standard, guest_name="Moussa Traoré",
                 guest_phone="+22966112233", guests_count=2,
                 check_in=date(2026, 7, 10), check_out=date(2026, 7, 13),
                 status="confirmed"),
            dict(room=confort, guest_name="Fatima Alou",
                 guest_phone="+22797445566", guests_count=1,
                 check_in=date(2026, 7, 15), check_out=date(2026, 7, 17),
                 status="confirmed"),
            dict(room=suite, guest_name="Ibrahim Maiga",
                 guest_phone="+22766778899", guests_count=4,
                 check_in=date(2026, 8, 1), check_out=date(2026, 8, 5),
                 status="pending"),
            dict(room=standard, guest_name="Aïcha Diallo",
                 guest_phone="+22961334455", guests_count=2,
                 check_in=date(2026, 8, 10), check_out=date(2026, 8, 12),
                 status="pending"),
            dict(room=confort, guest_name="Youssouf Kané",
                 guest_phone="+22799887766", guests_count=2,
                 check_in=date(2026, 7, 20), check_out=date(2026, 7, 22),
                 status="cancelled"),
        ]

        for b in bookings_data:
            # évite les doublons si le script tourne plusieurs fois
            exists = Booking.objects.filter(
                room=b["room"],
                guest_name=b["guest_name"],
                check_in=b["check_in"]
            ).exists()
            if not exists:
                Booking.objects.create(**b)
                self.stdout.write(f"  ✓ Réservation : {b['guest_name']} ({b['check_in']})")
            else:
                self.stdout.write(f"  → Déjà existant : {b['guest_name']}")

        self.stdout.write(self.style.SUCCESS("\nSeed terminé ✓"))
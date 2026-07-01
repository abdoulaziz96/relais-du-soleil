from django.db import migrations


def seed_rooms(apps, schema_editor):
    Room = apps.get_model("hotel", "Room")
    rooms = [
        dict(type_code="Standard", name="Standard", price_per_night=15000,
             description="Lit double, ventilateur, salle de bain privée.", total_units=8),
        dict(type_code="Confort", name="Confort climatisée", price_per_night=22000,
             description="Climatisation, télévision, eau chaude.", total_units=6),
        dict(type_code="Suite", name="Suite Fleuve", price_per_night=35000,
             description="Espace salon, vue dégagée, idéale pour familles ou séjours d'affaires.", total_units=3),
    ]
    for r in rooms:
        Room.objects.get_or_create(type_code=r["type_code"], defaults=r)


def remove_rooms(apps, schema_editor):
    Room = apps.get_model("hotel", "Room")
    Room.objects.filter(type_code__in=["Standard", "Confort", "Suite"]).delete()


class Migration(migrations.Migration):
    dependencies = [("hotel", "0001_initial")]
    operations = [migrations.RunPython(seed_rooms, remove_rooms)]

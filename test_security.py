"""
Tests de sécurité — utilise le client de test Django (pas de serveur HTTP requis).
Lance avec : python manage.py test hotel.tests_security --verbosity=0
Ou directement : python test_security.py
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "relais_backend.settings")
os.environ["DEBUG"] = "True"   # force le mode debug pour les tests locaux

import django
django.setup()

from django.test import TestCase, RequestFactory
from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from hotel.models import Room, Booking
import json

OK   = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
results = []

def check(label, passed, detail=""):
    icon = OK if passed else FAIL
    results.append(passed)
    print(f"  {icon}  {label}" + (f"\n       → {detail}" if detail else ""))

# Réinitialiser la base de test avec les données de seed
from django.test.utils import setup_databases
from io import StringIO

print("\n🔒 Tests de sécurité — Relais du Soleil\n")
print("(Utilise le client de test Django — pas de serveur HTTP requis)\n")

c = Client(enforce_csrf_checks=False)

# Récupère une vraie chambre
room = Room.objects.first()
if not room:
    print("❌  Aucune chambre en base. Lance d'abord : python manage.py migrate")
    exit(1)

# ── 1. GET /api/rooms/ retourne la liste ────────────────────────────────────
print("[1] Endpoint chambres")
resp = c.get("/api/rooms/")
rooms_data = resp.json()
check("GET /api/rooms/ → 200 avec chambres",
      resp.status_code == 200 and len(rooms_data) > 0,
      f"Chambres reçues : {[r['name'] for r in rooms_data]}")

# ── 2. Disponibilité normale ─────────────────────────────────────────────────
print("\n[2] Vérification de disponibilité")
resp = c.post("/api/check-availability/",
    data=json.dumps({"room": room.id, "check_in": "2026-08-01", "check_out": "2026-08-03"}),
    content_type="application/json")
check("Disponibilité réelle → 200 + champ 'available'",
      resp.status_code == 200 and "available" in resp.json(),
      str(resp.json()))

# ── 3. Validation des dates inversées ────────────────────────────────────────
print("\n[3] Validation des dates")
resp = c.post("/api/check-availability/",
    data=json.dumps({"room": room.id, "check_in": "2026-08-10", "check_out": "2026-08-05"}),
    content_type="application/json")
check("Dates inversées refusées (400)", resp.status_code == 400,
      f"Code reçu : {resp.status_code}")

# ── 4. Création de réservation valide ─────────────────────────────────────────
print("\n[4] Création de réservation")
resp = c.post("/api/bookings/",
    data=json.dumps({
        "room": room.id, "check_in": "2026-10-01", "check_out": "2026-10-03",
        "guest_name": "Moussa Traoré", "guest_phone": "+22966000001", "guests_count": 2
    }), content_type="application/json")
check("Réservation valide créée (201)", resp.status_code == 201,
      f"Code reçu : {resp.status_code} — {resp.json().get('id', resp.json())}")

# ── 5. Anti-overbooking ───────────────────────────────────────────────────────
print("\n[5] Anti-overbooking")
# Trouver la Suite (3 unités) et la saturer
suite = Room.objects.filter(type_code="Suite").first()
if suite:
    payload = {"room": suite.id, "check_in": "2026-11-01", "check_out": "2026-11-03",
               "guest_name": "X", "guest_phone": "+229000000", "guests_count": 1}
    codes = []
    for i in range(suite.total_units + 1):
        r = c.post("/api/bookings/",
            data=json.dumps({**payload, "guest_name": f"Client {i}", "guest_phone": f"+2299000000{i}"}),
            content_type="application/json")
        codes.append(r.status_code)
    last = codes[-1]
    check(f"Réservation n°{suite.total_units + 1} refusée quand toutes les unités prises (409)",
          last == 409, f"Codes obtenus : {codes}")
else:
    check("Anti-overbooking (Suite non trouvée)", False, "Chambre Suite absente")

# ── 6. Champs obligatoires manquants ─────────────────────────────────────────
print("\n[6] Validation des champs")
resp = c.post("/api/bookings/",
    data=json.dumps({"room": room.id, "check_in": "2026-08-01"}),
    content_type="application/json")
check("Réservation incomplète refusée (400)", resp.status_code == 400,
      f"Erreurs : {resp.json()}")

# ── 7. JSON malformé ──────────────────────────────────────────────────────────
print("\n[7] Données malformées")
resp = c.post("/api/bookings/", data=b"<<pas du json>>",
              content_type="application/json")
check("JSON invalide refusé (400)", resp.status_code == 400,
      f"Code reçu : {resp.status_code}")

# ── 8. DELETE non autorisé sur les réservations ──────────────────────────────
print("\n[8] Méthodes HTTP non autorisées")
resp = c.delete("/api/bookings/")
check("DELETE /api/bookings/ → 405 Method Not Allowed",
      resp.status_code == 405, f"Code reçu : {resp.status_code}")

# ── 9. Route inexistante ──────────────────────────────────────────────────────
print("\n[9] Gestion des erreurs")
resp = c.get("/api/inexistant/")
body = resp.content
check("Route inconnue → 404 sans traceback",
      resp.status_code == 404 and b"Traceback" not in body,
      "Traceback visible !" if b"Traceback" in body else "Réponse propre")

# ── 10. Panneau admin protégé ─────────────────────────────────────────────────
print("\n[10] Accès admin")
resp = c.get("/admin/reservations/", follow=False)
check("Admin sans login → redirection vers login",
      resp.status_code in (301, 302), f"Code reçu : {resp.status_code}")

# ── Throttling (simulé, le vrai test DRF se fait en intégration) ──────────────
print("\n[11] Throttling DRF (vérification config)")
from rest_framework.settings import api_settings
throttle_rates = api_settings.DEFAULT_THROTTLE_RATES
check("Throttle configuré pour les anonymes",
      'anon' in throttle_rates,
      f"Taux configurés : {throttle_rates}")

# ── Résumé ────────────────────────────────────────────────────────────────────
passed = sum(results)
total = len(results)
print(f"\n{'─'*50}")
print(f"Résultat : {passed}/{total} tests passés")
if passed == total:
    print("✅  Tous les tests passent — bon pour la démo.")
else:
    print(f"⚠️   {total - passed} point(s) à corriger.")
print()

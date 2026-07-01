# Backend Relais du Soleil — Django

## Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Un compte admin existe déjà : **admin / relais2026** (à changer !).
Pour en créer un autre : `python manage.py createsuperuser`

Le serveur tourne sur http://127.0.0.1:8000

## Panneau d'administration (pour le gérant)
http://127.0.0.1:8000/admin/
→ Modifier les tarifs, le nombre de chambres, voir/confirmer les réservations.
Aucune compétence technique requise.

## Endpoints API

| Méthode | URL                                   | Description                          |
|---------|----------------------------------------|---------------------------------------|
| GET     | /api/rooms/                            | Liste des chambres actives            |
| POST    | /api/check-availability/               | Vérifie la dispo (room, check_in, check_out) |
| POST    | /api/bookings/                         | Crée une réservation                  |
| GET     | /api/bookings/                         | Liste des réservations (à protéger en prod) |

### Exemple check-availability
```json
POST /api/check-availability/
{ "room": 1, "check_in": "2026-07-10", "check_out": "2026-07-12" }
```

### Exemple création réservation
```json
POST /api/bookings/
{
  "room": 1, "check_in": "2026-07-10", "check_out": "2026-07-12",
  "guest_name": "Aboul-aziz", "guest_phone": "+22966191510", "guests_count": 2
}
```

## Avant la mise en production

1. Dans `settings.py` : remplacer `CORS_ALLOW_ALL_ORIGINS = True` par
   `CORS_ALLOWED_ORIGINS = ["https://tondomaine.com"]`
2. Mettre `DEBUG = False` et configurer `ALLOWED_HOSTS`.
3. Changer `SECRET_KEY` et le mot de passe admin.
4. Passer de SQLite à PostgreSQL pour un usage en production (Render, Railway, PythonAnywhere supportent ça facilement, ou hébergement local).
5. Restreindre `DEFAULT_PERMISSION_CLASSES` pour que `GET /api/bookings/`
   nécessite une authentification (seul le gérant doit voir la liste des clients).
6. Déployer (Railway, Render, PythonAnywhere sont de bonnes options simples et peu coûteuses pour démarrer).

## Brancher le frontend

Dans le fichier HTML (`relais-du-soleil-connecte.html`), la variable
`API_BASE` en haut du `<script>` pointe vers `http://127.0.0.1:8000/api`
en local. Remplace-la par l'URL réelle une fois le backend déployé.

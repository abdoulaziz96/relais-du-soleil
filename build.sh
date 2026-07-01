#!/usr/bin/env bash
set -e

echo "==> Installation des dépendances"
pip install -r requirements.txt

echo "==> Migrations"
python manage.py migrate

echo "==> Seed des données (chambres + réservations de test)"
python manage.py seed_data

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --noinput

echo "==> Build terminé"
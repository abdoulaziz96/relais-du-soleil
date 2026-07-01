#!/usr/bin/env bash
set -e

echo "==> Installation des dépendances"
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques"
python manage.py collectstatic --noinput

echo "==> Migrations"
python manage.py migrate

echo "==> Build terminé"
# Déploiement sur Render — Guide étape par étape

## 1. Préparer un compte GitHub (si pas encore fait)
Crée un compte sur https://github.com si tu n'en as pas.

## 2. Créer le dépôt GitHub

```bash
# Dans le dossier relais_backend, lance ces commandes une fois :
git init
git add .
git commit -m "Initial : site Relais du Soleil"
```

Ensuite :
- Va sur https://github.com/new
- Donne le nom : `relais-du-soleil`
- Laisse en **Public** (gratuit, Render peut y accéder)
- Clique "Create repository"
- Copie les deux lignes "…push an existing repository" affichées, exemple :

```bash
git remote add origin https://github.com/TON_PSEUDO/relais-du-soleil.git
git push -u origin main
```

## 3. Créer le service sur Render

1. Va sur https://render.com → "Get Started for Free"
2. Connecte-toi avec ton compte GitHub
3. Clique **"New +" → "Web Service"**
4. Sélectionne le dépôt `relais-du-soleil`
5. Render détecte `render.yaml` automatiquement — confirme les paramètres :
   - **Runtime** : Python 3
   - **Build Command** : `./build.sh`
   - **Start Command** : `gunicorn relais_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
6. Clique **"Create Web Service"**

## 4. Configurer les variables d'environnement

Dans Render → Settings → Environment Variables, ajoute :

| Variable              | Valeur                                  |
|-----------------------|-----------------------------------------|
| `SECRET_KEY`          | (Render génère automatiquement — OK)    |
| `DEBUG`               | `False`                                 |
| `ALLOWED_HOSTS`       | `relais-du-soleil.onrender.com`         |
| `CSRF_TRUSTED_ORIGINS`| `https://relais-du-soleil.onrender.com` |

⚠️ L'URL exacte (`relais-du-soleil.onrender.com`) s'affiche dans Render dès
que le service est créé — copie-la exactement.

## 5. Créer le compte admin en production

Une fois le déploiement terminé, dans Render → ton service → onglet "Shell" :

```bash
python manage.py createsuperuser
```

Choisis un vrai mot de passe fort cette fois.

## 6. Envoyer le lien au client

Ton site sera accessible sur :
https://relais-du-soleil.onrender.com

Admin du gérant :
https://relais-du-soleil.onrender.com/admin/

## Note sur le plan gratuit Render

Le service gratuit se "met en veille" après 15 minutes sans trafic.
La première visite après une veille prend 20-30 secondes.
Pour une démo, c'est suffisant. Pour un client payant, prévoie le plan
"Starter" à 7$/mois qui supprime cette limite.

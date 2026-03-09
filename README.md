# ecoRide : plateforme de covoiturage eco-responsable

Ce projet est une maquette d'application de covoiturage axée sur la sensibilisation écologique et visant à inciter les utilisateurs à participer à des trajets partagés.

### Architecture
- **backend** : Flask, Postgres, Mongo
- **frontend** : Vite, HTMX, Alpinejs, Tailwindcss

L'application est conteneurisée avec Docker et déployée sur un VPS Linux.
> [Visiter l'application](https://vem-test.xyz)

Les identifiants d'accès administrateur sont fournis dans la *copie à rendre*.

---

## Configuration de l'environnement

Cloner le dépôt sur une machine Linux avec Docker installé.

Déployer un VPS via le fournisseur de votre choix. Les fournisseurs proposent généralement un terminal pour la configuration initiale :
- création d'un utilisateur non-root avec accès `sudo`
- configuration SSH pour l'accès distant
- installation de Nginx comme reverse proxy, et Certbot pour le TLS

Installer Docker sur le serveur (exemple pour Fedora/RHEL) :
```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
```

---

## Variables d'environnement

Docker et Flask attendent un fichier `.env` à la racine du projet. Les services de base de données requièrent une authentification, et une clé API pour le service d'envoi d'e-mails est nécessaire. Le fichier `environment.txt` à la racine du projet fournit le modèle avec toutes les variables attendues.

---

## Services de l'application

Trois conteneurs sont définis dans `compose.yaml` :

- **postgres** : `postgis/postgis:17-3.5` — choisi pour ses capacités GIS
- **mongo** : `7.0` — recommandé pour la compatibilité et la stabilité
- **flask_ecoride** : `python:3.12-slim` — voir le `Dockerfile` à la racine pour la configuration complète

---

## Build et lancement

### 1. Build des assets frontend

Le build Vite doit être exécuté avant de construire l'image Docker, car les assets compilés sont copiés dans le conteneur :
```bash
cd frontend
npm install
npm run build
cd ..
```

Cela génère les bundles CSS/JS avec hash dans `flask_app/app/static/dist/`.

### 2. Build et démarrage des conteneurs

Depuis la racine du dépôt (là où se trouve `compose.yaml`) :
```bash
docker compose build
docker compose up -d
```

### 3. Vérification

Consulter les logs de l'application :
```bash
docker logs flask_ecoride
```

Vous devriez voir quelque chose comme :
```
flask_ecoride  | [2026-01-01 17:01:25 +0000] [1] [INFO] Starting gunicorn 23.0.0
flask_ecoride  | [2026-01-01 17:01:25 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
flask_ecoride  | [2026-01-01 17:01:25 +0000] [1] [INFO] Using worker: sync
flask_ecoride  | [2026-01-01 17:01:25 +0000] [7] [INFO] Booting worker with pid: 7
flask_ecoride  | [2026-01-01 17:01:25 +0000] [8] [INFO] Booting worker with pid: 8
flask_ecoride  | [2026-01-01 17:01:25 +0000] [9] [INFO] Booting worker with pid: 9
flask_ecoride  | [17:01:26] INFO     TIME NOW : 01 January 2026
flask_ecoride  |            INFO     static ids loaded ~
flask_ecoride  |            INFO     DB SEED : Database seeded.
flask_ecoride  |            INFO     BATCH SUMMARIES: 42 summaries generated.
```

Indicateurs clés :
- `Listening at: http://0.0.0.0:8000` — Gunicorn sert l'application (3 workers sync)
- `static ids loaded` — Postgres est opérationnel et Flask peut y accéder
- `DB SEED` — la base de données a été peuplée avec des données de test

L'application écoute sur le port `8000` à l'intérieur du conteneur, lié à `127.0.0.1` sur l'hôte :
```yaml
services:
  flask_ecoride:
    ports:
      - "127.0.0.1:8000:8000"
```

Nginx prend en charge le trafic depuis là, en routant les requêtes du domaine vers l'application. Le domaine est sécurisé par Certbot pour le TLS.

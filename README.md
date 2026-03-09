# ecoRide : plateforme de covoiturage eco-responsable

Ce projet est une maquette d'application de covoiturage axée sur la sensibilisation écologique et visant à inciter les utilisateurs à participer à des trajets partagés.

### architecture
- **backend** : Flask, Postgres, Mongo
- **frontend** : Vite, HTMX, Alpinejs, Tailwindcss

The application is containerized using Docker, and deployed to a Linux-based VPS.
> [visit the live app](https://vem-test.xyz)

Credentials for admin access to the live app are provided in the *copie a rendre*.

---

## environment configuration

Clone the repository on a Linux machine with Docker installed.

Deploy a VPS via a provider of your choice. Providers usually give a terminal to do initial setup:
- create a non-root user with `sudo` access
- configure SSH for remote access
- install Nginx as a reverse proxy, and Certbot for TLS

Install Docker on the server (example for Fedora/RHEL):
```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
```

---

## environment variables

Docker and Flask expect a `.env` file at the root of the project. Database services rely on authentication, and a third-party mailing API key is required. The `environment.txt` file at the root provides the template with all expected variables.

---

## application services

Three containers are defined in `compose.yaml`:

- **postgres** : `postgis/postgis:17-3.5` — chosen for its GIS capabilities
- **mongo** : `7.0` — recommended for compatibility and stability
- **flask_ecoride** : `python:3.12-slim` — see `Dockerfile` for the full configuration

---

## build and run

### 1. build the frontend assets

The Vite build must be run before building the Docker image, as the compiled assets are copied into the container:
```bash
cd frontend
npm install
npm run build
cd ..
```

This generates the hashed CSS/JS bundles into `flask_app/app/static/dist/`.

### 2. build and start the containers

From the root of the repository (where `compose.yaml` lives):
```bash
docker compose build
docker compose up -d
```

### 3. verify

Check the Flask app logs:
```bash
docker logs flask_ecoride
```

You should see something like:
```
flask_ecoride  | [2026-01-01 17:01:25 +0000] [1] [INFO] Starting gunicorn 23.0.0
flask_ecoride  | [2026-01-01 17:01:25 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
flask_ecoride  | [2026-01-01 17:01:25 +0000] [1] [INFO] Using worker: sync
flask_ecoride  | [2026-01-01 17:01:25 +0000] [7] [INFO] Booting worker with pid: 7
flask_ecoride  | [2026-01-01 17:01:25 +0000] [8] [INFO] Booting worker with pid: 8
flask_ecoride  | [2026-01-01 17:01:25 +0000] [9] [INFO] Booting worker with pid: 9
flask_ecoride  | [17:01:26] INFO     TIME NOW : 01 January 2026 - 17:01hs          main.py:59
flask_ecoride  |            INFO     static ids loaded ~                            main.py:65
flask_ecoride  |            INFO     DB SEED : Database seeded.
flask_ecoride  |            INFO     BATCH SUMMARIES: 42 summaries generated.
```

Key indicators:
- `Listening at: http://0.0.0.0:8000` — Gunicorn is serving the app (3 sync workers)
- `static ids loaded` — Postgres is running and Flask can reach it
- `DB SEED` — the database was seeded with test data

The app listens on port `8000` inside the container, bound to `127.0.0.1` on the host:
```yaml
services:
  flask_ecoride:
    ports:
      - "127.0.0.1:8000:8000"
```

Nginx handles traffic from there, routing requests from the domain to the app. The domain is secured by Certbot for TLS.

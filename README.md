# AnalyseCV Django

Application Django pour l'analyse de CV avec intégration MinIO et API Anthropic Claude.

## Démarrage rapide

### Prérequis
- Docker et Docker Compose installés
- Git (pour cloner le projet)

### Installation et démarrage

1. **Configuration initiale** :
   ```bash
   cp env.example .env
   nano .env
   ```

2. **Démarrage** :
   ```bash
   docker-compose build
   docker-compose up -d
   docker-compose ps
   ```

## Services disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **Django App** | http://localhost:8000 | Application principale |
| **MinIO Console** | http://localhost:9001 | Interface de gestion des fichiers |
| **MinIO API** | http://localhost:9000 | API de stockage des fichiers |

### Identifiants MinIO par défaut
- Utilisateur : `minioadmin`
- Mot de passe : `minioadmin123`

## Commandes utiles

### Make
```bash
make up                # Démarrer les services
make down              # Arrêter les services
make logs              # Voir les logs
make shell             # Shell Django
make migrate           # Migrations
make test              # Tests
```

### Docker Compose
```bash
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose exec web python manage.py migrate
docker-compose exec web bash
```

## Structure du projet

```
analyse-cv-django/
├── accounts/                   # Gestion des utilisateurs
├── candidatures/              # Gestion des candidatures
├── dashboard/                 # Tableau de bord
├── AnalyseCVProject/          # Configuration Django
├── templates/                 # Templates HTML
├── static/                    # Fichiers statiques
├── Dockerfile                 # Image Docker
├── docker-compose.yml         # Configuration Docker
├── requirements.txt           # Dépendances de base
├── requirements-dev.txt       # Dépendances de développement
├── requirements-prod.txt      # Dépendances de production
└── Makefile                   # Commandes
```

## Configuration

### Variables d'environnement (.env)
```bash
DEBUG=True
SECRET_KEY=votre-secret
ANTHROPIC_API_KEY=votre-cle-api
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_SECURE=False
MINIO_BUCKET_NAME=cv-uploads
```

## Tests

```bash
make test
docker-compose exec web python manage.py test
```

## Logs

```bash
docker-compose logs -f
docker-compose logs -f web
docker-compose ps
```

## Dépannage

### Problèmes courants

**Port 8000 déjà utilisé** :
```bash
# Modifier le port dans docker-compose.yml
ports:
  - "8080:8000"
```

**Reconstruire sans cache** :
```bash
docker-compose build --no-cache
```

**Nettoyer les volumes** :
```bash
docker-compose down -v
docker-compose up -d
```

## Développement

### Ajout de dépendances
1. Ajouter dans le fichier approprié (requirements.txt, requirements-dev.txt, requirements-prod.txt)
2. Reconstruire : `docker-compose build`

### Hot reload
Le code est monté en volume, les modifications sont automatiquement prises en compte.

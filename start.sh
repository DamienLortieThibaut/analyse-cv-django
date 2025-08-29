#!/bin/bash

set -e

echo "Démarrage de l'application AnalyseCV..."

if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose n'est pas installé."
    exit 1
fi

if [ ! -f .env ]; then
    echo "Création du fichier .env..."
    cp env.example .env
    echo "Configurez vos variables d'environnement dans .env"
fi

echo "Construction des images..."
docker-compose build

echo "Démarrage des services..."
docker-compose up -d

echo "Attente du démarrage..."
sleep 10

echo "État des conteneurs :"
docker-compose ps

echo ""
echo "Application démarrée :"
echo "  - Django : http://localhost:8000"
echo "  - MinIO : http://localhost:9001 (minioadmin/minioadmin123)"
echo ""
echo "Commandes utiles :"
echo "  - Logs : docker-compose logs -f"
echo "  - Arrêter : docker-compose down"
echo "  - Shell : docker-compose exec web bash"
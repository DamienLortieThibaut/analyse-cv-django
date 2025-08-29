# Script PowerShell pour démarrer l'application AnalyseCV

Write-Host "Démarrage de l'application AnalyseCV..." -ForegroundColor Green

# Vérifier si Docker est installé
try {
    docker --version | Out-Null
} catch {
    Write-Host "Docker n'est pas installé." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Vérifier si Docker Compose est installé
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "Docker Compose n'est pas installé." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "Création du fichier .env..." -ForegroundColor Yellow
    
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
    } else {
        @"
DEBUG=True
SECRET_KEY=votre-secret
ANTHROPIC_API_KEY=votre-cle-api
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_SECURE=False
MINIO_BUCKET_NAME=cv-uploads
"@ | Out-File -FilePath ".env" -Encoding UTF8
    }
    Write-Host "Configurez vos variables d'environnement dans .env" -ForegroundColor Yellow
}

# Construction des images
Write-Host "Construction des images..." -ForegroundColor Blue
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de la construction des images" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Démarrage des services
Write-Host "Démarrage des services..." -ForegroundColor Blue
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors du démarrage des services" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Attente du démarrage
Write-Host "Attente du démarrage..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# État des conteneurs
Write-Host "État des conteneurs :" -ForegroundColor Green
docker-compose ps

Write-Host ""
Write-Host "Application démarrée :" -ForegroundColor Green
Write-Host "  - Django : http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - MinIO : http://localhost:9001 (minioadmin/minioadmin123)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commandes utiles :" -ForegroundColor Yellow
Write-Host "  - Logs : docker-compose logs -f"
Write-Host "  - Arrêter : docker-compose down"
Write-Host "  - Shell : docker-compose exec web bash"
Write-Host ""

Read-Host "Appuyez sur Entrée pour continuer"

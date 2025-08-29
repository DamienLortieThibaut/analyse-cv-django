@echo off
setlocal enabledelayedexpansion

echo Demarrage de l'application AnalyseCV...

:: Verifier si Docker est installe
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker n'est pas installe.
    pause
    exit /b 1
)

:: Verifier si Docker Compose est installe
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose n'est pas installe.
    pause
    exit /b 1
)

:: Creer le fichier .env s'il n'existe pas
if not exist .env (
    echo Creation du fichier .env...
    if exist env.example (
        copy env.example .env >nul
    ) else (
        echo DEBUG=True > .env
        echo SECRET_KEY=votre-secret >> .env
        echo ANTHROPIC_API_KEY=votre-cle-api >> .env
        echo ANTHROPIC_MODEL=claude-3-5-sonnet-20241022 >> .env
        echo MINIO_ENDPOINT=localhost:9000 >> .env
        echo MINIO_ACCESS_KEY=minioadmin >> .env
        echo MINIO_SECRET_KEY=minioadmin123 >> .env
        echo MINIO_SECURE=False >> .env
        echo MINIO_BUCKET_NAME=cv-uploads >> .env
    )
    echo Configurez vos variables d'environnement dans .env
)

echo Construction des images...
docker-compose build
if errorlevel 1 (
    echo Erreur lors de la construction des images
    pause
    exit /b 1
)

echo Demarrage des services...
docker-compose up -d
if errorlevel 1 (
    echo Erreur lors du demarrage des services
    pause
    exit /b 1
)

echo Attente du demarrage...
timeout /t 10 /nobreak >nul

echo Etat des conteneurs :
docker-compose ps

echo.
echo Application demarree :
echo   - Django : http://localhost:8000
echo   - MinIO : http://localhost:9001 (minioadmin/minioadmin123)
echo.
echo Commandes utiles :
echo   - Logs : docker-compose logs -f
echo   - Arreter : docker-compose down
echo   - Shell : docker-compose exec web bash
echo.
pause

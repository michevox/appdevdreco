@echo off
echo 🐘 Installation PostgreSQL pour DEVDRECO SOFT
echo ================================================

echo.
echo 📋 Vérification des prérequis...

:: Vérifier si Chocolatey est installé
where choco >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Chocolatey trouvé
    echo.
    echo 🔄 Installation PostgreSQL avec Chocolatey...
    choco install postgresql -y
    goto :configure
)

:: Vérifier si Scoop est installé
where scoop >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Scoop trouvé
    echo.
    echo 🔄 Installation PostgreSQL avec Scoop...
    scoop install postgresql
    goto :configure
)

:: Aucun gestionnaire de paquets trouvé
echo ❌ Aucun gestionnaire de paquets trouvé
echo.
echo 📥 Installation manuelle requise :
echo 1. Visitez : https://www.postgresql.org/download/windows/
echo 2. Téléchargez l'installateur officiel
echo 3. Exécutez l'installateur
echo 4. Choisissez un mot de passe pour 'postgres'
echo 5. Notez le port (par défaut 5432)
echo.
echo Après installation, relancez ce script.
pause
exit /b 1

:configure
echo.
echo 🔧 Configuration PostgreSQL...

:: Démarrer le service PostgreSQL
echo 🔄 Démarrage du service PostgreSQL...
net start postgresql-x64-15 2>nul
if %errorlevel% neq 0 (
    net start postgresql-x64-14 2>nul
    if %errorlevel% neq 0 (
        net start postgresql-x64-13 2>nul
        if %errorlevel% neq 0 (
            echo ⚠️ Impossible de démarrer PostgreSQL automatiquement
            echo 💡 Démarrez manuellement via les Services Windows
        )
    )
)

:: Attendre que le service démarre
timeout /t 5 /nobreak >nul

:: Créer la base de données
echo 🗄️ Création de la base de données...
createdb -U postgres devdreco_soft 2>nul
if %errorlevel% equ 0 (
    echo ✅ Base de données 'devdreco_soft' créée
) else (
    echo ⚠️ Impossible de créer la base de données automatiquement
    echo 💡 Créez manuellement : psql -U postgres -c "CREATE DATABASE devdreco_soft;"
)

echo.
echo 🎉 Installation PostgreSQL terminée !
echo.
echo 📋 Prochaines étapes :
echo 1. python manage.py migrate
echo 2. python manage.py createsuperuser
echo 3. python manage.py runserver
echo.
pause

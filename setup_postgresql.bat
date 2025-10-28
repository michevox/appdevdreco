@echo off
echo 🐘 Configuration PostgreSQL pour DEVDRECO SOFT
echo ================================================

echo.
echo 📋 Création de la base de données...

:: Ajouter PostgreSQL au PATH
set PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin

:: Créer la base de données
echo 🔄 Création de la base de données 'devdreco_soft'...
createdb -U postgres devdreco_soft

if %errorlevel% equ 0 (
    echo ✅ Base de données créée avec succès !
) else (
    echo ❌ Erreur lors de la création de la base de données
    echo 💡 Vérifiez le mot de passe PostgreSQL
    pause
    exit /b 1
)

echo.
echo 🔄 Migration Django...
python manage.py migrate

if %errorlevel% equ 0 (
    echo ✅ Migration réussie !
) else (
    echo ❌ Erreur lors de la migration
    pause
    exit /b 1
)

echo.
echo 🔄 Création du superutilisateur...
python manage.py createsuperuser

echo.
echo 🎉 Configuration PostgreSQL terminée !
echo.
echo 📋 Prochaines étapes :
echo 1. python manage.py runserver
echo 2. Visitez : http://127.0.0.1:8000
echo.
pause

# Script PowerShell pour installer PostgreSQL sur Windows
# DEVDRECO SOFT

Write-Host "🐘 Installation PostgreSQL pour DEVDRECO SOFT" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Vérifier si PowerShell est exécuté en tant qu'administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️ Ce script nécessite des privilèges administrateur" -ForegroundColor Yellow
    Write-Host "💡 Relancez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour continuer"
}

# Fonction pour vérifier si une commande existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Vérifier les gestionnaires de paquets
Write-Host "🔍 Vérification des gestionnaires de paquets..." -ForegroundColor Yellow

if (Test-Command "choco") {
    Write-Host "✅ Chocolatey trouvé" -ForegroundColor Green
    Write-Host "🔄 Installation PostgreSQL avec Chocolatey..." -ForegroundColor Blue
    choco install postgresql -y
    $postgresInstalled = $true
}
elseif (Test-Command "scoop") {
    Write-Host "✅ Scoop trouvé" -ForegroundColor Green
    Write-Host "🔄 Installation PostgreSQL avec Scoop..." -ForegroundColor Blue
    scoop install postgresql
    $postgresInstalled = $true
}
else {
    Write-Host "❌ Aucun gestionnaire de paquets trouvé" -ForegroundColor Red
    Write-Host "📥 Installation manuelle requise :" -ForegroundColor Yellow
    Write-Host "1. Visitez : https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "2. Téléchargez l'installateur officiel" -ForegroundColor White
    Write-Host "3. Exécutez l'installateur" -ForegroundColor White
    Write-Host "4. Choisissez un mot de passe pour 'postgres'" -ForegroundColor White
    Write-Host "5. Notez le port (par défaut 5432)" -ForegroundColor White
    Write-Host ""
    Write-Host "Après installation, relancez ce script." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

if ($postgresInstalled) {
    Write-Host ""
    Write-Host "🔧 Configuration PostgreSQL..." -ForegroundColor Blue
    
    # Démarrer le service PostgreSQL
    Write-Host "🔄 Démarrage du service PostgreSQL..." -ForegroundColor Yellow
    $services = @("postgresql-x64-15", "postgresql-x64-14", "postgresql-x64-13", "postgresql")
    
    $serviceStarted = $false
    foreach ($service in $services) {
        try {
            Start-Service -Name $service -ErrorAction SilentlyContinue
            if (Get-Service -Name $service -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq "Running"}) {
                Write-Host "✅ Service $service démarré" -ForegroundColor Green
                $serviceStarted = $true
                break
            }
        }
        catch {
            # Continuer avec le service suivant
        }
    }
    
    if (-not $serviceStarted) {
        Write-Host "⚠️ Impossible de démarrer PostgreSQL automatiquement" -ForegroundColor Yellow
        Write-Host "💡 Démarrez manuellement via les Services Windows" -ForegroundColor Yellow
    }
    
    # Attendre que le service démarre
    Write-Host "⏳ Attente du démarrage du service..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Créer la base de données
    Write-Host "🗄️ Création de la base de données..." -ForegroundColor Blue
    try {
        & createdb -U postgres devdreco_soft 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Base de données 'devdreco_soft' créée" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Impossible de créer la base de données automatiquement" -ForegroundColor Yellow
            Write-Host "💡 Créez manuellement : psql -U postgres -c 'CREATE DATABASE devdreco_soft;'" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️ Erreur lors de la création de la base de données" -ForegroundColor Red
        Write-Host "💡 Créez manuellement : psql -U postgres -c 'CREATE DATABASE devdreco_soft;'" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 Installation PostgreSQL terminée !" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Prochaines étapes :" -ForegroundColor Cyan
    Write-Host "1. python manage.py migrate" -ForegroundColor White
    Write-Host "2. python manage.py createsuperuser" -ForegroundColor White
    Write-Host "3. python manage.py runserver" -ForegroundColor White
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour continuer"
}

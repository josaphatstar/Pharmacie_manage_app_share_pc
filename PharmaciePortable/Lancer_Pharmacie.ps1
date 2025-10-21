# Application Pharmacie Portable
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   APPLICATION PHARMACIE PORTABLE" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detecte: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Python n'est pas installe" -ForegroundColor Red
    Write-Host "Installez Python depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit
}

# Installer les dépendances
Write-Host "Installation des dependances..." -ForegroundColor Yellow
pip install streamlit pandas requests

# Lancer l'application
Write-Host "Lancement de l'application..." -ForegroundColor Green
python desktop_portable.py

Read-Host "Appuyez sur Entree pour quitter"

"""
Créateur de package portable sans PyInstaller
Crée un package complet qui fonctionne sur n'importe quel PC Windows
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_portable_package():
    """Crée un package portable complet"""
    
    print("Creation du package portable Pharmacie...")
    
    # Créer le dossier de distribution
    dist_dir = Path("PharmaciePortable")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    print("Copie des fichiers de l'application...")
    
    # Copier les fichiers Python essentiels
    essential_files = [
        'app.py',
        'db.py', 
        'utils.py',
        'desktop_portable.py'
    ]
    
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, dist_dir / file)
            print(f"  - {file}")
        else:
            print(f"  ERREUR: {file} manquant")
    
    # Créer un fichier batch de lancement
    batch_content = """@echo off
title Application Pharmacie
echo.
echo ========================================
echo   APPLICATION PHARMACIE PORTABLE
echo ========================================
echo.
echo Lancement de l'application...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe sur ce PC
    echo.
    echo Veuillez installer Python depuis: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Installer les dépendances si nécessaire
echo Verification des dependances...
pip install streamlit pandas requests >nul 2>&1

REM Lancer l'application
echo Demarrage de l'application...
python desktop_portable.py

pause
"""
    
    with open(dist_dir / "Lancer_Pharmacie.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    # Créer un fichier PowerShell alternatif
    ps_content = """# Application Pharmacie Portable
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
"""
    
    with open(dist_dir / "Lancer_Pharmacie.ps1", "w", encoding="utf-8") as f:
        f.write(ps_content)
    
    # Créer un fichier README complet
    readme_content = """# Application de Gestion de Pharmacie - Version Portable

## 📋 Prérequis
- **Windows 10/11**
- **Python 3.8 ou plus récent** (téléchargeable sur https://www.python.org/downloads/)

## 🚀 Installation et Utilisation

### Méthode 1 : Lancement automatique (Recommandée)
1. **Double-cliquez** sur `Lancer_Pharmacie.bat`
2. L'application va :
   - Vérifier que Python est installé
   - Installer automatiquement les dépendances
   - Lancer l'application dans votre navigateur

### Méthode 2 : Lancement manuel
1. Ouvrez un terminal (cmd ou PowerShell)
2. Naviguez vers ce dossier
3. Exécutez : `python desktop_portable.py`

### Méthode 3 : PowerShell (Alternative)
1. Clic droit sur `Lancer_Pharmacie.ps1`
2. Sélectionnez "Exécuter avec PowerShell"

## 💊 Fonctionnalités
- ✅ **Ajouter des produits** avec validation complète
- ✅ **Modifier des produits** existants
- ✅ **Supprimer des produits** avec confirmation
- ✅ **Rechercher des produits** par nom
- ✅ **Historique complet** des opérations
- ✅ **Code couleur** pour les dates d'expiration :
  - 🟢 Vert : Plus de 90 jours
  - 🟡 Jaune : 30-90 jours (à surveiller)
  - 🔴 Rouge : Moins de 30 jours (urgent)

## 📊 Données
- Vos données sont sauvegardées automatiquement
- Base de données SQLite locale (`pharmacy.db`)
- Pas d'installation de serveur externe requis

## 🔧 Dépannage

### "Python n'est pas reconnu"
1. Installez Python depuis https://www.python.org/downloads/
2. Cochez "Add Python to PATH" lors de l'installation
3. Redémarrez votre PC

### "Module 'streamlit' non trouvé"
- Le script d'installation installe automatiquement les dépendances
- Si le problème persiste, exécutez manuellement :
  ```
  pip install streamlit pandas requests
  ```

### "Port 8501 déjà utilisé"
- Fermez d'autres instances de l'application
- Ou redémarrez votre PC

## 📁 Fichiers inclus
- `app.py` - Application principale Streamlit
- `db.py` - Gestion de la base de données
- `utils.py` - Fonctions utilitaires
- `desktop_portable.py` - Lanceur portable
- `Lancer_Pharmacie.bat` - Script de lancement Windows
- `Lancer_Pharmacie.ps1` - Script PowerShell alternatif

## 🎯 Avantages de cette version portable
- ✅ **Aucune compilation** requise
- ✅ **Installation automatique** des dépendances
- ✅ **Compatible** avec tous les PC Windows
- ✅ **Facile à distribuer** (copier-coller le dossier)
- ✅ **Interface web** moderne et intuitive
- ✅ **Données locales** sécurisées

## 💡 Conseil
Cette version portable est **plus fiable** qu'un exécutable compilé car elle utilise Python directement. Elle s'adapte automatiquement à l'environnement du PC de destination.

---
**Développé avec Python, Streamlit et SQLite**
"""
    
    with open(dist_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Créer un fichier d'installation automatique
    install_content = """@echo off
title Installation Pharmacie Portable
echo.
echo ========================================
echo   INSTALLATION PHARMACIE PORTABLE
echo ========================================
echo.

REM Vérifier Python
echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Python n'est pas installe
    echo.
    echo Veuillez:
    echo 1. Aller sur https://www.python.org/downloads/
    echo 2. Telecharger et installer Python
    echo 3. COCHER "Add Python to PATH" lors de l'installation
    echo 4. Redemarrer votre PC
    echo 5. Relancer ce script
    echo.
    pause
    exit /b 1
)

echo Python detecte!
echo.

REM Installer les dépendances
echo Installation des dependances...
echo Cela peut prendre quelques minutes...
echo.

pip install streamlit pandas requests

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   INSTALLATION TERMINEE AVEC SUCCES!
    echo ========================================
    echo.
    echo Vous pouvez maintenant lancer l'application avec:
    echo - Lancer_Pharmacie.bat
    echo - ou python desktop_portable.py
    echo.
) else (
    echo.
    echo ERREUR lors de l'installation des dependances
    echo Essayez de relancer ce script en tant qu'administrateur
    echo.
)

pause
"""
    
    with open(dist_dir / "Installation.bat", "w", encoding="utf-8") as f:
        f.write(install_content)
    
    # Créer un fichier de test
    test_content = """@echo off
title Test Pharmacie Portable
echo.
echo ========================================
echo   TEST DE L'ENVIRONNEMENT
echo ========================================
echo.

echo Test de Python...
python --version
if %errorlevel% neq 0 (
    echo ERREUR: Python non detecte
    pause
    exit /b 1
)

echo.
echo Test des modules...
python -c "import streamlit; print('Streamlit: OK')" 2>nul || echo Streamlit: MANQUANT
python -c "import pandas; print('Pandas: OK')" 2>nul || echo Pandas: MANQUANT  
python -c "import sqlite3; print('SQLite: OK')" 2>nul || echo SQLite: MANQUANT
python -c "import requests; print('Requests: OK')" 2>nul || echo Requests: MANQUANT

echo.
echo Test des fichiers...
if exist "app.py" (echo app.py: OK) else (echo app.py: MANQUANT)
if exist "db.py" (echo db.py: OK) else (echo db.py: MANQUANT)
if exist "utils.py" (echo utils.py: OK) else (echo utils.py: MANQUANT)
if exist "desktop_portable.py" (echo desktop_portable.py: OK) else (echo desktop_portable.py: MANQUANT)

echo.
echo ========================================
echo   FIN DU TEST
echo ========================================
pause
"""
    
    with open(dist_dir / "Test_Environnement.bat", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"\nPackage portable cree dans: {dist_dir.absolute()}")
    print("\nFichiers inclus:")
    print("  - app.py, db.py, utils.py, desktop_portable.py (application)")
    print("  - Lancer_Pharmacie.bat (lancement principal)")
    print("  - Lancer_Pharmacie.ps1 (lancement PowerShell)")
    print("  - Installation.bat (installation des dependances)")
    print("  - Test_Environnement.bat (test de l'environnement)")
    print("  - README.txt (guide complet)")
    
    return True

def main():
    """Fonction principale"""
    print("Createur de package portable Pharmacie")
    print("=" * 50)
    
    # Vérifier que tous les fichiers nécessaires existent
    required_files = ['app.py', 'db.py', 'utils.py', 'desktop_portable.py']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"ERREUR Fichiers manquants: {', '.join(missing_files)}")
        return
    
    print("Creation du package portable...")
    
    if create_portable_package():
        print("\n" + "=" * 50)
        print("SUCCES: Package portable cree avec succes!")
        print("=" * 50)
        print("\nInstructions de distribution:")
        print("1. Copiez le dossier 'PharmaciePortable' sur le PC de destination")
        print("2. Sur le PC de destination, double-cliquez sur 'Installation.bat'")
        print("3. Puis double-cliquez sur 'Lancer_Pharmacie.bat'")
        print("\nLe package fonctionne sur n'importe quel PC Windows avec Python!")
        print("\nAvantages:")
        print("- Aucune compilation requise")
        print("- Installation automatique des dependances")
        print("- Plus fiable qu'un executable")
        print("- Facile a distribuer et utiliser")
    else:
        print("\nERREUR lors de la creation du package")

if __name__ == "__main__":
    main()

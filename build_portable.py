"""
Script de construction pour créer un exécutable portable
Version simplifiée qui évite les problèmes de PyInstaller
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

def install_pyinstaller():
    """Installe PyInstaller si nécessaire"""
    try:
        import PyInstaller
        print("PyInstaller deja installe")
        return True
    except ImportError:
        print("Installation de PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller installe avec succes")
            return True
        except subprocess.CalledProcessError:
            print("ERREUR: Impossible d'installer PyInstaller")
            return False

def build_simple_executable():
    """Construit un exécutable simple sans webview"""
    
    print("Construction de l'executable portable...")
    
    # Commande PyInstaller simplifiée
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name", "PharmaciePortable",
        "--add-data", "app.py;.",
        "--add-data", "db.py;.",
        "--add-data", "utils.py;.",
        "--hidden-import", "streamlit",
        "--hidden-import", "pandas",
        "--hidden-import", "sqlite3",
        "--hidden-import", "requests",
        "--hidden-import", "pathlib",
        "--hidden-import", "threading",
        "--hidden-import", "subprocess",
        "--hidden-import", "webbrowser",
        "--hidden-import", "datetime",
        "--hidden-import", "contextlib",
        "--hidden-import", "typing",
        "desktop_portable.py"
    ]
    
    try:
        print("Lancement de PyInstaller...")
        print("Ce processus peut prendre quelques minutes...")
        
        # Exécuter PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Construction reussie!")
        
        exe_path = Path('dist/PharmaciePortable.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Executable cree: {exe_path.absolute()}")
            print(f"Taille: {size_mb:.1f} MB")
            return True
        else:
            print("ERREUR: L'executable n'a pas ete cree")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"ERREUR lors de la construction: {e}")
        if e.stderr:
            print(f"Erreur detaillee: {e.stderr}")
        return False
    
    except FileNotFoundError:
        print("ERREUR: PyInstaller non trouve")
        return False

def create_portable_package():
    """Crée un package portable complet"""
    
    print("Creation du package portable...")
    
    # Créer le dossier de distribution
    dist_dir = Path("PharmaciePortable")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copier l'exécutable
    exe_path = Path("dist/PharmaciePortable.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "PharmaciePortable.exe")
        print("Executable copie dans le package")
    else:
        print("ERREUR: L'executable n'existe pas")
        return False
    
    # Créer un fichier README pour l'utilisateur final
    readme_content = """# Application de Gestion de Pharmacie - Version Portable

## Installation
Aucune installation requise ! Cette application est portable.

## Utilisation
1. Double-cliquez sur "PharmaciePortable.exe"
2. L'application se lance automatiquement
3. Votre navigateur s'ouvre avec l'interface
4. Utilisez l'interface pour gérer vos médicaments

## Fonctionnalités
- Ajouter des produits
- Modifier des produits existants
- Supprimer des produits
- Rechercher des produits
- Historique des opérations
- Code couleur pour les dates d'expiration

## Données
Vos données sont sauvegardées automatiquement dans une base de données locale.

## Support
Cette application fonctionne sur Windows 10/11 sans installation de logiciels supplémentaires.

Développé avec Python, Streamlit et SQLite.
"""
    
    with open(dist_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Créer un fichier batch pour faciliter le lancement
    batch_content = """@echo off
title Application Pharmacie
echo Lancement de l'application Pharmacie...
echo.
echo L'application va s'ouvrir dans votre navigateur.
echo Fermez cette fenetre pour arreter l'application.
echo.
PharmaciePortable.exe
pause
"""
    
    with open(dist_dir / "Lancer_Pharmacie.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print(f"Package portable cree dans: {dist_dir.absolute()}")
    return True

def main():
    """Fonction principale de construction"""
    print("Constructeur d'application portable pour Pharmacie")
    print("=" * 50)
    
    # Vérifier que tous les fichiers nécessaires existent
    required_files = ['desktop_portable.py', 'app.py', 'db.py', 'utils.py']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"ERREUR Fichiers manquants: {', '.join(missing_files)}")
        return
    
    # Installer PyInstaller si nécessaire
    if not install_pyinstaller():
        return
    
    # Construire l'exécutable
    print("\n" + "=" * 50)
    print("ETAPE 1: Construction de l'executable")
    print("=" * 50)
    
    if build_simple_executable():
        print("\n" + "=" * 50)
        print("ETAPE 2: Creation du package portable")
        print("=" * 50)
        
        if create_portable_package():
            print("\n" + "=" * 50)
            print("SUCCES: Application portable creee avec succes!")
            print("=" * 50)
            print("\nInstructions:")
            print("1. L'executable se trouve dans le dossier 'PharmaciePortable/'")
            print("2. Copiez le dossier 'PharmaciePortable' sur le PC de destination")
            print("3. Double-cliquez sur 'PharmaciePortable.exe' pour lancer l'application")
            print("\nL'application fonctionne sur n'importe quel PC Windows sans installation!")
            print("\nFichiers crees:")
            print("- PharmaciePortable/PharmaciePortable.exe (application principale)")
            print("- PharmaciePortable/README.txt (guide utilisateur)")
            print("- PharmaciePortable/Lancer_Pharmacie.bat (raccourci batch)")
        else:
            print("\nERREUR lors de la creation du package portable")
    else:
        print("\nERREUR lors de la construction de l'executable")

if __name__ == "__main__":
    main()

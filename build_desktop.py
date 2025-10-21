"""
Script de construction pour créer un exécutable Windows complet
Utilise PyInstaller pour packager l'application avec toutes les dépendances
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

def build_executable():
    """Construit l'exécutable avec PyInstaller en utilisant le fichier .spec"""
    
    print("Construction de l'application desktop...")
    
    # Vérifier que le fichier .spec existe
    if not Path("PharmacieGestion.spec").exists():
        print("ERREUR: Le fichier PharmacieGestion.spec n'existe pas")
        return False
    
    # Commande PyInstaller avec le fichier .spec
    cmd = [
        "pyinstaller",
        "--clean",  # Nettoyer le cache
        "--noconfirm",  # Pas de confirmation
        "PharmacieGestion.spec"
    ]
    
    try:
        print("Lancement de PyInstaller...")
        print("Ce processus peut prendre plusieurs minutes...")
        
        # Exécuter PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Construction reussie!")
        
        exe_path = Path('dist/PharmacieGestion.exe')
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

def create_distribution_package():
    """Crée un package de distribution complet"""
    
    print("Creation du package de distribution...")
    
    # Créer le dossier de distribution
    dist_dir = Path("Distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copier l'exécutable
    exe_path = Path("dist/PharmacieGestion.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "PharmacieGestion.exe")
        print("Executable copie dans le package")
    else:
        print("ERREUR: L'executable n'existe pas")
        return False
    
    # Créer un fichier README pour l'utilisateur final
    readme_content = """# Application de Gestion de Pharmacie

## Installation
Aucune installation requise ! Cette application est portable.

## Utilisation
1. Double-cliquez sur "PharmacieGestion.exe"
2. L'application se lance automatiquement
3. Utilisez l'interface pour gérer vos médicaments

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
    
    # Créer un raccourci (optionnel)
    shortcut_content = f"""[InternetShortcut]
URL=file:///{Path(dist_dir / 'PharmacieGestion.exe').absolute()}
IconFile={Path(dist_dir / 'PharmacieGestion.exe').absolute()}
IconIndex=0
"""
    
    with open(dist_dir / "Lancer_Pharmacie.url", "w", encoding="utf-8") as f:
        f.write(shortcut_content)
    
    print(f"Package de distribution cree dans: {dist_dir.absolute()}")
    return True

def main():
    """Fonction principale de construction"""
    print("Constructeur d'application desktop pour Pharmacie")
    print("=" * 50)
    
    # Vérifier que tous les fichiers nécessaires existent
    required_files = ['desktop_app.py', 'app.py', 'db.py', 'utils.py', 'PharmacieGestion.spec']
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
    
    if build_executable():
        print("\n" + "=" * 50)
        print("ETAPE 2: Creation du package de distribution")
        print("=" * 50)
        
        if create_distribution_package():
            print("\n" + "=" * 50)
            print("SUCCES: Application desktop creee avec succes!")
            print("=" * 50)
            print("\nInstructions:")
            print("1. L'executable se trouve dans le dossier 'Distribution/'")
            print("2. Copiez le dossier 'Distribution' sur le PC de destination")
            print("3. Double-cliquez sur 'PharmacieGestion.exe' pour lancer l'application")
            print("\nL'application fonctionne sur n'importe quel PC Windows sans installation!")
            print("\nFichiers crees:")
            print("- Distribution/PharmacieGestion.exe (application principale)")
            print("- Distribution/README.txt (guide utilisateur)")
            print("- Distribution/Lancer_Pharmacie.url (raccourci)")
        else:
            print("\nERREUR lors de la creation du package de distribution")
    else:
        print("\nERREUR lors de la construction de l'executable")

if __name__ == "__main__":
    main()

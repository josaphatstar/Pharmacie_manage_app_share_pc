"""
Script de test pour vérifier l'installation des dépendances
"""
import sys
import importlib

def test_imports():
    """Teste l'importation de tous les modules nécessaires"""
    modules_to_test = [
        'streamlit',
        'pandas', 
        'sqlite3',
        'requests',
        'pathlib',
        'threading',
        'subprocess',
        'webbrowser'
    ]
    
    print("=== Test des modules Python ===")
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"OK {module}")
        except ImportError:
            print(f"ERREUR {module} - MANQUANT")
            failed_imports.append(module)
    
    print("\n=== Test des modules optionnels ===")
    optional_modules = ['webview']
    
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"OK {module} - Disponible")
        except ImportError:
            print(f"ATTENTION {module} - Non disponible (utilisera le navigateur par defaut)")
    
    print(f"\n=== Résumé ===")
    if failed_imports:
        print(f"ERREUR Modules manquants: {', '.join(failed_imports)}")
        print("Installez-les avec: pip install " + " ".join(failed_imports))
        return False
    else:
        print("SUCCES Tous les modules requis sont disponibles!")
        return True

def test_files():
    """Teste la présence des fichiers nécessaires"""
    from pathlib import Path
    required_files = ['app.py', 'db.py', 'utils.py']
    
    print("\n=== Test des fichiers ===")
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"OK {file}")
        else:
            print(f"ERREUR {file} - MANQUANT")
            missing_files.append(file)
    
    if missing_files:
        print(f"ERREUR Fichiers manquants: {', '.join(missing_files)}")
        return False
    else:
        print("SUCCES Tous les fichiers requis sont presents!")
        return True

def main():
    """Fonction principale de test"""
    print("Test de l'environnement pour l'application desktop")
    print("=" * 50)
    
    from pathlib import Path
    
    # Test des imports
    imports_ok = test_imports()
    
    # Test des fichiers
    files_ok = test_files()
    
    print("\n" + "=" * 50)
    if imports_ok and files_ok:
        print("SUCCES Environnement pret pour l'application desktop!")
        print("\nPour lancer l'application:")
        print("  python desktop_app.py")
        print("\nOu version simplifiee:")
        print("  python desktop_simple.py")
    else:
        print("ERREUR Problemes detectes. Corrigez-les avant de continuer.")
    
    input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()

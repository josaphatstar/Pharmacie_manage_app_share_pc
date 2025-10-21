"""
Script de diagnostic pour pywebview
Identifie la version et teste les paramètres supportés
"""
import sys

def test_webview_version():
    """Teste la version de pywebview et ses capacités"""
    try:
        import webview
        print(f"Version de pywebview: {webview.__version__}")
        
        # Tester les paramètres supportés
        test_params = {
            'title': 'Test',
            'url': 'about:blank',
            'width': 800,
            'height': 600,
            'resizable': True,
            'fullscreen': False,
            'min_size': (400, 300),
            'on_top': False,
            'shadow': True,
            'focus': True,
            'minimizable': True,
            'maximizable': True
        }
        
        print("\nTest des parametres supportes:")
        
        # Tester chaque paramètre individuellement
        for param, value in test_params.items():
            try:
                # Créer une configuration de test avec juste ce paramètre
                test_config = {'title': 'Test', 'url': 'about:blank'}
                test_config[param] = value
                
                # Essayer de créer la fenêtre (sans la lancer)
                window = webview.create_window(**test_config)
                print(f"  OK: {param}")
                
            except Exception as e:
                print(f"  ERREUR: {param} - {str(e)}")
        
        return True
        
    except ImportError:
        print("pywebview n'est pas installe")
        return False
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        return False

def suggest_config():
    """Suggère une configuration optimale"""
    try:
        import webview
        version = webview.__version__
        print(f"\nConfiguration suggeree pour pywebview {version}:")
        
        # Configuration basique qui devrait fonctionner partout
        basic_config = {
            'title': 'Gestion de Pharmacie',
            'url': 'http://localhost:8501',
            'width': 1200,
            'height': 800,
            'resizable': True,
            'fullscreen': False
        }
        
        print("Configuration de base (compatible):")
        for key, value in basic_config.items():
            print(f"  '{key}': {value},")
        
        # Suggestions d'amélioration selon la version
        if version >= '4.0':
            print("\nParametres supplementaires disponibles:")
            additional_params = {
                'min_size': '(800, 600)',
                'on_top': 'False',
                'shadow': 'True'
            }
            for key, value in additional_params.items():
                print(f"  '{key}': {value},")
        
    except:
        print("Impossible de determiner la configuration optimale")

def main():
    """Fonction principale de diagnostic"""
    print("=== Diagnostic pywebview ===")
    print(f"Python: {sys.version}")
    
    if test_webview_version():
        suggest_config()
    else:
        print("\nPour installer pywebview:")
        print("pip install pywebview")
    
    print("\n=== Recommandations ===")
    print("1. Si pywebview fonctionne: utilisez desktop_app.py")
    print("2. Si pywebview pose probleme: utilisez desktop_simple.py")
    print("3. Pour maximum compatibilite: utilisez desktop_minimal.py")
    
    input("\nAppuyez sur Entree pour quitter...")

if __name__ == "__main__":
    main()

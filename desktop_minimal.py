"""
Version ultra-minimaliste de l'application desktop
Compatible avec toutes les versions de pywebview
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def run_streamlit_minimal():
    """Lance Streamlit avec la configuration minimale"""
    try:
        print("Demarrage de l'application Pharmacie...")
        
        # Lancer Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        process = subprocess.Popen(cmd)
        
        # Attendre que le serveur soit prêt
        print("Attente du demarrage du serveur...")
        time.sleep(5)
        
        # Essayer d'ouvrir avec webview minimal
        try:
            import webview
            print("Ouverture de l'interface native...")
            
            # Configuration ultra-minimaliste
            webview.create_window(
                title='Gestion de Pharmacie',
                url='http://localhost:8501',
                width=1200,
                height=800
            )
            webview.start()
            
        except Exception as webview_error:
            print(f"Webview non disponible ({webview_error})")
            print("Ouverture dans le navigateur par defaut...")
            webbrowser.open("http://localhost:8501")
            
            # Garder le processus en vie
            print("Application lancee dans le navigateur.")
            print("Fermez cette fenetre pour arreter l'application.")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nArret de l'application...")
                process.terminate()
        
        # Nettoyer
        if process.poll() is None:
            process.terminate()
            
    except Exception as e:
        print(f"Erreur: {e}")
        input("Appuyez sur Entree pour quitter...")

def main():
    """Fonction principale minimaliste"""
    if not Path("app.py").exists():
        print("ERREUR: Le fichier app.py n'est pas trouve.")
        input("Appuyez sur Entree pour quitter...")
        return
    
    run_streamlit_minimal()

if __name__ == "__main__":
    main()

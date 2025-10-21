"""
Application Desktop pour la Gestion de Pharmacie
Utilise Streamlit avec une interface webview intégrée
"""
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
import os

def run_streamlit():
    """Lance Streamlit en arrière-plan"""
    try:
        # Définir le port et l'adresse pour l'accès local uniquement
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        # Lancer Streamlit
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Erreur lors du lancement de Streamlit: {e}")
        return None

def wait_for_server(max_wait=30):
    """Attend que le serveur Streamlit soit prêt"""
    import requests
    
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8501", timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def open_webview() -> bool:
    """Tente d'ouvrir l'UI dans une fenêtre webview.

    Retourne True si la fenêtre native est utilisée, False si ouverture dans le navigateur.
    """
    try:
        import webview
        
        # Configuration de la fenêtre (version compatible)
        window_config = {
            'title': 'Gestion de Pharmacie',
            'url': 'http://localhost:8501',
            'width': 1200,
            'height': 800,
            'resizable': True,
            'fullscreen': False
        }
        
        # Créer et lancer la fenêtre
        webview.create_window(**window_config)
        webview.start(debug=False)
        return True
        
    except ImportError:
        print("Module 'webview' non trouve. Ouverture dans le navigateur par defaut...")
        webbrowser.open("http://localhost:8501")
        return False
    except Exception as e:
        print(f"Erreur lors de l'ouverture de la webview: {e}")
        webbrowser.open("http://localhost:8501")
        return False

def main():
    """Fonction principale"""
    print("Lancement de l'application Pharmacie Desktop...")
    
    # Vérifier que app.py existe
    if not Path("app.py").exists():
        print("ERREUR: Le fichier app.py n'est pas trouve dans le repertoire courant.")
        input("Appuyez sur Entree pour quitter...")
        return
    
    # Lancer Streamlit en arrière-plan
    print("Demarrage du serveur Streamlit...")
    streamlit_process = run_streamlit()
    
    if streamlit_process is None:
        print("ERREUR: Impossible de lancer Streamlit.")
        input("Appuyez sur Entree pour quitter...")
        return
    
    # Attendre que le serveur soit prêt
    print("Attente du demarrage du serveur...")
    if wait_for_server():
        print("Serveur pret!")
        
        # Ouvrir l'interface (webview si possible, sinon navigateur) 
        print("Ouverture de l'interface...")
        used_native_window = open_webview()
        
        if used_native_window:
            # Fermeture de la fenêtre native -> on arrête le serveur
            print("Arret du serveur...")
            streamlit_process.terminate()
            streamlit_process.wait()
            print("Application fermee.")
        else:
            # Navigateur: garder le serveur actif jusqu'à fermeture par l'utilisateur
            print("Application ouverte dans le navigateur. Fermez cette fenetre ou utilisez Ctrl+C pour arreter.")
            try:
                streamlit_process.wait()
            except KeyboardInterrupt:
                pass
            finally:
                print("Arret du serveur...")
                streamlit_process.terminate()
                streamlit_process.wait()
                print("Application fermee.")
    else:
        print("ERREUR: Le serveur n'a pas pu demarrer dans les temps.")
        streamlit_process.terminate()
        input("Appuyez sur Entree pour quitter...")

if __name__ == "__main__":
    main()

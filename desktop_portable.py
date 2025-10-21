"""
Version portable de l'application desktop
Utilise uniquement le navigateur par défaut (plus compatible)
"""
import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def run_streamlit_portable():
    """Lance Streamlit et ouvre le navigateur par défaut"""
    try:
        print("Demarrage de l'application Pharmacie Portable...")
        
        # Lancer Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        print("Ouverture de l'interface dans votre navigateur...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre un peu puis ouvrir le navigateur
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        print("=" * 60)
        print("APPLICATION PHARMACIE LANCEE!")
        print("=" * 60)
        print("L'application est disponible sur: http://localhost:8501")
        print("Votre navigateur devrait s'ouvrir automatiquement.")
        print("")
        print("Pour arreter l'application:")
        print("- Fermez cette fenetre")
        print("- Ou appuyez sur Ctrl+C")
        print("=" * 60)
        
        # Attendre que l'utilisateur ferme
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nArret de l'application...")
            process.terminate()
            print("Application fermee.")
            
    except Exception as e:
        print(f"Erreur: {e}")
        input("Appuyez sur Entree pour quitter...")

def main():
    """Fonction principale portable"""
    if not Path("app.py").exists():
        print("ERREUR: Le fichier app.py n'est pas trouve.")
        input("Appuyez sur Entree pour quitter...")
        return
    
    run_streamlit_portable()

if __name__ == "__main__":
    main()

"""
Version simplifiée de l'application desktop
Fallback si la version principale ne fonctionne pas
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def run_streamlit_simple():
    """Lance Streamlit et ouvre directement le navigateur"""
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
        
        print("Ouverture de l'interface dans votre navigateur...")
        process = subprocess.Popen(cmd)
        
        # Attendre un peu puis ouvrir le navigateur
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        print("Application lancee! Fermez cette fenetre pour arreter l'application.")
        print("L'application est disponible sur: http://localhost:8501")
        
        # Attendre que l'utilisateur ferme
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nArret de l'application...")
            process.terminate()
            
    except Exception as e:
        print(f"Erreur: {e}")
        input("Appuyez sur Entree pour quitter...")

def main():
    """Fonction principale simplifiée"""
    if not Path("app.py").exists():
        print("ERREUR: Le fichier app.py n'est pas trouve.")
        input("Appuyez sur Entree pour quitter...")
        return
    
    run_streamlit_simple()

if __name__ == "__main__":
    main()

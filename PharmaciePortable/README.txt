# Application de Gestion de Pharmacie - Version Portable

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

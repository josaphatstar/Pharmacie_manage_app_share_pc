# 🖥️ Application Desktop - Gestion de Pharmacie

## 📋 Vue d'ensemble

Cette version transforme votre application Streamlit en une **application desktop native** qui s'exécute dans une fenêtre Windows sans navigateur externe.

## 🚀 Installation et Lancement

### Option 1 : Lancement Direct (Recommandé pour le développement)

1. **Installer les dépendances :**
```bash
pip install -r requirements_desktop.txt
```

2. **Lancer l'application :**
```bash
python desktop_app.py
```

### Option 2 : Exécutable Windows (Pour la distribution)

1. **Construire l'exécutable :**
```bash
python build_desktop.py
```

2. **L'application sera créée dans le dossier `dist/PharmacieGestion.exe`**

## 🎯 Fonctionnalités

### ✅ **Avantages de la version desktop :**
- 🖥️ **Fenêtre native** Windows
- 🚀 **Lancement rapide** (pas d'installation de serveur)
- 🔒 **Données locales** (base SQLite intégrée)
- 🎨 **Interface préservée** (même design Streamlit)
- 📦 **Distribution simple** (un seul fichier .exe)

### 🎨 **Interface utilisateur :**
- **Taille de fenêtre** : 1200x800 pixels (redimensionnable)
- **Taille minimale** : 800x600 pixels
- **Icône** : 💊 (peut être personnalisée)
- **Titre** : "Gestion de Pharmacie"

## 🔧 Architecture Technique

### 📁 **Fichiers ajoutés :**
- `desktop_app.py` : Point d'entrée de l'application desktop
- `build_desktop.py` : Script de construction de l'exécutable
- `requirements_desktop.txt` : Dépendances supplémentaires
- `PharmacieGestion.spec` : Configuration PyInstaller (généré automatiquement)

### 🏗️ **Fonctionnement :**
1. **Lancement** du serveur Streamlit en local (port 8501)
2. **Attente** que le serveur soit prêt
3. **Ouverture** d'une fenêtre webview intégrée
4. **Nettoyage** automatique à la fermeture

## 🛠️ Personnalisation

### 🎨 **Modifier l'apparence :**
Éditez `desktop_app.py` ligne 35-47 :
```python
window_config = {
    'title': '💊 Votre Titre Personnalisé',
    'width': 1400,      # Largeur
    'height': 900,      # Hauteur
    'resizable': True,  # Redimensionnable
    # ... autres options
}
```

### 🖼️ **Ajouter une icône personnalisée :**
1. Placez votre fichier `.ico` dans le projet
2. Modifiez la ligne `'icon': 'votre_icone.ico'` dans `desktop_app.py`
3. Mettez à jour `build_desktop.py` si vous construisez un exécutable

## 📦 Distribution

### 🎯 **Pour distribuer l'application :**

1. **Construire l'exécutable :**
```bash
python build_desktop.py
```

2. **Créer un package :**
   - Copiez `PharmacieGestion.exe` dans un dossier
   - Copiez `app.py`, `db.py`, `utils.py` dans le même dossier
   - Créez un fichier `requirements.txt` avec juste `streamlit==1.37.1`

3. **Testez** l'exécutable sur une machine sans Python installé

## 🐛 Dépannage

### ❌ **Problèmes courants :**

1. **"Module webview non trouvé"**
   ```bash
   pip install pywebview
   ```

2. **"Port 8501 déjà utilisé"**
   - Fermez d'autres instances de Streamlit
   - Ou modifiez le port dans `desktop_app.py`

3. **"Application ne se lance pas"**
   - Vérifiez que `app.py` existe dans le même dossier
   - Lancez en mode console pour voir les erreurs

### 🔍 **Mode Debug :**
Pour voir les logs, modifiez `desktop_app.py` ligne 56 :
```python
webview.start(debug=True)  # Au lieu de False
```

## 🚀 Améliorations Futures

### 💡 **Suggestions d'amélioration :**
- 🔔 **Notifications système** pour les expirations
- 💾 **Sauvegarde automatique** des données
- 🎨 **Thèmes** (sombre/clair)
- 📊 **Rapports PDF** intégrés
- 🔄 **Mise à jour automatique**

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que toutes les dépendances sont installées
2. Lancez en mode debug pour voir les erreurs
3. Testez d'abord en mode développement avant de construire l'exécutable

---

**🎉 Votre application de gestion de pharmacie est maintenant prête à être utilisée comme application desktop !**

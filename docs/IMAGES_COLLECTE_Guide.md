# Configuration du Répertoire d'Images - Guide Simplifié

## Vue d'ensemble

L'application cy8_prompts_manager utilise maintenant un système simplifié pour la gestion des images, en se concentrant uniquement sur la variable **IMAGES_COLLECTE**.

## 📁 IMAGES_COLLECTE

**IMAGES_COLLECTE** est la variable d'environnement principale qui définit où les images générées par ComfyUI seront stockées.

### Valeur par défaut
- Si aucune configuration n'est trouvée : `./images` (répertoire "images" dans le dossier courant)
- L'application restaure automatiquement la dernière configuration utilisée

### Configuration via l'interface

1. **Ouvrir l'onglet Data**
   - Dans l'interface principale, cliquez sur l'onglet "Data"

2. **Section "Configuration du répertoire d'images"**
   - Vous verrez le chemin actuel affiché dans un champ en lecture seule
   - Le titre indique clairement "(IMAGES_COLLECTE)"

3. **Changer le répertoire**
   - Cliquez sur le bouton "Parcourir..."
   - Sélectionnez le nouveau répertoire dans la boîte de dialogue
   - Le chemin s'affiche immédiatement dans l'interface

4. **Appliquer les changements**
   - Cliquez sur "✓ Appliquer le changement"
   - La variable d'environnement IMAGES_COLLECTE est mise à jour
   - La configuration est sauvegardée dans vos préférences utilisateur

5. **Actions supplémentaires**
   - **📁 Créer le répertoire** : Crée le répertoire s'il n'existe pas encore
   - **🗂️ Ouvrir dans l'explorateur** : Ouvre le répertoire dans l'explorateur de fichiers

## 💾 Persistance des préférences

- La configuration est automatiquement sauvegardée dans vos préférences utilisateur
- Emplacement : `%APPDATA%\cy8_prompts_manager\preferences.json`
- La configuration est restaurée automatiquement au prochain démarrage

## 🔧 Configuration technique

### Variable d'environnement
```python
import os
images_path = os.getenv("IMAGES_COLLECTE")
```

### Préférences utilisateur
```python
# Sauvegarder
user_prefs.set_preference("images_collecte_path", "/chemin/vers/images")

# Récupérer
saved_path = user_prefs.get_preference("images_collecte_path")
```

## 🧪 Tests

Le système inclut des tests automatisés pour vérifier :
- L'initialisation correcte de IMAGES_COLLECTE
- La synchronisation entre l'interface et la variable d'environnement
- La sauvegarde dans les préférences utilisateur
- La création de répertoires

Lancer les tests :
```bash
python test_images_simple.py
```

## 📝 Notes importantes

1. **Simplicité** : Seule IMAGES_COLLECTE est gérée, les autres variables (IMAGES_TRASH, IMAGES_CENTRAL) ne sont plus dans l'interface
2. **Compatibilité** : Compatible avec les configurations ComfyUI existantes
3. **Flexibilité** : Peut être configuré par variable d'environnement ou via l'interface
4. **Persistance** : La configuration survit aux redémarrages de l'application

## ✅ Avantages de cette approche

- **Interface simplifiée** : Une seule configuration à gérer
- **Moins d'erreurs** : Moins de chemins à configurer = moins de risques d'erreur
- **Focus** : Concentration sur l'essentiel (où stocker les images générées)
- **Maintenabilité** : Code plus simple et plus facile à maintenir

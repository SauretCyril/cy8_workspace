# Amélioration du Bouton "Ouvrir Dossier Images"

## 📋 Résumé

Amélioration de la fonction `open_images_folder()` pour gérer les dossiers introuvables et permettre la sélection d'un nouveau répertoire.

## 🎯 Problème

Lorsque le dossier d'images configuré dans `IMAGES_COLLECTE` n'existait pas, l'application affichait simplement un message d'avertissement sans proposer de solution. L'utilisateur devait manuellement modifier la configuration.

## ✅ Solution Implémentée

### Nouveau Comportement

1. **Si le dossier existe** → Ouvrir directement (comportement inchangé)

2. **Si le dossier n'existe pas** :
   - ❓ **Popup de confirmation** : "Dossier introuvable. Voulez-vous choisir un autre dossier ?"
   
   - Si OUI :
     - 📁 **Sélecteur de dossier** s'ouvre
     - Le nouveau dossier est ouvert immédiatement
     - 💾 **Proposition de sauvegarde** : "Voulez-vous définir ce dossier comme dossier par défaut ?"
     
   - Si sauvegarde acceptée :
     - ✏️ Mise à jour du fichier `.env`
     - 🔄 Mise à jour de la variable d'environnement pour la session en cours
     - ✅ Confirmation de la sauvegarde

## 🔧 Fonctionnalités Détaillées

### 1. Détection du Dossier Manquant

```python
if not os.path.exists(images_path):
    # Proposer de choisir un nouveau dossier
    result = messagebox.askyesno(...)
```

### 2. Sélection Interactive

- Utilise `filedialog.askdirectory()`
- Démarre depuis le répertoire utilisateur
- Interface native du système d'exploitation

### 3. Sauvegarde dans `.env`

La fonction gère intelligemment le fichier `.env` :

- **Si le fichier existe** : Remplace la ligne `IMAGES_COLLECTE=...` existante
- **Si le fichier n'existe pas** : Crée un nouveau fichier `.env`
- **Encodage UTF-8** pour supporter tous les caractères de chemin

### 4. Mise à Jour de la Session

```python
os.environ["IMAGES_COLLECTE"] = new_path
```

La variable d'environnement est mise à jour immédiatement sans redémarrer l'application.

## 📍 Emplacements

### Fichier Modifié
- `src/cy8_prompts_manager_main.py`
- Fonction : `open_images_folder()` (ligne ~4407)

### Boutons Concernés

1. **Onglet "Images"** → Bouton "Ouvrir dossier images"
2. **Sous-onglet "Galerie complète"** → Bouton "📁 Ouvrir dossier"

Les deux boutons utilisent la même fonction et bénéficient de l'amélioration.

## 🎨 Interface Utilisateur

### Séquence de Popups

```
┌─────────────────────────────────────┐
│ Dossier introuvable                 │
│ ─────────────────────────────────── │
│ Le dossier n'existe pas:            │
│ E:/Comfyui_G11/ComfyUI/output       │
│                                     │
│ Voulez-vous choisir un autre        │
│ dossier d'images ?                  │
│                                     │
│        [Non]     [Oui]              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Sélectionner le dossier d'images    │
│ ─────────────────────────────────── │
│ [Explorateur de fichiers natif]     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Sauvegarder le chemin               │
│ ─────────────────────────────────── │
│ Voulez-vous définir ce dossier      │
│ comme dossier par défaut ?          │
│                                     │
│ Dossier: G:/Images/ComfyUI          │
│                                     │
│ (Créera/modifiera la variable       │
│  d'environnement IMAGES_COLLECTE)   │
│                                     │
│        [Non]     [Oui]              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Succès                              │
│ ─────────────────────────────────── │
│ Le dossier d'images par défaut      │
│ a été défini sur:                   │
│ G:/Images/ComfyUI                   │
│                                     │
│ Sauvegardé dans:                    │
│ G:/G_WCS/cy8_workspace/.env         │
│                                     │
│             [OK]                    │
└─────────────────────────────────────┘
```

## 🛡️ Gestion des Erreurs

### Erreurs Interceptées

1. **Dossier inexistant** → Proposition de sélection
2. **Annulation de sélection** → Retour silencieux (pas d'erreur)
3. **Erreur d'écriture .env** → Message d'avertissement (le dossier reste ouvert)
4. **Erreur générale** → Popup d'erreur avec détails

### Robustesse

- ✅ Gestion des chemins avec espaces
- ✅ Gestion des caractères spéciaux
- ✅ Gestion des chemins absolus et relatifs
- ✅ Compatible Windows, macOS et Linux

## 📝 Format du Fichier `.env`

```env
IMAGES_COLLECTE=G:/Images/ComfyUI
# Autres variables...
```

- Une ligne par variable
- Format : `CLE=valeur`
- Pas de guillemets nécessaires
- Encodage UTF-8

## 🔄 Impact sur les Autres Fonctions

### Fonctions Bénéficiaires

Toutes les fonctions qui utilisent `os.getenv("IMAGES_COLLECTE")` bénéficient de cette amélioration :

- `refresh_gallery()` - Chargement de la galerie
- `scan_images_directory()` - Scan du répertoire
- `add_output_images_to_database()` - Ajout automatique
- Etc.

## 🧪 Tests Recommandés

### Scénarios de Test

1. ✅ **Dossier existant** : Vérifier ouverture directe
2. ✅ **Dossier inexistant + Annulation** : Vérifier retour sans erreur
3. ✅ **Dossier inexistant + Sélection** : Vérifier ouverture du nouveau dossier
4. ✅ **Sauvegarde acceptée** : Vérifier création/modification de `.env`
5. ✅ **Sauvegarde refusée** : Vérifier ouverture sans sauvegarde
6. ✅ **Fichier .env existant** : Vérifier remplacement de ligne
7. ✅ **Fichier .env inexistant** : Vérifier création

### Test Manuel

```bash
# 1. Tester avec dossier inexistant
# Modifier temporairement .env ou supprimer le dossier

# 2. Lancer l'application
python src/cy8_prompts_manager_main.py

# 3. Cliquer sur "Ouvrir dossier images"
# 4. Accepter de choisir un nouveau dossier
# 5. Sélectionner un dossier valide
# 6. Accepter de sauvegarder
# 7. Vérifier le fichier .env créé/modifié
```

## 📊 Avantages

✅ **Expérience utilisateur améliorée** : Résolution guidée du problème  
✅ **Flexibilité** : Changement rapide de répertoire sans éditer les fichiers  
✅ **Persistance** : Configuration sauvegardée pour les prochaines sessions  
✅ **Sécurité** : Validation de l'existence avant sauvegarde  
✅ **Feedback clair** : Messages informatifs à chaque étape  

## 🔜 Améliorations Futures Possibles

1. **Historique des dossiers** : Liste des derniers dossiers utilisés
2. **Validation du contenu** : Vérifier que le dossier contient des images
3. **Configuration multi-environnement** : Un dossier par environnement ComfyUI
4. **Interface de gestion** : Panneau de configuration des chemins
5. **Import de configuration** : Détecter automatiquement les chemins ComfyUI

## 📅 Historique

- **2025-10-09** : Implémentation initiale (commit à venir)
  - Ajout de la sélection interactive
  - Sauvegarde automatique dans `.env`
  - Gestion complète des erreurs

---

**Note** : Cette amélioration s'inscrit dans l'effort continu d'amélioration de l'UX de cy8_prompts_manager.

# 📖 GUIDE UTILISATION - GROUPE PRÉFÉRENCES

## 🎯 Comment utiliser le nouveau groupe Préférences

### 🚀 **Accès aux préférences**

1. **Localisation** : Dans le ruban principal de l'application
2. **Groupe** : "Préférences" (à côté du groupe "Base de données")
3. **Bouton** : "⚙️ Paramètres"

### 📊 **Interface des préférences**

#### **Ouverture de la popup :**
- Cliquez sur **"⚙️ Paramètres"** dans le ruban
- Une fenêtre popup s'ouvre (800x600 pixels)
- La fenêtre est **modale** (bloque l'interaction avec l'application principale)

#### **Contenu affiché :**
```
Variable                  | Valeur                    | Description
-------------------------|---------------------------|---------------------------
version                  | 1.0                       | Version des préférences
created_at               |                           | Date de création
last_updated             | 2025-10-11T...            | Dernière mise à jour
error_solutions_directory| g:/temp                   | Répertoire des solutions d'erreurs
last_database_path       | G:\tmp\prompts_manager.db | Dernière base de données utilisée
window_geometry          | 1858x1037+244+121         | Géométrie de la fenêtre
recent_databases         |                           | Bases de données récentes
```

## ✏️ **Édition des valeurs**

### **Modifier une préférence :**
1. **Double-cliquez** sur la ligne à modifier
2. Une fenêtre d'édition s'ouvre avec la valeur actuelle
3. Modifiez la valeur dans le champ de saisie
4. **Cliquez "💾 Sauvegarder"** ou appuyez sur **Entrée**
5. **Cliquez "❌ Annuler"** ou appuyez sur **Échap** pour annuler

### **Types supportés :**
- **📝 Texte** : Chaînes de caractères (chemins, noms, etc.)
- **🔢 Nombres entiers** : Validation automatique
- **🔢 Nombres décimaux** : Validation automatique
- **✅ Booléens** : `true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off`

### **Exemples d'édition :**
```
Variable: error_solutions_directory
Valeur actuelle: g:/temp
Nouvelle valeur: D:/Solutions_ComfyUI

Variable: window_geometry
Valeur actuelle: 1858x1037+244+121
Nouvelle valeur: 1920x1080+0+0
```

## 💾 **Gestion des modifications**

### **Boutons disponibles :**
- **💾 Sauvegarder** : Enregistre TOUTES les modifications sur disque
- **🔄 Recharger** : Recharge les valeurs depuis les fichiers sur disque (annule les modifications non sauvegardées)
- **❌ Fermer** : Ferme la fenêtre (demande confirmation si modifications non sauvegardées)

### **Process de sauvegarde :**
1. Effectuez toutes vos modifications
2. Cliquez **"💾 Sauvegarder"**
3. Confirmation affichée : "Préférences sauvegardées avec succès!"
4. La fenêtre se ferme automatiquement

## ⚠️ **Bonnes pratiques**

### **Préférences importantes :**
- **`error_solutions_directory`** : Répertoire où sont stockées les solutions d'erreurs ComfyUI
- **`last_database_path`** : Dernière base de données utilisée (rechargée au démarrage)
- **`window_geometry`** : Position et taille de la fenêtre (sauvegardée automatiquement)

### **Précautions :**
- **Vérifiez les chemins** : Assurez-vous que les répertoires existent
- **Format des booléens** : Utilisez `true`/`false` pour les valeurs logiques
- **Sauvegardez régulièrement** : Les modifications ne sont persistantes qu'après sauvegarde

### **En cas d'erreur :**
- **Type incorrect** : Message d'erreur spécifique affiché
- **Chemin invalide** : L'application peut ne pas fonctionner correctement
- **Corruption** : Utilisez **"🔄 Recharger"** pour restaurer depuis le disque

## 🔧 **Variables détaillées**

### **Préférences système :**
- `version` : Version du format des préférences (lecture seule recommandée)
- `created_at` : Date de première création des préférences
- `last_updated` : Mise à jour automatique à chaque sauvegarde

### **Préférences fonctionnelles :**
- `error_solutions_directory` : Répertoire pour stocker les solutions d'erreurs analysées par Mistral
- `last_database_path` : Base de données chargée automatiquement au démarrage
- `window_geometry` : Position et taille de la fenêtre (format: largeurxhauteur+x+y)
- `recent_databases` : Liste des bases récemment utilisées (format JSON)

## 💡 **Conseils d'utilisation**

### **Optimisation :**
- **Répertoire solutions** : Utilisez un répertoire facilement accessible (ex: `D:/ComfyUI_Solutions`)
- **Géométrie fenêtre** : Adaptez selon votre résolution d'écran
- **Base de données** : Gardez un chemin court et sans espaces

### **Maintenance :**
- **Sauvegarde régulière** : Les préférences sont dans `%APPDATA%\cy8_prompts_manager\`
- **Nettoyage** : Supprimez les bases non utilisées de `recent_databases`
- **Migration** : Copiez les fichiers de préférences entre machines

---

**🎉 Le système de préférences vous permet maintenant de personnaliser entièrement votre environnement de travail !**

Toutes vos modifications sont sauvegardées localement et restaurées automatiquement au démarrage. ✨

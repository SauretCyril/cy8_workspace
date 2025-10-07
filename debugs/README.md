# 🐛 Répertoire Debugs

## 📋 Contenu

Ce répertoire contient les **fichiers de débogage** pour le projet `cy8_prompts_manager`.

### 📁 Fichiers présents :

- **`debug_extraction.py`** : Débogage du système d'extraction de configuration
- **`debug_extra_paths.py`** : Débogage des chemins extra ComfyUI et identification d'environnement

### 🎯 Objectif

Les scripts de débogage permettent de :
- 🔍 **Diagnostiquer les problèmes** spécifiques
- 🧪 **Isoler les bugs** dans des composants particuliers
- 📊 **Analyser le comportement** détaillé des fonctions
- 🛠️ **Développer des correctifs** ciblés

### 🚀 Utilisation

```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer un script de débogage
python debugs/debug_extraction.py
python debugs/debug_extra_paths.py
```

### ⚠️ Attention

Ces fichiers sont destinés au **développement et au débogage**. Ils peuvent :
- Modifier des fichiers temporaires
- Afficher des informations sensibles
- Nécessiter des configurations spécifiques
- Avoir des dépendances particulières

### 📝 Recommandations

- Utilisez ces scripts dans un **environnement de développement**
- Sauvegardez vos données avant exécution
- Vérifiez les prérequis mentionnés dans chaque script

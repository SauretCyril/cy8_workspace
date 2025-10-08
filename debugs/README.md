# 🐛 Répertoire Debugs

# 🐛 Répertoire Debugs

## 📋 Contenu

Ce répertoire contient les **fichiers de débogage et diagnostic** pour le projet `cy8_prompts_manager`.

## 🎯 Scripts principaux

### debug_environment.py
Diagnostic complet de l'environnement ComfyUI.

```bash
python debugs/debug_environment.py
```

**Vérifie :**
- Configuration de l'environnement ComfyUI
- Variables d'environnement
- Chemins des modèles
- Connexion au serveur
- Base de données

### diagnostic_rag_simple.py
Test rapide du système RAG (Retrieval-Augmented Generation).

```bash
python debugs/diagnostic_rag_simple.py
```

**Vérifie :**
- Disponibilité de ChromaDB
- Embeddings (sentence-transformers)
- Indexation de documents
- Recherche sémantique

### diagnostic_rag_apprentissage.py
Diagnostic approfondi de l'apprentissage du RAG.

```bash
python debugs/diagnostic_rag_apprentissage.py
```

### fix_rag_environment.py
Script de correction pour les problèmes d'environnement RAG.

```bash
python debugs/fix_rag_environment.py
```

## � Scripts de diagnostic spécialisés

- `debug_extra_paths.py` - Analyse des extra_model_paths.yaml
- `debug_extraction.py` - Debug de l'extraction de configuration
- `debug_comfyui_direct.py` - Test de connexion directe ComfyUI
- `debug_custom_node_location.py` - Localisation des custom nodes
- `diagnose_environment.py` - Diagnostic d'environnement
- `diagnose_multiple_comfyui.py` - Détection d'environnements multiples
- `diagnose_paths_detailed.py` - Analyse détaillée des chemins

## 🧪 Scripts de test de diagnostic

Tests spécifiques qui peuvent aussi servir au debug :

- `test_app_identification.py` - Test identification d'application
- `test_app_rag_quick.py` - Test RAG rapide
- `test_config_detection.py` - Test détection de configuration
- `test_custom_node_debug.py` - Debug des custom nodes
- `test_environment_sync.py` - Test synchronisation d'environnement
- `test_identification_complete.py` - Test identification complète
- `test_rag_fixes.py` - Test des corrections RAG

### 📁 Fichiers hérités :

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

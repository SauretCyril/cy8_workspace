# 🧠 Guide d'utilisation du système RAG ComfyUI

## Vue d'ensemble

Le système RAG (Retrieval-Augmented Generation) vous permet de surveiller et optimiser votre serveur ComfyUI grâce à une mémoire intelligente des erreurs, succès et contraintes système.

## 🎯 Objectifs du RAG

- **Mémoriser vos erreurs** et leurs solutions pour éviter de répéter les mêmes problèmes
- **Surveiller l'état du serveur** ComfyUI et détecter les patterns problématiques
- **Gérer vos contraintes** matérielles et logicielles (VRAM, versions, compatibilités)
- **Optimiser les performances** en se basant sur l'historique des succès/échecs
- **Faciliter l'installation** de custom nodes en prévenant les conflits

## 📁 Architecture par environnement

Chaque environnement ComfyUI a sa propre base de données RAG :

```
H:\comfyui\G11_01\analyses\
├── vector_db\           # Base vectorielle ChromaDB
├── constraints.db       # Base SQLite des contraintes
└── analyse_*.txt       # Analyses Mistral sauvegardées
```

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```bash
pip install chromadb sentence-transformers
```

### 2. Initialisation avec des données d'exemple

```bash
python demo_rag_system.py
```

### 3. Utilisation dans l'application

1. Lancez l'application : `python src/cy8_prompts_manager_main.py`
2. Allez dans l'onglet **"💬 Chat"**
3. Le RAG se présente automatiquement avec l'état de votre serveur

## 💬 Interface Chat

### Message de bienvenue automatique

Au premier lancement, le RAG analyse votre environnement et affiche :
- État actuel du serveur ComfyUI
- Contraintes système actives
- Erreurs récurrentes détectées
- Recommandations d'optimisation

### Actions rapides disponibles

| Bouton | Description |
|--------|-------------|
| 📊 **État du serveur** | Résumé complet de l'état actuel |
| ⚠️ **Erreurs récurrentes** | Liste des problèmes les plus fréquents |
| 🎯 **Optimisations** | Recommandations d'amélioration |
| 🔧 **Contraintes** | Vos limitations système configurées |
| 📝 **Ajouter contrainte** | Dialogue pour nouvelle contrainte |
| 🔍 **Rechercher erreur** | Recherche dans l'historique |

### Exemples de questions

- *"J'ai une erreur de mémoire VRAM, que faire ?"*
- *"Comment optimiser mes générations SDXL ?"*
- *"Quels custom nodes sont compatibles avec ma config ?"*
- *"Rappelle-moi pourquoi je ne peux pas utiliser numpy 2.x"*

## 🚫 Gestion des contraintes système

### Types de contraintes supportés

- **package_version** : Versions de packages (numpy, torch, etc.)
- **hardware_limitation** : Limitations matérielles (VRAM, CPU)
- **memory_limit** : Limites mémoire spécifiques
- **gpu_compatibility** : Compatibilité GPU/CUDA
- **python_version** : Version Python requise
- **custom_node_conflict** : Incompatibilités entre custom nodes

### Exemples de contraintes typiques

```
numpy_version: 1.24.4
→ "Ne peut pas passer à numpy 2.x - incompatibilité avec custom nodes existants"

vram_limit: 12GB
→ "RTX 3060 Ti - limitation pour les gros modèles SDXL"

batch_size_limit: 2
→ "Limitation batch size pour éviter OOM"
```

## 🔍 Indexation automatique

### Analyses Mistral intégrées

Chaque fois que vous sauvegardez une analyse Mistral AI depuis l'onglet Log, le RAG :

1. **Indexe automatiquement** le contenu dans la base vectorielle
2. **Extrait les erreurs** et solutions pour l'historique
3. **Met à jour l'état** du serveur
4. **Crée des embeddings** pour la recherche sémantique

### Structure des données indexées

```json
{
  "timestamp": "2025-10-04T19:30:00",
  "type": "log_analysis",
  "summary": "Résumé de l'analyse",
  "errors": [
    {
      "type": "memory_error",
      "message": "CUDA out of memory...",
      "solution": "Réduire batch_size ou utiliser model offloading"
    }
  ],
  "successes": ["Custom nodes chargés correctement"],
  "recommendations": ["Activer attention offloading"]
}
```

## 🔎 Recherche intelligente

### Recherche sémantique

Le RAG utilise des embeddings pour comprendre le sens de vos questions :

- *"problème mémoire"* → trouve les erreurs VRAM, OOM, etc.
- *"lenteur generation"* → trouve les optimisations de performance
- *"conflit nodes"* → trouve les incompatibilités custom nodes

### Scoring de pertinence

Les résultats incluent un score de similiarité :
- **80%+** : Très pertinent, solution probable
- **50-79%** : Pertinent, contexte utile
- **30-49%** : Peu pertinent, à considérer
- **<30%** : Non pertinent

## 📊 Monitoring d'état

### États du serveur

- **healthy** : Aucune erreur détectée
- **warning** : Quelques erreurs, mais plus de succès
- **problematic** : Plus d'erreurs que de succès

### Indicateurs de santé

- Fréquence des erreurs récurrentes
- Temps depuis la dernière analyse réussie
- Nombre de contraintes actives
- Évolution des performances

## 🛠️ Maintenance et optimisation

### Nettoyage périodique

```python
# Supprimer les anciennes analyses (optionnel)
rag.cleanup_old_data(days=30)

# Réindexer après modifications
rag.reindex_all_analyses()
```

### Performance

- **Base vectorielle** : Optimisée pour <1000 analyses
- **Recherche** : <200ms pour requêtes typiques
- **Stockage** : ~50MB par environnement avec 100 analyses

## 🎯 Cas d'usage typiques

### 1. Installation d'un nouveau custom node

Avant installation :
1. Demandez au RAG : *"Compatible avec ComfyUI-Manager ?"*
2. Vérifiez les contraintes système
3. Recherchez des conflits similaires dans l'historique

### 2. Optimisation des performances

1. Analysez l'état actuel : Action **📊 État du serveur**
2. Consultez l'historique : *"Quelles optimisations ont fonctionné ?"*
3. Appliquez les recommandations du RAG

### 3. Résolution d'erreurs

1. Copiez le message d'erreur dans le chat
2. Le RAG recherche des problèmes similaires
3. Applique les solutions qui ont déjà fonctionné

### 4. Mise à jour de ComfyUI

Avant mise à jour :
1. Consultez les contraintes : Action **🔧 Contraintes**
2. Documentez l'état actuel : Action **📊 État du serveur**
3. Créez un point de restauration de configuration

## 🚨 Dépannage

### RAG non disponible

Si le message "RAG non disponible" s'affiche :

```bash
pip install chromadb sentence-transformers
```

### Erreurs d'indexation

Vérifiez les permissions du répertoire :
```
H:\comfyui\{environment_id}\analyses\
```

### Performance lente

- Réduisez la limite de recherche dans les paramètres
- Nettoyez les anciennes données
- Vérifiez l'espace disque disponible

## 🔬 Mode développeur

### Tests et validation

```bash
# Test d'intégration complet
python tests/test_rag_integration.py

# Démonstration avec données réalistes
python demo_rag_system.py
```

### API programmatique

```python
from cy8_rag_manager import RAGManager

# Initialisation
rag = RAGManager(db_manager, environment_id="G11_01")

# Ajout contrainte
rag.add_constraint("numpy_version", "1.24.4", "Stabilité custom nodes")

# Recherche
results = rag.search_similar_issues("erreur VRAM", limit=5)

# État serveur
status = rag.get_server_status_summary()
```

---

## 💡 Conseils d'utilisation

1. **Documentez vos contraintes** dès l'installation
2. **Analysez régulièrement** vos logs avec Mistral AI
3. **Consultez le RAG** avant toute modification importante
4. **Partagez vos solutions** en documentant les résolutions
5. **Maintenez à jour** vos contraintes système

Le RAG apprend de votre utilisation et devient plus pertinent avec le temps ! 🚀

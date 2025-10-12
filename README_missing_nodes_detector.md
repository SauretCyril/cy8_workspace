# 🔍 Système de Détection de Nodes Manquants ComfyUI

Ce système permet de détecter automatiquement les custom nodes manquants dans un workflow ComfyUI.

## 📁 Architecture

### 1. **Classe principale** : `cy8_missing_nodes_detector.py`
- Analyse les workflows JSON ComfyUI
- Scanne les custom nodes disponibles
- Détecte les nodes manquants
- Génère des rapports détaillés

### 2. **Custom Node ComfyUI** : `missing_nodes_detector_node.py`
- Node ComfyUI intégrable dans l'interface graphique
- Auto-détection des chemins
- Sorties formatées (rapport, JSON, statut)

### 3. **Intégration API** : Méthodes dans `ComfyUICustomNodeCaller`
- `detect_missing_nodes()` : Détection via API
- `print_missing_nodes_report()` : Affichage formaté

## 🚀 Installation

### Étape 1: Copier les fichiers
```bash
# Copier vers ComfyUI
cp src/cy8_missing_nodes_detector.py /path/to/ComfyUI/custom_nodes/
cp custom_nodes/missing_nodes_detector_node.py /path/to/ComfyUI/custom_nodes/
```

### Étape 2: Redémarrer ComfyUI
```bash
# Redémarrer ComfyUI pour charger le nouveau custom node
python main.py  # Dans le répertoire ComfyUI
```

## 🔧 Utilisation

### A. Via l'API Python

```python
from cy8_comfyui_customNode_call import ComfyUICustomNodeCaller

# Créer le caller
with ComfyUICustomNodeCaller() as caller:
    # Détecter les nodes manquants
    result = caller.detect_missing_nodes(
        workflow_path="mon_workflow.json",
        custom_nodes_dir="ComfyUI/custom_nodes",
        auto_detect_paths=True  # Auto-détection des chemins
    )

    # Afficher le rapport
    caller.print_missing_nodes_report(result)
```

### B. Via la classe directe

```python
from cy8_missing_nodes_detector import MissingNodesDetector

# Créer le détecteur
detector = MissingNodesDetector()

# Analyser un workflow
result = detector.detect_missing_nodes(
    workflow_path="workflow.json",
    custom_nodes_dir="ComfyUI/custom_nodes"
)

# Générer le rapport
if not result["error"]:
    report = detector.generate_report(result)
    print(report)
```

### C. Via l'interface ComfyUI

1. **Ajouter le node** : Cherchez "Missing Nodes Detector" dans ComfyUI
2. **Configurer** :
   - `workflow_path`: Chemin vers votre workflow JSON
   - `custom_nodes_dir`: Chemin vers custom_nodes
   - `auto_detect_paths`: Laissez sur True pour l'auto-détection
3. **Exécuter** : Le node retourne un rapport détaillé

## 📊 Format des résultats

### Sortie principale
```json
{
  "error": false,
  "status": "SUCCESS|WARNING|ERROR",
  "report": "Rapport textuel détaillé",
  "missing_data": {
    "missing_nodes": ["Node1", "Node2"],
    "summary": {
      "total_nodes": 10,
      "builtin_nodes": 5,
      "custom_nodes": 5,
      "missing_nodes": 2,
      "available_custom": 3
    }
  }
}
```

### Rapport textuel
```
🔍 RAPPORT D'ANALYSE DES NODES
==================================================
📄 Workflow: mon_workflow.json
📁 Custom nodes: ComfyUI/custom_nodes

📊 RÉSUMÉ:
   • Total nodes utilisés: 10
   • Built-in ComfyUI: 5
   • Custom nodes: 5
   • Custom disponibles: 3
   • Nodes manquants: 2

🧩 NODES MANQUANTS:
   ❌ AdvancedControlNet
   ❌ IPAdapterPlus

👉 Action recommandée:
   • Installer via ComfyUI-Manager
   • Ou rechercher manuellement les custom nodes
```

## 🔍 Fonctionnalités

### ✅ **Détection automatique**
- Scan complet du répertoire custom_nodes
- Extraction des NODE_CLASS_MAPPINGS
- Auto-détection des chemins ComfyUI

### ✅ **Analyse complète**
- Distinction built-in vs custom nodes
- Mapping nodes → fichiers sources
- Statistiques détaillées

### ✅ **Formats de workflow supportés**
- Format ComfyUI standard (clés numériques)
- Format avec clé "nodes"
- Validation de structure

### ✅ **Rapports détaillés**
- Rapport textuel formaté
- Données JSON structurées
- Statuts d'exécution clairs

## 🧪 Tests

```bash
# Tester le système complet
python test_missing_nodes_system.py
```

### Tests inclus :
1. **Test classe standalone** : Fonctionnement de MissingNodesDetector
2. **Test custom node** : Validation du fichier ComfyUI
3. **Test intégration** : API ComfyUICustomNodeCaller

## 🛠️ Dépannage

### Custom node non trouvé dans ComfyUI
```bash
# Vérifier l'emplacement
ls /path/to/ComfyUI/custom_nodes/missing_nodes_detector_node.py
ls /path/to/ComfyUI/custom_nodes/cy8_missing_nodes_detector.py

# Vérifier les logs ComfyUI au démarrage
```

### Erreur "Classe MissingNodesDetector non trouvée"
- Assurez-vous que `cy8_missing_nodes_detector.py` est dans le même répertoire
- Vérifiez les permissions de lecture

### Auto-détection des chemins échoue
```python
# Utiliser des chemins absolus
result = caller.detect_missing_nodes(
    workflow_path="/chemin/absolu/vers/workflow.json",
    custom_nodes_dir="/chemin/absolu/vers/ComfyUI/custom_nodes",
    auto_detect_paths=False
)
```

## 📝 Exemples

### Exemple 1: Workflow simple
```python
# Analyser un workflow basique
detector = MissingNodesDetector()
result = detector.detect_missing_nodes(
    "basic_workflow.json",
    "ComfyUI/custom_nodes"
)
print(detector.generate_report(result))
```

### Exemple 2: Via ComfyUI API
```python
# Utilisation avec serveur ComfyUI
caller = ComfyUICustomNodeCaller("http://localhost:8188")
result = caller.detect_missing_nodes("complex_workflow.json", "custom_nodes")

if result["status"] == "WARNING":
    print("⚠️ Nodes manquants détectés!")
    caller.print_missing_nodes_report(result)
```

## 🎯 Cas d'usage

### 🔄 **Partage de workflows**
Vérifiez que tous les custom nodes sont disponibles avant de partager

### 📦 **Migration ComfyUI**
Identifiez les custom nodes à installer sur une nouvelle installation

### 🛠️ **Développement**
Validez les dépendances lors de la création de workflows complexes

### 🏢 **Déploiement**
Automatisez la vérification des prérequis en production

---

## 📧 Support

Pour des questions ou problèmes :
1. Vérifiez les logs ComfyUI
2. Testez avec `test_missing_nodes_system.py`
3. Utilisez les chemins absolus si l'auto-détection échoue

# Organisation des Tests - cy8_prompts_manager

## 📁 Structure des tests

Tous les fichiers de test sont maintenant organisés dans le répertoire `tests/` :

```
tests/
├── test_ci_validation.py        # Tests de validation CI/CD
├── test_comfyui_connection.py   # Test de connexion ComfyUI (sans exécution)
├── test_comfyui_quick.py        # Test de diagnostic rapide ComfyUI
├── test_comfyui_tab.py          # Test de l'onglet ComfyUI dans l'interface
├── test_direct_workflow.py      # Test direct de workflow (diagnostic)
├── test_execution_progress.py   # Test de progression d'exécution
└── test_images_simple.py        # Test du système d'images (obsolète)
```

## 🧪 Types de tests

### Tests principaux (toujours valides)
- **`src/cy8_test_suite.py`** : Suite principale de tests cy8
  - Tests de base de données
  - Tests de structures de données
  - Tests d'intégration système

### Tests de connexion ComfyUI
- **`tests/test_comfyui_connection.py`** : Test de connexion uniquement
  - ✅ Test HTTP vers ComfyUI
  - ❌ Tests d'exécution supprimés (maintenant dans l'interface)
- **`tests/test_comfyui_quick.py`** : Diagnostic rapide

### Tests d'interface
- **`tests/test_comfyui_tab.py`** : Test du nouvel onglet ComfyUI
  - Vérification de la création de l'onglet
  - Test des boutons et indicateurs
  - Validation de l'interface

### Tests de validation
- **`tests/test_ci_validation.py`** : Tests automatisés pour CI/CD
  - Validation des imports
  - Vérification de la structure du projet
  - Tests de régression

## 🚀 Exécution des tests

### Script unifié (recommandé)
```bash
python run_all_tests.py
```
Ce script lance automatiquement :
- Tests principaux cy8
- Test de connexion ComfyUI
- Test de l'onglet ComfyUI
- Test de validation CI
- Tests pytest (si disponible)

### Tests individuels
```bash
# Tests principaux
python src/cy8_test_suite.py

# Test de connexion ComfyUI
python tests/test_comfyui_connection.py

# Test de l'onglet ComfyUI
python tests/test_comfyui_tab.py

# Tous les tests pytest
pytest tests/ -v
```

### Tests spécifiques
```bash
# Test spécifique avec pytest
pytest tests/test_comfyui_tab.py -v

# Test de diagnostic ComfyUI
python tests/test_comfyui_quick.py
```

## ⚠️ Tests obsolètes

### `test_images_simple.py`
- **Statut** : Obsolète
- **Raison** : Teste des fonctionnalités supprimées (apply_images_path)
- **Remplacement** : Interface en lecture seule pour IMAGES_COLLECTE

### Tests d'exécution automatique
- **Anciennement** : `test_workflow_execution()` dans `test_comfyui_connection.py`
- **Maintenant** : Supprimé, remplacé par l'onglet ComfyUI dans l'interface

## 📊 Résultats attendus

### Tests qui doivent passer
- ✅ `src/cy8_test_suite.py` : 8 tests OK
- ✅ `tests/test_comfyui_connection.py` : Connexion ComfyUI OK
- ✅ `tests/test_comfyui_tab.py` : Interface ComfyUI OK
- ✅ `pytest tests/` : 20 tests passed (avec warnings sur return values)

### Tests avec problèmes connus
- ⚠️ `test_images_simple.py` : Échoue (fonctionnalités supprimées)
- ⚠️ Encodage Unicode : Problèmes d'affichage des emojis sur Windows

## 🔧 Configuration des tests

### Variables d'environnement requises
```env
COMFYUI_SERVER=127.0.0.1:8188
IMAGES_COLLECTE=E:/Comfyui_G11/ComfyUI/output
```

### Prérequis
- ComfyUI démarré sur 127.0.0.1:8188 (pour tests de connexion)
- Python 3.10+ avec tous les modules cy8
- Environnement virtuel activé

### pytest (optionnel)
```bash
pip install pytest
```

## 💡 Bonnes pratiques

1. **Lancer tous les tests** : Utiliser `python run_all_tests.py`
2. **Tests de développement** : `python src/cy8_test_suite.py` suffit
3. **Test de connexion** : Vérifier ComfyUI avant les tests
4. **Interface ComfyUI** : Tester via l'onglet dédié dans l'application

## 🎯 Tests manuels

Pour les tests d'exécution de workflow (maintenant manuels) :
1. Lancer `python src/cy8_prompts_manager_main.py`
2. Sélectionner un prompt dans la liste
3. Aller dans l'onglet "ComfyUI"
4. Cliquer sur "🔗 Tester la connexion"

Cette approche offre plus de contrôle et évite les interférences avec ComfyUI en production.

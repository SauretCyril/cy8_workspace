# 🧪 Tests - cy8_prompts_manager

## 📋 Organisation des Tests

### 📁 `unit/` - Tests Unitaires
Tests de composants individuels isolés :

- `test_correction_thread.py` - Test de sécurité des threads pour les popups
- `test_corrections_multiples.py` - Test des corrections multiples (popup, préférences, status)
- `test_confirmation_popup.py` - Test de la popup de confirmation de workflow
- `test_phase1_consolidation.py` - Test de validation des fonctions UI consolidées

### � `integration/` - Tests d'Intégration
Tests de l'interaction entre plusieurs composants :

- `test_database_structure.py` - Test de vérification et réparation de la base de données
- `test_generation_image_diagnostic.py` - Test de génération d'image ComfyUI avec diagnostic serveur
- `test_synchronisation_chat_env.py` - Test de synchronisation chat-environnement

### 📁 `system/` - Tests Système
Tests de l'ensemble du système et du workflow complet :

- `test_workflow_monitor.py` - Test du système de gestion des workflows avec pile et surveillance
- `test_server_failure_detection.py` - Test de détection de panne serveur
- `test_server_protection_complete.py` - Test complet de la gestion des pannes serveur

## 🗑️ Fichiers Supprimés (Obsolètes)

Les fichiers suivants ont été supprimés car ils n'étaient plus pertinents :

- `test_confirmation_reel.py` - Test avec modèle valide (imports obsolètes)
- `test_json_fix.py` - Test de correction JSONDecodeError (imports obsolètes)
- `test_models_disponibles.py` - Test de listing des modèles (imports obsolètes)

## 🚀 Utilisation

### Exécuter tous les tests
```bash
python -m pytest tests/ -v
```

### Exécuter par catégorie
```bash
# Tests unitaires uniquement
python -m pytest tests/unit/ -v

# Tests d'intégration uniquement
python -m pytest tests/integration/ -v

# Tests système uniquement
python -m pytest tests/system/ -v
```

### Exécuter un test spécifique
```bash
python -m pytest tests/unit/test_correction_thread.py -v
```

## 📝 Conventions

- Tous les tests commencent par `test_`
- Les imports pointent vers `src/` via le chemin relatif `../../src`
- Chaque répertoire contient un `__init__.py` pour la structure Python
- Les tests sont organisés par niveau de complexité (unitaire → intégration → système)

## 🎯 Maintenance

- Les tests récents (< 7 jours) avec imports valides ont été conservés
- Les tests obsolètes ou avec imports cassés ont été supprimés
- La structure suit les bonnes pratiques de test Python
- `test_rag_learning_simple.py` - Tests d'apprentissage RAG
- `test_rag_tester_sync.py` - Tests de synchronisation RAG

### Tests d'environnement
- `test_environment_identification.py` - Identification d'environnement
- `test_environment_tracking.py` - Suivi d'environnement
- `test_env_display.py` - Affichage d'environnement
- `test_env_tab.py` - Tests de l'onglet environnement

### Tests de base de données
- `test_db_manager.py` - Tests du gestionnaire de base de données
- `check_environments_db.py` - Vérification de la DB des environnements

### Tests de configuration
- `test_config_extraction.py` - Extraction de configuration
- `test_extract_config_id.py` - Extraction d'ID de configuration
- `test_extra_path_reader.py` - Lecture des extra paths
- `test_extra_paths_diagnostic.py` - Diagnostic des extra paths

### Tests de custom nodes
- `test_custom_node_caller.py` - Appels de custom nodes
- `test_custom_node_caller_debug.py` - Debug des custom nodes

### Tests de solutions d'erreurs
- `test_error_solutions.py` - Tests des solutions d'erreurs
- `test_execution_progress.py` - Tests de progression d'exécution

### Utilitaires de test
- `run_tests.py` - Runner de tests principal
- `run_all_tests.py` - Exécution de tous les tests
- `check_venv.py` - Vérification de l'environnement virtuel
- `validate_ci_quick.py` - Validation CI/CD rapide
- `test_ci_validation.py` - Validation CI complète

## 🚀 Exécution des tests

### Tous les tests
```bash
python tests/run_all_tests.py
```

### Tests avec pytest
```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_rag_*.py -v

# Tests avec couverture
pytest tests/ --cov=src --cov-report=html
```

### Tests individuels
```bash
# Test de connexion ComfyUI
python tests/test_comfyui_connection.py

# Test RAG
python tests/test_rag_integration.py

# Test d'environnement
python tests/test_environment_identification.py
```

## 📊 Types de tests

### Tests unitaires
Testent des fonctions/méthodes individuelles de manière isolée.

### Tests d'intégration
Testent l'interaction entre plusieurs composants.

### Tests end-to-end
Testent des scénarios complets d'utilisation.

## ✅ Bonnes pratiques

- Chaque fichier de test commence par `test_`
- Utiliser des assertions claires avec messages explicites
- Mocker les dépendances externes (API, base de données)
- Nettoyer les ressources après chaque test
- Tests indépendants et reproductibles

## 🔍 Debug des tests

Si un test échoue, vérifier :
1. Les logs dans la console
2. Les variables d'environnement (.env)
3. La connexion au serveur ComfyUI
4. La base de données (data/prompts_manager.db)

## 📝 Ajouter un nouveau test

1. Créer un fichier `test_nom_fonctionnalite.py`
2. Importer les modules nécessaires
3. Créer des fonctions de test avec `test_` en préfixe
4. Utiliser pytest fixtures si besoin
5. Ajouter le test à `run_all_tests.py` si nécessaire

Exemple :
```python
def test_ma_fonctionnalite():
    """Test de ma nouvelle fonctionnalité"""
    # Arrange
    data = setup_test_data()

    # Act
    result = ma_fonction(data)

    # Assert
    assert result == expected_value
```

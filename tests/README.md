# 🧪 Tests

Répertoire contenant tous les tests du projet cy8_workspace.

## 📋 Organisation

### Tests d'application
- `test_app_startup.py` - Tests de démarrage de l'application
- `test_complete_env.py` - Tests d'environnement complet
- `test_complete_workflow.py` - Tests de workflow complet

### Tests ComfyUI
- `test_comfyui_connection.py` - Test de connexion au serveur ComfyUI
- `test_comfyui_quick.py` - Tests rapides ComfyUI
- `test_comfyui_tab.py` - Tests de l'onglet ComfyUI
- `test_direct_workflow.py` - Tests de workflows directs

### Tests RAG (Retrieval-Augmented Generation)
- `test_rag_correction.py` - Tests de correction RAG
- `test_rag_integration.py` - Tests d'intégration RAG
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

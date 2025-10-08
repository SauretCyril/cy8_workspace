# 📁 Structure du Projet cy8_workspace

Organisation professionnelle du projet cy8_prompts_manager.

## 🏗️ Architecture

```
cy8_workspace/
│
├── 📄 main.py                      # Point d'entrée principal de l'application
├── 📄 requirements.txt             # Dépendances Python
├── 📄 README.md                    # Documentation principale
├── 📄 .env                         # Configuration locale (non versionné)
├── 📄 .env.example                 # Template de configuration
├── 📄 .gitignore                   # Fichiers à ignorer par Git
│
├── 📂 src/                         # Code source principal
│   ├── cy8_prompts_manager_main.py     # Application principale Tkinter
│   ├── cy8_database_manager.py         # Gestion de la base de données SQLite
│   ├── cy8_rag_manager.py              # Système RAG (Retrieval-Augmented Generation)
│   ├── cy8_rag_tester.py               # Tests du système RAG
│   ├── cy8_mistral.py                  # Intégration Mistral AI
│   ├── cy8_paths.py                    # Gestion des chemins
│   ├── cy8_preferences_manager.py      # Gestion des préférences utilisateur
│   ├── cy8_user_preferences.py         # Préférences utilisateur
│   ├── cy8_popup_manager.py            # Gestion des popups
│   ├── cy8_editable_tables.py          # Tables éditables Tkinter
│   ├── cy8_log_analyzer.py             # Analyse des logs ComfyUI
│   ├── cy8_image_index_manager.py      # Indexation des images
│   ├── cy8_fast_image_processor.py     # Traitement d'images optimisé
│   ├── cy8_comfyui_customNode_call.py  # Appels aux custom nodes ComfyUI
│   ├── cy6_*.py                        # Modules hérités (legacy)
│   └── __pycache__/
│
├── 📂 tests/                       # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── run_tests.py                    # Runner de tests principal
│   ├── run_all_tests.py                # Exécution de tous les tests
│   ├── test_app_startup.py             # Tests de démarrage
│   ├── test_comfyui_*.py               # Tests ComfyUI
│   ├── test_rag_*.py                   # Tests du système RAG
│   ├── test_db_manager.py              # Tests de la base de données
│   ├── test_environment_*.py           # Tests d'environnement
│   ├── check_environments_db.py        # Vérification de la DB
│   ├── check_venv.py                   # Vérification de l'environnement virtuel
│   └── validate_ci_quick.py            # Validation CI/CD rapide
│
├── 📂 debugs/                      # Scripts de diagnostic et debug
│   ├── debug_environment.py            # Debug de l'environnement
│   ├── diagnostic_rag_apprentissage.py # Diagnostic RAG apprentissage
│   ├── diagnostic_rag_simple.py        # Diagnostic RAG simplifié
│   └── fix_rag_environment.py          # Correction environnement RAG
│
├── 📂 demos/                       # Exemples et démos
│   ├── demo_images.py                  # Démo gestion d'images
│   ├── exemple_preferences.py          # Exemple de préférences
│   └── guide_test_rag.py               # Guide de test du RAG
│
├── 📂 scripts/                     # Scripts utilitaires
│   ├── activate.bat                    # Activation venv (Windows)
│   ├── activate.sh                     # Activation venv (Linux/Mac)
│   ├── start.sh                        # Démarrage (Linux/Mac)
│   ├── start_with_venv.bat             # Démarrage avec venv (Windows)
│   ├── ci_setup.bat                    # Configuration CI (Windows)
│   ├── ci_setup.sh                     # Configuration CI (Linux/Mac)
│   ├── install_hooks.py                # Installation des hooks Git
│   ├── install_rust_optimization.bat   # Installation optimisations Rust (Windows)
│   └── install_rust_optimization.sh    # Installation optimisations Rust (Linux/Mac)
│
├── 📂 docs/                        # Documentation détaillée
│   ├── README.md
│   ├── GUIDE_UTILISATION_*.md          # Guides utilisateur
│   ├── *_IMPLEMENTATION.md             # Documentation d'implémentation
│   ├── Exemples_Questions_Mistral.txt  # Exemples pour Mistral
│   ├── guide_*.py                      # Guides Python
│   └── Tests_Organisation.md           # Organisation des tests
│
├── 📂 data/                        # Données de l'application
│   ├── Workflows/                      # Workflows ComfyUI
│   │   └── *.json
│   ├── prompts_manager.db              # Base de données principale
│   └── rag_tests/                      # Résultats des tests RAG
│
├── 📂 logs/                        # Fichiers de logs
│   └── *.log
│
├── 📂 custom_nodes/                # Custom nodes ComfyUI
│   └── cy8_nodes/
│
├── 📂 rust_image_processor/        # Optimisations Rust pour les images
│   ├── Cargo.toml
│   ├── README.md
│   └── src/
│
├── 📂 .vscode/                     # Configuration VS Code
│   ├── launch.json                     # Configurations de debug
│   ├── settings.json                   # Paramètres de l'éditeur
│   └── tasks.json                      # Tâches automatisées
│
├── 📂 .github/                     # Configuration GitHub
│   ├── copilot-instructions.md         # Instructions pour Copilot
│   └── workflows/                      # GitHub Actions CI/CD
│
└── 📂 venv/                        # Environnement virtuel Python (non versionné)
    └── ...
```

## 🎯 Points d'entrée

### Démarrage de l'application
```bash
# Méthode 1 : Direct
python main.py

# Méthode 2 : Avec script (Windows)
scripts\start_with_venv.bat

# Méthode 3 : Avec script (Linux/Mac)
bash scripts/start.sh

# Méthode 4 : VS Code (F5)
# Utilise .vscode/launch.json
```

### Exécution des tests
```bash
# Tous les tests
python tests/run_all_tests.py

# Tests spécifiques
python -m pytest tests/ -v

# Test rapide CI
python tests/validate_ci_quick.py
```

### Outils de debug
```bash
# Diagnostic environnement
python debugs/debug_environment.py

# Diagnostic RAG
python debugs/diagnostic_rag_simple.py

# Vérification base de données
python tests/check_environments_db.py
```

## 📦 Modules principaux

### Application (src/)
- **cy8_prompts_manager_main.py** : Interface Tkinter principale avec onglets (ComfyUI, Log, Chat, Images)
- **cy8_database_manager.py** : Gestion SQLite des environnements, analyses et résultats
- **cy8_rag_manager.py** : Système RAG avec ChromaDB et embeddings
- **cy8_mistral.py** : Intégration API Mistral pour le chat intelligent

### Gestion ComfyUI
- **cy8_comfyui_customNode_call.py** : Appels aux custom nodes via WebSocket
- **cy8_paths.py** : Extraction et gestion des extra_model_paths.yaml
- **cy8_log_analyzer.py** : Analyse des logs d'exécution ComfyUI

### Tests (tests/)
- **test_rag_*.py** : Tests du système RAG (indexation, recherche, apprentissage)
- **test_comfyui_*.py** : Tests d'intégration ComfyUI
- **test_environment_*.py** : Tests de détection et gestion d'environnement

## 🔧 Configuration

### Fichiers de configuration
- **.env** : Variables d'environnement (API keys, chemins)
- **src/cy8_user_preferences.py** : Préférences sauvegardées de l'utilisateur
- **data/prompts_manager.db** : Base de données SQLite

### Variables d'environnement importantes
```env
MISTRAL_API_KEY=your_api_key_here
COMFYUI_URL=http://127.0.0.1:8188
IMAGES_COLLECTE=E:/ComfyUI/output
```

## 🚀 Workflow de développement

1. **Cloner et configurer**
   ```bash
   git clone <repo>
   cd cy8_workspace
   python -m venv venv
   source scripts/activate.sh  # ou scripts\activate.bat sur Windows
   pip install -r requirements.txt
   ```

2. **Développer**
   - Modifier les fichiers dans `src/`
   - Ajouter des tests dans `tests/`
   - Documenter dans `docs/`

3. **Tester**
   ```bash
   python tests/run_all_tests.py
   ```

4. **Déboguer**
   - Utiliser VS Code avec F5
   - Logs de debug automatiques dans la console
   - Scripts de diagnostic dans `debugs/`

## 📝 Conventions

### Nommage des fichiers
- **cy8_*.py** : Modules principaux version 8
- **cy6_*.py** : Modules legacy version 6
- **test_*.py** : Fichiers de test
- **debug_*.py** : Scripts de debug
- **demo_*.py** : Scripts de démonstration

### Organisation du code
- Logs de debug conservés pour faciliter le diagnostic
- Gestion d'erreurs avec traceback complet
- Documentation inline avec docstrings
- Type hints pour améliorer la lisibilité

## 🔍 Dépannage

### Logs
- Console : Logs en temps réel avec emojis 🔍
- Fichiers : `logs/*.log`
- Tests RAG : `data/rag_tests/*.json`

### Outils de diagnostic
```bash
# Vérifier l'environnement
python debugs/debug_environment.py

# Vérifier la base de données
python tests/check_environments_db.py

# Tester le RAG
python debugs/diagnostic_rag_simple.py
```

## 📊 État du projet

✅ Structure réorganisée et professionnelle  
✅ Tests séparés du code source  
✅ Scripts d'utilitaires centralisés  
✅ Documentation complète  
✅ Configuration VS Code optimisée  
✅ CI/CD prêt avec GitHub Actions  

---

**Dernière mise à jour** : 8 octobre 2025  
**Version** : 8.0  
**Mainteneur** : Projet cy8_workspace

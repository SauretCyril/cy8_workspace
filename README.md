# Gestionnaire de Prompts ComfyUI - cy8_prompts_manager

## 🎯 Vue d'ensemble

Le **cy8_prompts_manager** est une application de bureau Python moderne construite avec Tkinter pour gérer et exécuter des prompts ComfyUI. Cette version cy8 représente une refactorisation complète du système avec une architecture modulaire professionnelle.

## ✨ Fonctionnalités principales

- **🗃️ Gestion de base de données** : Stockage SQLite avec validation automatique de structure
- **🎨 Interface utilisateur moderne** : Interface Tkinter avec style professionnel ttk
- **🔗 Intégration ComfyUI** : Connexion WebSocket directe avec ComfyUI pour l'exécution de workflows
- **📊 Tableaux éditables** : Modification en temps réel des prompt values et workflows
- **💾 Sauvegarde automatique** : Persistance des données avec callbacks intégrés
- **🔍 Popups d'identification** : Système CY8-POPUP-XXX pour faciliter la communication
- **📂 Gestion multi-bases** : Basculement facile entre différentes bases de données
- **⚙️ Préférences utilisateur** : Sauvegarde des paramètres et géométrie de fenêtre
- **🔄 Suivi d'exécution** : Onglet dédié avec historique complet, progression en % et détails des workflows ComfyUI

## 🏗️ Architecture

### 📂 Structure du projet

```
cy8_workspace/
├── 📄 main.py                  # Point d'entrée principal
├── 📄 requirements.txt         # Dépendances Python
├── 📄 README.md               # Ce fichier
│
├── 📂 src/                    # Code source principal
│   ├── cy8_prompts_manager_main.py
│   ├── cy8_database_manager.py
│   ├── cy8_rag_manager.py
│   ├── cy8_mistral.py
│   └── ... (autres modules)
│
├── 📂 tests/                  # Tests unitaires et d'intégration
│   ├── test_*.py
│   └── run_tests.py
│
├── 📂 scripts/                # Scripts utilitaires
│   ├── activate.*             # Activation venv
│   ├── start.*                # Démarrage application
│   └── install_*.* 
│
├── 📂 debugs/                 # Scripts de diagnostic
│   ├── debug_*.py
│   └── diagnostic_*.py
│
├── 📂 demos/                  # Exemples et démos
│   ├── demo_*.py
│   └── guide_*.py
│
├── 📂 docs/                   # Documentation complète
│   ├── INDEX.md               # Index de la documentation
│   ├── STRUCTURE.md           # Architecture détaillée
│   └── ... (45+ documents)
│
├── 📂 data/                   # Données de l'application
│   ├── Workflows/
│   └── prompts_manager.db
│
└── 📂 logs/                   # Fichiers de logs
```

📖 **Documentation complète** : Voir [docs/INDEX.md](docs/INDEX.md)  
🏗️ **Architecture détaillée** : Voir [docs/STRUCTURE.md](docs/STRUCTURE.md)

### Modules principaux

- **`cy8_prompts_manager_main.py`** : Gestionnaire principal et interface utilisateur
- **`cy8_database_manager.py`** : Gestion SQLite avec validation de structure
- **`cy8_editable_tables.py`** : Tableaux éditables pour values/workflows
- **`cy8_popup_manager.py`** : Gestion des popups avec identifiants uniques
- **`cy8_user_preferences.py`** : Préférences utilisateur et cookies
- **`cy8_paths.py`** : Gestion des chemins cross-platform

### Modules d'intégration ComfyUI

- **`cy6_wkf001_Basic.py`** : Tâches ComfyUI de base
- **`cy6_task_comfyui.py`** : Gestionnaire de tâches ComfyUI
- **`cy6_websocket_api_client.py`** : Client WebSocket pour ComfyUI
- **`cy6_file.py`** : Utilitaires de fichiers pour ComfyUI

## 🚀 Installation et utilisation

### Prérequis

```bash
Python 3.10+ (recommandé 3.10.11 pour compatibilité ComfyUI optimale)
ComfyUI en fonctionnement sur 127.0.0.1:8188
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement de l'application

**Méthode recommandée (avec scripts) :**
```bash
# Windows
scripts\start_with_venv.bat

# Unix/Linux/Mac
bash scripts/start.sh
```

**Méthode simple :**
```bash
python main.py
```

**Méthode directe :**
```bash
python src/cy8_prompts_manager_main.py
```

### Scripts utilitaires

📂 Tous les scripts sont dans le répertoire `scripts/`

- **`activate.bat/sh`** : Activation rapide de l'environnement virtuel
- **`start_with_venv.bat/start.sh`** : Démarrage avec vérifications
- **`ci_setup.bat/sh`** : Configuration CI/CD
- **`install_hooks.py`** : Installation des hooks Git
- **`install_rust_optimization.bat/sh`** : Optimisations Rust pour images

📖 **Guide complet** : Voir [scripts/README.md](scripts/README.md)

### 🧪 Tests

Le projet inclut une suite de tests complète dans le répertoire `tests/`.

#### Exécution des tests

```bash
# Exécuter tous les tests
python tests/run_all_tests.py

# Avec pytest
pytest tests/ -v

# Test spécifique
python tests/test_comfyui_connection.py
```

#### Tests disponibles

- Tests d'application : `test_app_*.py`
- Tests ComfyUI : `test_comfyui_*.py`
- Tests RAG : `test_rag_*.py`
- Tests d'environnement : `test_environment_*.py`
- Tests de base de données : `test_db_*.py`
- Et bien d'autres...

📖 **Guide complet des tests** : Voir [tests/README.md](tests/README.md)

### 🐛 Debug et Diagnostic

Scripts de diagnostic disponibles dans `debugs/` :

```bash
# Diagnostic environnement
python debugs/debug_environment.py

# Diagnostic RAG
python debugs/diagnostic_rag_simple.py

# Vérification base de données
python tests/check_environments_db.py
```

📖 **Guide de diagnostic** : Voir [debugs/README.md](debugs/README.md)

### 🎨 Démos et Exemples

Exemples d'utilisation dans `demos/` :

```bash
# Démo système d'images
python demos/demo_images.py

# Démo système RAG
python demos/demo_rag_system.py

# Guide de test RAG
python demos/guide_test_rag.py
```

📖 **Liste complète des démos** : Voir [demos/README.md](demos/README.md)

## 🎮 Guide d'utilisation

### Interface principale

L'interface est divisée en deux panneaux principaux :

1. **Panneau gauche** : Liste des prompts avec colonnes ID, Name, Status, Model, Comment
2. **Panneau droit** : Onglets détaillés (Prompt Values, Workflow, Informations, Data, Exécutions)

### Gestion des prompts

- **Nouveau prompt** : Menu Fichier → Nouveau prompt
- **Édition** : Double-clic sur un prompt ou Menu Édition → Hériter prompt
- **Exécution** : Menu Exécution → Exécuter prompt
- **Sauvegarde** : Ctrl+S ou boutons de sauvegarde dans chaque onglet

### Gestion des bases de données

L'onglet **Data** permet de :
- Changer de base de données
- Créer de nouvelles bases
- Gérer les bases récentes
- Valider la structure des bases

### Exécution de workflows

1. Sélectionnez un prompt dans la liste
2. Cliquez sur "Exécuter prompt" ou utilisez le menu
3. Suivez l'exécution via l'onglet **Exécutions** avec :
   - Progression en temps réel (0-100%)
   - Nom du prompt en cours d'exécution
   - Historique détaillé des étapes
   - Statut de chaque exécution
4. Les images générées sont automatiquement récupérées

### Suivi des exécutions

L'onglet **Exécutions** offre :
- **Vue d'ensemble** : Tableau avec toutes les exécutions (ID, Nom, Statut, %, Heure)
- **Détails complets** : Sélectionnez une exécution pour voir l'historique complet
- **Indicateur barre de statut** : Affichage compact de l'exécution en cours
- **Gestion historique** : Bouton pour effacer l'historique des exécutions

## 🔧 Configuration

### Configuration des répertoires

#### IMAGES_COLLECTE (Simplifié)

L'application utilise maintenant un système simplifié centré sur **IMAGES_COLLECTE** :

- **Via l'interface** : Onglet "Data" > Section "Configuration du répertoire d'images"
- **Variable d'environnement** : `IMAGES_COLLECTE=path/to/comfyui/output`
- **Valeur par défaut** : `./images` si non configuré

**Actions disponibles :**
- 📁 Parcourir et sélectionner un nouveau répertoire
- ✅ Appliquer les changements (sauvegardé dans les préférences)
- 📂 Créer le répertoire s'il n'existe pas
- 🗂️ Ouvrir dans l'explorateur de fichiers

Voir le [Guide IMAGES_COLLECTE](docs/IMAGES_COLLECTE_Guide.md) pour plus de détails.

#### Autres variables (optionnelles)

```env
COMFYUI_SERVER=127.0.0.1:8188
```

### Structure des données

Les prompts sont stockés dans SQLite avec la structure :
- `id` : Identifiant unique
- `name` : Nom du prompt
- `prompt_values` : JSON des valeurs (positive, negative, seed, etc.)
- `workflow` : JSON du workflow ComfyUI
- `url`, `model`, `comment`, `status` : Métadonnées

## 🧪 Tests et validation

### Infrastructure CI/CD

Le projet dispose d'une infrastructure CI complète pour garantir la qualité du code :

#### Validation locale

```bash
python validate_ci.py
```

Ce script vérifie automatiquement :
- ✅ Version Python (3.9+)
- ✅ Dépendances installées
- ✅ Imports des modules cy8
- ✅ Tests unitaires cy8 (8 tests)
- ✅ Tests pytest (10+ tests)
- ✅ Style de code (flake8)

#### Hooks Git

Des hooks Git sont automatiquement installés pour bloquer les push défaillants :

```bash
python install_hooks.py  # Installation des hooks
git push                 # Validation automatique avant push
git push --no-verify     # Bypass temporaire du hook
```

#### GitHub Actions

Tests automatiques sur plusieurs plateformes :
- 🐧 Ubuntu (Python 3.9, 3.10, 3.11, 3.12)
- 🪟 Windows (Python 3.9, 3.10, 3.11, 3.12)
- 🚀 Exécution sur chaque push et pull request

### Test de connexion ComfyUI

```bash
python tests/test_comfyui_connection.py
```

Ce script vérifie :
- ✅ Accessibilité de ComfyUI
- ✅ Version et statut du serveur
- ✅ Exécution d'un workflow de test
- ✅ Récupération d'images

### Tests unitaires

```bash
python -m pytest tests/
```

## 🐛 Dépannage

### ComfyUI non accessible

1. Vérifiez que ComfyUI fonctionne sur `127.0.0.1:8188`
2. Testez avec `python tests/test_comfyui_connection.py`
3. Vérifiez la configuration du firewall

### Erreurs de base de données

1. L'application valide automatiquement la structure
2. Les bases corrompues sont réparées automatiquement
3. Sauvegardez vos données importantes avant les réparations

### Problèmes d'interface

1. Fermez et relancez l'application
2. Supprimez le fichier de préférences si nécessaire
3. Vérifiez les logs dans la console

## 📋 Popups et identifiants

Le système utilise des identifiants uniques pour faciliter la communication :

- **CY8-POPUP-001** : Nouveau prompt
- **CY8-POPUP-002** : Édition de prompt
- **CY8-POPUP-003** : Héritage de prompt
- **CY8-POPUP-004** : Sélection de base de données
- **CY8-POPUP-005** : Création de base de données
- **CY8-POPUP-006** : Édition de valeurs de prompt
- **CY8-POPUP-007** : Édition de workflow
- **CY8-POPUP-008** : Confirmation de suppression
- **CY8-POPUP-009** : Importation JSON
- **CY8-POPUP-010** : Exportation JSON

## 🤝 Contribution et développement

### Workflow de développement

Le projet utilise une infrastructure CI complète pour maintenir la qualité :

1. **Clonez et configurez** :
   ```bash
   git clone [repository]
   cd cy8_workspace
   pip install -r requirements.txt
   python install_hooks.py  # Installe les hooks Git
   ```

2. **Développement** :
   ```bash
   python validate_ci.py  # Validation locale avant commit
   git add .
   git commit -m "feat: votre fonctionnalité"
   git push  # Validation automatique via hook pre-push
   ```

3. **Intégration continue** :
   - Les tests s'exécutent automatiquement sur GitHub Actions
   - Couverture multi-plateforme (Ubuntu/Windows)
   - Matrix testing Python 3.9-3.12

### Pour contribuer au projet :

1. Forkez le repository
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Développez avec validation CI (`python validate_ci.py`)
4. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
5. Pushez vers la branche (`git push origin feature/AmazingFeature`)
6. Ouvrez une Pull Request

### Standards de qualité

- ✅ Tests unitaires obligatoires
- ✅ Style de code conforme (black, flake8)
- ✅ Documentation des nouvelles fonctionnalités
- ✅ Compatibilité Python 3.9+

## 📝 Changelog

### Version cy8 (Actuelle)
- ✅ Refactorisation complète en classes modulaires
- ✅ Système de popups avec identifiants
- ✅ Gestion multi-bases de données
- ✅ Validation automatique de structure
- ✅ Interface utilisateur modernisée
- ✅ Intégration ComfyUI corrigée
- ✅ Infrastructure CI/CD complète
- ✅ Hooks Git pour validation pre-push
- ✅ GitHub Actions multi-plateforme
- ✅ Suite de tests automatisée (cy8 + pytest)
- ✅ Validation de style de code (black, flake8)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- ComfyUI pour l'excellente plateforme de génération d'images
- La communauté Python pour les outils et bibliothèques
- Tous les contributeurs qui ont aidé à améliorer ce projet#   T e s t   h o o k 
 
 

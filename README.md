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

**Méthode simple :**
```bash
python src/cy8_prompts_manager_main.py
```

**Méthode avec scripts de démarrage :**
```bash
# Windows
start.bat

# Unix/Linux/Mac
./start.sh
```

**Point d'entrée principal :**
```bash
python main.py  # Point d'entrée avec gestion d'erreurs
```

### Scripts utilitaires

- **`validate_ci.py`** : Validation complète du code (tests, style, dépendances)
- **`install_hooks.py`** : Installation des hooks Git pre-push
- **`start.bat/sh`** : Scripts de démarrage avec vérifications
- **`activate.bat/sh`** : Activation rapide de l'environnement virtuel

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

### Variables d'environnement

Créez un fichier `.env` avec :

```env
COMFYUI_SERVER=127.0.0.1:8188
IMAGES_COLLECTE=path/to/comfyui/output
IMAGES_CENTRAL=path/to/comfyui/central
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

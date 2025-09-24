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
- **🔄 Suivi d'exécution** : Pile d'exécution en temps réel pour les workflows ComfyUI

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
Python 3.8+
ComfyUI en fonctionnement sur 127.0.0.1:8188
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement de l'application

```bash
python src/cy8_prompts_manager_main.py
```

## 🎮 Guide d'utilisation

### Interface principale

L'interface est divisée en deux panneaux principaux :

1. **Panneau gauche** : Liste des prompts avec colonnes ID, Name, Status, Model, Comment
2. **Panneau droit** : Onglets détaillés (Prompt Values, Workflow, Informations, Data)

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
3. Suivez l'exécution dans la pile d'exécution
4. Les images générées sont automatiquement récupérées

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

## 🤝 Contribution

Pour contribuer au projet :

1. Forkez le repository
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Changelog

### Version cy8 (Actuelle)
- ✅ Refactorisation complète en classes modulaires
- ✅ Système de popups avec identifiants
- ✅ Gestion multi-bases de données
- ✅ Validation automatique de structure
- ✅ Interface utilisateur modernisée
- ✅ Intégration ComfyUI corrigée

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- ComfyUI pour l'excellente plateforme de génération d'images
- La communauté Python pour les outils et bibliothèques
- Tous les contributeurs qui ont aidé à améliorer ce projet
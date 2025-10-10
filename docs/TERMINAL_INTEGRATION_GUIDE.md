# 🖥️ Terminal Intégré - Guide Complet

## Vue d'ensemble

Le terminal intégré dans `cy8_prompts_manager` offre une interface de ligne de commande directement dans l'application, avec des fonctionnalités avancées d'indexation RAG automatique des sessions.

## 🚀 Fonctionnalités Principales

### Interface Terminal
- **Émulation terminal** : Interface sombre style console avec police Consolas
- **Répertoire de travail** : Affichage et modification du répertoire courant
- **Historique intelligent** : Navigation avec ↑/↓ dans les commandes précédentes
- **Exécution asynchrone** : Commandes en arrière-plan sans bloquer l'interface

### Gestion des Commandes
- **Commandes système** : Exécution de toutes commandes shell/PowerShell
- **Commandes intégrées** :
  - `cls` / `clear` : Efface l'écran
  - `cd <répertoire>` : Change de répertoire
  - `exit` : Ferme le terminal
- **Auto-complétion** : Support de base (extensible)

### Intégration RAG
- **Indexation automatique** : Chaque session est automatiquement indexée
- **Contexte enrichi** : Commande, résultat, environnement, timestamp
- **Recherche intelligente** : Retrouvez vos sessions avec le RAG Hybride

## 🎯 Interface Utilisateur

### Zone d'en-tête
```
Répertoire: [C:\workspace\projet] [📁 Parcourir] [💾 Sauvegarder] [🧹 Effacer]
☑️ Indexer dans RAG
```

### Zone Terminal
```
████████████████████████████████████████
█ C:\workspace>  python --version       █
█ Python 3.11.7                         █
█ ✅ Commande terminée (code: 0)         █
█                                        █
█ C:\workspace> _                        █
████████████████████████████████████████
```

### Zone de Contrôle
```
Commande: [python main.py                    ] [⚡ Exécuter] [🛑 Arrêter]
```

## 🔧 Utilisation

### Démarrage
1. Ouvrir l'application `cy8_prompts_manager`
2. Cliquer sur l'onglet "⚡ Terminal"
3. Le terminal démarre dans le répertoire de l'application

### Exécution de Commandes
```bash
# Navigation
C:\workspace> cd src
C:\workspace\src> pwd

# Exécution Python
C:\workspace> python --version
C:\workspace> pip list

# Gestion de fichiers
C:\workspace> dir
C:\workspace> type README.md

# Git
C:\workspace> git status
C:\workspace> git log --oneline
```

### Navigation dans l'Historique
- **↑** : Commande précédente
- **↓** : Commande suivante
- **Enter** : Exécuter la commande
- **Tab** : Auto-complétion (basique)

### Gestion des Processus
- **Processus courts** : Exécution directe avec affichage du résultat
- **Processus longs** : Exécution en arrière-plan avec mise à jour temps réel
- **Interruption** : Bouton "🛑 Arrêter" pour terminer un processus

## 📚 Intégration RAG

### Indexation Automatique
Chaque commande exécutée est automatiquement indexée dans le RAG avec :

```python
{
    "timestamp": "2024-01-15T14:30:25",
    "command": "python train_model.py",
    "returncode": 0,
    "cwd": "C:\\workspace\\ml_project",
    "environment": "venv_ml",
    "analysis": "✅ Commande exécutée avec succès\n🐍 Exécution de script/programme"
}
```

### Types de Commandes Reconnues
- **📦 Gestion packages** : `pip`, `conda`, `npm`
- **🔧 Contrôle version** : `git`, `svn`
- **🐍 Exécution scripts** : `python`, `node`, `java`
- **📁 Navigation** : `cd`, `ls`, `dir`

### Recherche dans l'Historique
Utilisez le RAG pour retrouver vos sessions :
```
Question: "Comment j'ai installé TensorFlow la semaine dernière ?"
Réponse: "pip install tensorflow==2.15.0 (2024-01-08, code: 0)"
```

## ⚙️ Configuration

### Variables d'Environnement
Le terminal hérite automatiquement de :
- `PATH` système
- Variables d'environnement virtuelles (`VIRTUAL_ENV`)
- Variables personnalisées de l'application

### Paramètres
- **Répertoire par défaut** : Répertoire de l'application
- **Indexation RAG** : Activée par défaut (toggle disponible)
- **Historique** : Sauvegardé en mémoire pendant la session
- **Timeout** : 30 secondes pour les commandes longues

## 🎨 Personnalisation

### Styles de Sortie
- **Commandes** : Texte blanc sur fond sombre
- **Succès** : Texte vert (codes 0)
- **Erreurs** : Texte rouge (codes != 0)
- **Info** : Texte bleu (messages système)
- **Warnings** : Texte orange (interruptions)

### Raccourcis Clavier
- **Ctrl+C** : Copier (sélection)
- **Ctrl+V** : Coller dans l'input
- **Ctrl+L** : Effacer l'écran (équivalent `clear`)
- **F5** : Ré-exécuter la dernière commande

## 🔍 Dépannage

### Problèmes Courants

#### Commande Introuvable
```
❌ 'git' is not recognized as an internal or external command
```
**Solution** : Vérifier que Git est installé et dans le PATH

#### Processus Bloqué
```
C:\workspace> ping -t google.com
🛑 [Cliquer sur Arrêter pour interrompre]
```
**Solution** : Utiliser le bouton "🛑 Arrêter"

#### Erreur de Permissions
```
❌ Access denied: C:\Windows\System32
```
**Solution** : Utiliser un répertoire avec permissions ou lancer en admin

### Logs de Debug
Les erreurs sont affichées dans :
1. **Console terminal** : Erreurs d'exécution
2. **Console Python** : Erreurs internes
3. **Fichier log** : `logs/terminal_debug.log`

## 🚀 Cas d'Usage Avancés

### Développement ComfyUI
```bash
# Installation de nodes
C:\ComfyUI> git clone https://github.com/ltdrdata/ComfyUI-Manager.git custom_nodes/

# Test de workflow
C:\ComfyUI> python main.py --input-directory ./input --output-directory ./output

# Debug
C:\ComfyUI> python -c "import torch; print(torch.cuda.is_available())"
```

### Gestion d'Environnements
```bash
# Création venv
C:\projet> python -m venv venv_test

# Activation
C:\projet> venv_test\Scripts\activate

# Installation dépendances
(venv_test) C:\projet> pip install -r requirements.txt
```

### Scripts d'Automatisation
```bash
# Sauvegarde workflow
C:\workspace> python backup_workflows.py --date 2024-01-15

# Clean cache
C:\workspace> python clean_temp.py --force

# Deploy model
C:\workspace> python deploy_model.py --environment production
```

## 🔮 Fonctionnalités Futures

### En Développement
- **Auto-complétion avancée** : Fichiers, commandes, paramètres
- **Syntax highlighting** : Coloration syntaxique des commandes
- **Onglets multiples** : Plusieurs sessions simultanées
- **Macros** : Enregistrement et replay de séquences

### Intégrations Prévues
- **VS Code** : Synchronisation avec terminal VS Code
- **Docker** : Support containers et images
- **SSH** : Connexions distantes
- **AI Assistant** : Suggestions intelligentes de commandes

## 📊 Métriques et Performance

### Statistiques Affichées
- **Commandes exécutées** : Compteur session
- **Temps d'exécution** : Chronomètre par commande
- **Taux de succès** : Pourcentage codes 0
- **Répertoires visités** : Historique navigation

### Optimisations
- **Cache processus** : Réutilisation shells
- **Buffer intelligent** : Limitation sortie longue
- **Threading optimisé** : Non-blocage interface

---

## 🎯 Résumé

Le terminal intégré transforme `cy8_prompts_manager` en véritable IDE avec :

✅ **Interface moderne** et intuitive
✅ **Exécution asynchrone** sans blocage
✅ **Indexation RAG automatique** des sessions
✅ **Gestion processus avancée** avec interruption
✅ **Historique intelligent** avec navigation
✅ **Intégration parfaite** avec l'écosystème ComfyUI

🚀 **Prêt pour le développement productif !**

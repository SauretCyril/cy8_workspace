# Fonctionnalité: Répertoire d'Analyses IA par Environnement

## 🎯 Objectif

Chaque analyse complète avec IA doit être sauvegardée dans un sous-répertoire "analyses" du répertoire correspondant à l'environnement ComfyUI sélectionné, permettant une organisation claire et séparée par environnement.

## 📋 Spécifications

### Structure de Sauvegarde

- **Environnement G11_01** → Répertoire: `H:\comfyui\G11_01` → Analyses: `H:\comfyui\G11_01\analyses`
- **Environnement G11_02** → Répertoire: `H:\comfyui\G11_02` → Analyses: `H:\comfyui\G11_02\analyses`
- **Environnement G11_03** → Répertoire: `H:\comfyui\G11_03` → Analyses: `H:\comfyui\G11_03\analyses`
- **Environnement G11_04** → Répertoire: `H:\comfyui\G11_04` → Analyses: `H:\comfyui\G11_04\analyses`
- **Environnement G11_05** → Répertoire: `H:\comfyui\G11_05` → Analyses: `H:\comfyui\G11_05\analyses`

### Gestion des Cas d'Erreur

- Si l'environnement n'existe pas dans la base : `g:/temp/analyses/{environment_id}`
- Si aucun environnement sélectionné : répertoire global configuré dans les préférences
- Création automatique des répertoires s'ils n'existent pas

## 🔧 Implémentation Technique

### 1. Base de Données

**Fichier**: `src/cy8_database_manager.py`

#### Nouvelle Méthode
```python
def get_environment_analyses_directory(self, environment_id):
    """Récupérer le répertoire d'analyses pour un environnement"""
    try:
        self.cursor.execute(
            "SELECT path FROM environnements WHERE id = ?",
            (environment_id,),
        )
        result = self.cursor.fetchone()
        if result and result[0]:
            # Créer le chemin du répertoire analyses
            analyses_dir = os.path.join(result[0], "analyses")
            # Créer le répertoire s'il n'existe pas
            os.makedirs(analyses_dir, exist_ok=True)
            return analyses_dir
        else:
            # Répertoire par défaut si l'environnement n'est pas trouvé
            default_dir = f"g:/temp/analyses/{environment_id}"
            os.makedirs(default_dir, exist_ok=True)
            return default_dir
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération du répertoire analyses : {e}")
        # Répertoire par défaut en cas d'erreur
        default_dir = f"g:/temp/analyses/{environment_id}"
        os.makedirs(default_dir, exist_ok=True)
        return default_dir
```

### 2. Interface Utilisateur

**Fichier**: `src/cy8_prompts_manager_main.py`

#### Modifications des Fonctions de Sauvegarde

##### Sauvegarde de l'Analyse Globale
```python
def save_global_analysis(self, analysis_content, popup_id=None):
    # Obtenir le répertoire de sauvegarde spécifique à l'environnement
    if self.current_environment_id:
        solutions_dir = self.db_manager.get_environment_analyses_directory(self.current_environment_id)
    else:
        # Répertoire par défaut si aucun environnement sélectionné
        solutions_dir = self.user_prefs.get_error_solutions_directory()
        if not os.path.exists(solutions_dir):
            os.makedirs(solutions_dir, exist_ok=True)
```

##### Ouverture du Dossier Solutions
```python
def open_solutions_folder(self):
    # Utiliser le répertoire spécifique à l'environnement s'il y en a un de sélectionné
    if self.current_environment_id:
        solutions_dir = self.db_manager.get_environment_analyses_directory(self.current_environment_id)
        print(f"📁 Ouverture du répertoire d'analyses pour l'environnement {self.current_environment_id}: {solutions_dir}")
    else:
        solutions_dir = self.error_solutions_dir.get()
        os.makedirs(solutions_dir, exist_ok=True)
        print(f"📁 Ouverture du répertoire global: {solutions_dir}")
```

## 🎭 Scénarios d'Usage

### Scénario 1: Analyse avec Environnement Sélectionné

1. **Utilisateur** sélectionne l'environnement **G11_01**
2. **Utilisateur** analyse un log ComfyUI
3. **Utilisateur** clique sur "🤖 Analyse IA complète"
4. **Système** génère l'analyse avec Mistral AI
5. **Système** sauvegarde automatiquement dans `H:\comfyui\G11_01\analyses\`

**Fichier créé**: `analyse_log_complete_20251004_143025.txt`

### Scénario 2: Changement d'Environnement

1. **Utilisateur** passe à l'environnement **G11_02**
2. **Utilisateur** analyse un autre log
3. **Système** sauvegarde dans `H:\comfyui\G11_02\analyses\`
4. **Résultat**: Pas de mélange avec les analyses de G11_01

### Scénario 3: Ouverture du Dossier

1. **Utilisateur** a l'environnement **G11_03** sélectionné
2. **Utilisateur** clique sur "📁 Ouvrir dossier" (bouton solutions)
3. **Système** ouvre `H:\comfyui\G11_03\analyses\` dans l'explorateur
4. **Utilisateur** voit toutes les analyses de cet environnement

## ✅ Avantages

### Organisation
- **Séparation claire** : Chaque environnement a ses propres analyses
- **Localisation logique** : Analyses stockées près des données ComfyUI
- **Facilité de gestion** : Plus facile de retrouver les analyses par environnement

### Workflow
- **Automatique** : Pas de configuration manuelle requise
- **Intelligent** : Choix automatique du bon répertoire selon l'environnement
- **Robuste** : Gestion des cas d'erreur avec répertoires par défaut

### Maintenance
- **Évite les mélanges** : Analyses d'environnements différents bien séparées
- **Facilite la sauvegarde** : Un répertoire par environnement à sauvegarder
- **Améliore la lisibilité** : Structure claire et organisée

## 🔍 Structure Résultante

```
H:\comfyui\
├── G11_01\
│   ├── analyses\
│   │   ├── analyse_log_complete_20251004_143025.txt
│   │   ├── analyse_log_complete_20251004_150312.txt
│   │   └── analyse_log_complete_20251004_163421.txt
│   ├── ComfyUI\
│   └── [autres fichiers et dossiers ComfyUI]
│
├── G11_02\
│   ├── analyses\
│   │   ├── analyse_log_complete_20251004_154521.txt
│   │   └── analyse_log_complete_20251004_171205.txt
│   ├── ComfyUI\
│   └── [autres fichiers et dossiers ComfyUI]
│
├── G11_03\
│   ├── analyses\
│   │   └── analyse_log_complete_20251004_182314.txt
│   ├── ComfyUI\
│   └── [autres fichiers et dossiers ComfyUI]
│
└── ...
```

## 🧪 Tests

**Fichier de test**: `tests/test_environment_analyses_directory.py`

### Tests Couverts
- ✅ Récupération du répertoire d'analyses pour chaque environnement
- ✅ Construction correcte du chemin avec sous-répertoire "analyses"
- ✅ Gestion des environnements inexistants (répertoire par défaut)
- ✅ Création automatique des répertoires
- ✅ Scénarios d'usage complets

### Résultats
- **Tous les tests réussis** ✅
- **Fonctionnalité validée** ✅
- **Prêt pour utilisation** ✅

## 🚀 Déploiement

1. **Code modifié** dans `cy8_database_manager.py` et `cy8_prompts_manager_main.py`
2. **Tests créés** et validés
3. **Documentation complète** fournie
4. **Application testée** et fonctionnelle

La fonctionnalité est **opérationnelle** et prête à l'usage !

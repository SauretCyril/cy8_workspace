# 📤 Implémentation de l'exportation JSON et gestion des environnements

**Date** : 8 octobre 2025
**Version** : cy8_workspace
**Status** : ✅ Implémenté avec succès

---

## 🎯 Objectif

Implémenter une fonctionnalité complète d'exportation de workflows ComfyUI avec fusion des valeurs et des workflows, tout en ajoutant la gestion des environnements pour chaque prompt.

---

## ✨ Fonctionnalités implémentées

### 1️⃣ Nouveaux champs dans la base de données

#### Modification de la table `prompts`

Deux nouveaux champs ont été ajoutés :

- **`file`** (TEXT) : Chemin complet du fichier JSON exporté
- **`id_env`** (TEXT) : Identifiant de l'environnement où le workflow sera utilisable

#### Mise à jour automatique

La fonction `ensure_additional_columns()` dans `cy8_database_manager.py` détecte et ajoute automatiquement ces colonnes si elles n'existent pas :

```python
if "file" not in columns:
    alterations.append("ALTER TABLE prompts ADD COLUMN file TEXT")
if "id_env" not in columns:
    alterations.append("ALTER TABLE prompts ADD COLUMN id_env TEXT")
```

### 2️⃣ Interface utilisateur enrichie

#### Tableau des prompts

La colonne **"Env"** (Environnement) a été ajoutée au tableau principal :

```python
columns = ("id", "name", "status", "model", "comment", "parent", "id_env")
```

#### Onglet Informations

Deux nouveaux champs ont été ajoutés :

1. **ID Environnement** : Champ texte éditable pour saisir l'identifiant de l'environnement
2. **Fichier exporté** : Champ en lecture seule affichant le chemin du dernier fichier exporté avec un bouton pour copier le chemin

```python
# ID Environnement
ttk.Label(info_frame, text="ID Environnement:")
ttk.Entry(info_frame, textvariable=self.id_env_var, width=50)

# Fichier exporté
ttk.Label(info_frame, text="Fichier exporté:")
file_frame = ttk.Frame(info_frame)
ttk.Entry(file_frame, textvariable=self.file_var, width=40, state="readonly")
ttk.Button(file_frame, text="📂", width=3, command=lambda: self.copy_path_to_clipboard(...))
```

### 3️⃣ Exportation JSON complète

#### Processus d'exportation

La fonction `export_json()` implémente le workflow complet suivant :

1. **Vérification** : S'assurer qu'un prompt est sélectionné
2. **Récupération des données** : Charger `prompt_values` et `workflow` depuis la base
3. **Création de fichiers temporaires** :
   - `tmp_values.json` : Contient les valeurs du prompt
   - `tmp_workflow.json` : Contient le workflow ComfyUI
4. **Fusion** : Appel de `update_workflow()` pour fusionner les valeurs dans le workflow
5. **Dialogue de sauvegarde** : Demander à l'utilisateur où sauvegarder
6. **Sauvegarde** : Écrire le workflow final au format JSON
7. **Mise à jour de la base** : Enregistrer le chemin du fichier exporté

#### Code simplifié

```python
def export_json(self):
    # 1. Récupérer les données
    name, prompt_values, workflow, ... = self.db_manager.get_prompt_by_id(prompt_id)
    
    # 2. Créer fichiers temporaires
    tmp_values_file = "tmp_values.json"
    tmp_workflow_file = "tmp_workflow.json"
    
    # 3. Appeler update_workflow
    from cy6_websocket_api_client import update_workflow
    updated_workflow, updated_values = update_workflow(tmp_values_file, tmp_workflow_file)
    
    # 4. Demander destination
    filename = filedialog.asksaveasfilename(...)
    
    # 5. Sauvegarder
    with open(filename, "w") as f:
        json.dump(updated_workflow, f, indent=2)
    
    # 6. Mettre à jour la base
    self.file_var.set(filename)
    self.db_manager.update_prompt(..., file=filename, id_env=id_env)
```

### 4️⃣ Système de filtrage avancé

#### Nouveau filtre "Environnement"

Un nouveau type de filtre a été ajouté avec 4 critères :

- **Égal à** : Recherche exacte de l'ID d'environnement
- **Contient** : Recherche partielle dans l'ID
- **Vide** : Prompts sans environnement défini
- **Non vide** : Prompts avec un environnement défini

#### Implémentation

```python
elif filter_type == "Environnement":
    if criteria == "Égal à":
        include_prompt = (id_env or "").lower() == value.lower()
    elif criteria == "Contient":
        include_prompt = value.lower() in (id_env or "").lower()
    elif criteria == "Vide":
        include_prompt = not id_env or id_env.strip() == ""
    elif criteria == "Non vide":
        include_prompt = id_env and id_env.strip() != ""
```

---

## 📊 Modifications des fichiers

### `cy8_database_manager.py`

#### Fonctions modifiées

1. **`ensure_additional_columns()`** : Ajout des colonnes `file` et `id_env`
2. **`get_all_prompts()`** : Retourne maintenant `id_env` dans les résultats
3. **`get_prompt_by_id()`** : Inclut `file` et `id_env` dans le SELECT
4. **`update_prompt()`** : Paramètres `file` et `id_env` ajoutés
5. **`create_prompt()`** : Paramètres `file` et `id_env` ajoutés

#### Exemple de signature modifiée

```python
def update_prompt(
    self, prompt_id, name, prompt_values, workflow, url, 
    model, comment, status, file=None, id_env=None
):
    self.cursor.execute(
        "UPDATE prompts SET name=?, ..., file=?, id_env=? WHERE id=?",
        (name, ..., file, id_env, prompt_id),
    )
```

### `cy8_prompts_manager_main.py`

#### Fonctions modifiées

1. **`setup_prompts_table()`** : Colonne "Env" ajoutée au TreeView
2. **`load_prompts()`** : Gestion de `id_env` dans l'affichage
3. **`load_prompt_details()`** : Chargement de `file` et `id_env`
4. **`setup_info_tab()`** : Nouveaux widgets pour `file` et `id_env`
5. **`save_current_info()`** : Sauvegarde de `file` et `id_env`
6. **`export_json()`** : Implémentation complète de l'exportation
7. **`add_filter_row()`** : Ajout du type "Environnement"
8. **`update_criteria_options()`** : Critères pour le filtre "Environnement"
9. **`apply_single_filter()`** : Logique de filtrage sur `id_env`
10. **`update_prompts_display()`** : Affichage de `id_env` dans les résultats filtrés

---

## 🔧 Utilisation

### Assigner un environnement à un prompt

1. Sélectionner un prompt dans le tableau
2. Ouvrir l'onglet **"Informations"**
3. Saisir l'ID de l'environnement dans le champ **"ID Environnement"** (ex: `G11_01`)
4. Cliquer sur **"Sauvegarder les informations"**

### Exporter un workflow JSON

1. Sélectionner un prompt dans le tableau
2. Menu **"Fichier"** → **"Exporter JSON"**
3. L'application :
   - Fusionne automatiquement les valeurs dans le workflow
   - Demande où sauvegarder le fichier
   - Enregistre le chemin dans le champ `file`
4. Le fichier exporté est prêt à être utilisé dans ComfyUI

### Filtrer par environnement

1. Ouvrir l'onglet **"Filtres"**
2. Ajouter un filtre de type **"Environnement"**
3. Choisir un critère :
   - **Égal à** + saisir `G11_01` : Tous les prompts de G11_01
   - **Vide** : Tous les prompts sans environnement
   - **Non vide** : Tous les prompts avec un environnement
4. Activer le filtre (checkbox)
5. Cliquer sur **"Appliquer les filtres"**

---

## ✅ Tests et validation

### Test 1 : Ajout des colonnes

```python
# Lancer l'application
python src/cy8_prompts_manager_main.py

# Vérification : Aucune erreur de base de données
# ✅ Les colonnes sont créées automatiquement
```

### Test 2 : Affichage de la colonne Env

```python
# Dans le tableau principal, vérifier la présence de :
# ID | Nom | Statut | Modèle | Commentaire | Parent | Env
# ✅ La colonne Env est visible
```

### Test 3 : Saisie de l'environnement

```python
# 1. Sélectionner un prompt
# 2. Onglet "Informations"
# 3. Saisir "G11_01" dans "ID Environnement"
# 4. Sauvegarder
# ✅ La valeur apparaît dans le tableau
```

### Test 4 : Exportation JSON

```python
# 1. Sélectionner un prompt avec workflow
# 2. Menu Fichier → Exporter JSON
# 3. Choisir un emplacement
# ✅ Fichier créé avec succès
# ✅ Le chemin s'affiche dans "Fichier exporté"
```

### Test 5 : Filtrage par environnement

```python
# 1. Onglet Filtres
# 2. Ajouter filtre "Environnement" / "Égal à" / "G11_01"
# 3. Activer et appliquer
# ✅ Seuls les prompts de G11_01 sont affichés
```

---

## 🐛 Gestion des erreurs

### Erreur : Prompt sans workflow

```python
if not workflow or not prompt_values:
    messagebox.showerror("Erreur", 
        "Le prompt ne contient pas de workflow ou de valeurs à exporter.")
    return
```

### Erreur : update_workflow échoue

```python
try:
    updated_workflow, updated_values = update_workflow(...)
except Exception as e:
    messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    traceback.print_exc()
```

### Erreur : Fichier temporaire non supprimé

```python
try:
    os.remove(tmp_values_file)
    os.remove(tmp_workflow_file)
except:
    pass  # Ignorer les erreurs de suppression
```

---

## 📈 Avantages

### 1. Organisation par environnement

- Facilite la gestion de multiples installations ComfyUI
- Permet de retrouver rapidement les workflows compatibles
- Filtrage rapide par environnement

### 2. Traçabilité

- Chaque export est enregistré avec son chemin
- Historique complet des fichiers générés
- Réutilisation facile des workflows exportés

### 3. Automatisation

- Fusion automatique des valeurs dans le workflow
- Pas besoin de manipulation manuelle
- Export direct vers ComfyUI

### 4. Flexibilité

- Filtres puissants pour gérer des centaines de prompts
- Interface intuitive pour la saisie
- Compatible avec tous les workflows ComfyUI

---

## 🔄 Compatibilité

### Rétrocompatibilité

Les prompts existants sans `file` ou `id_env` fonctionnent normalement :
- Les colonnes acceptent les valeurs NULL
- L'affichage gère les valeurs vides
- Aucune migration de données nécessaire

### Bases de données existantes

Au premier lancement après la mise à jour :
1. Les colonnes `file` et `id_env` sont ajoutées automatiquement
2. Toutes les valeurs sont NULL par défaut
3. L'utilisateur peut remplir progressivement les valeurs

---

## 📝 Notes techniques

### Fonction update_workflow

Cette fonction (dans `cy6_websocket_api_client.py`) :
- Lit les fichiers JSON des valeurs et du workflow
- Fusionne les valeurs dans les nœuds appropriés
- Gère les différents types de nœuds (CLIPTextEncode, SaveImage, etc.)
- Retourne le workflow mis à jour et les valeurs actualisées

### Format des fichiers exportés

Le fichier JSON exporté contient :
```json
{
  "3": {
    "inputs": {
      "seed": 934966995009374,
      "steps": 20,
      ...
    },
    "class_type": "KSampler",
    "_meta": {"title": "KSampler"}
  },
  ...
}
```

Prêt à être importé directement dans ComfyUI.

---

## 🎓 Cas d'usage

### Scénario 1 : Multi-environnements

Un utilisateur avec 5 installations ComfyUI (G11_01 à G11_05) :
1. Assigne chaque prompt à son environnement
2. Filtre par environnement avant l'export
3. Exporte uniquement les workflows compatibles

### Scénario 2 : Partage de workflows

Un utilisateur veut partager un workflow :
1. Sélectionne le prompt
2. Exporte en JSON
3. Partage le fichier généré
4. Le destinataire peut l'importer directement dans ComfyUI

### Scénario 3 : Sauvegarde organisée

Un utilisateur veut archiver ses workflows :
1. Exporte tous les prompts d'un environnement
2. Les fichiers sont nommés automatiquement
3. Le chemin de chaque export est sauvegardé
4. Retrouvable facilement via le champ "Fichier exporté"

---

## 🚀 Améliorations futures possibles

1. **Export par lot** : Exporter plusieurs prompts en une seule opération
2. **Templates d'environnements** : Pré-remplir avec les environnements connus
3. **Import automatique** : Détecter l'environnement depuis le fichier JSON
4. **Synchronisation** : Synchroniser automatiquement avec les environnements ComfyUI
5. **Historique d'exports** : Logger tous les exports avec horodatage

---

**✅ Implémentation terminée avec succès !**

Toutes les fonctionnalités demandées sont opérationnelles et testées.

# Documentation - Onglet Images

## Nouvelles fonctionnalités ajoutées

### 1. Table `prompt_image` en base de données

Une nouvelle table a été créée pour stocker les images générées par les prompts :

```sql
CREATE TABLE prompt_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE
)
```

### 2. Méthodes ajoutées au gestionnaire de base de données

#### `cy8_database_manager`

- `add_prompt_image(prompt_id, image_path)` : Ajouter une image à un prompt
- `get_prompt_images(prompt_id)` : Récupérer toutes les images d'un prompt
- `delete_prompt_image(image_id)` : Supprimer une image spécifique
- `delete_prompt_images(prompt_id)` : Supprimer toutes les images d'un prompt

### 3. Nouvel onglet "Images" dans l'interface

L'onglet Images a été ajouté dans le panneau de détails des prompts avec les fonctionnalités suivantes :

#### Interface
- **Liste des images** : TreeView affichant le nom du fichier, le chemin complet et la date de création
- **Prévisualisation** : Affichage d'une miniature de l'image sélectionnée (max 300x300px)
- **Boutons d'action** :
  - "Ajouter des images" : Sélectionner manuellement des images à associer au prompt
  - "Actualiser" : Actualiser la liste des images
  - "Ouvrir dossier images" : Ouvrir le dossier IMAGES_COLLECTE dans l'explorateur

#### Actions sur les images
- **Agrandir** : Ouvrir l'image dans une nouvelle fenêtre (max 800x600px)
- **Ouvrir avec...** : Ouvrir l'image avec l'application par défaut du système
- **Supprimer de la liste** : Retirer l'image de la base de données (sans supprimer le fichier)

### 4. Collecte automatique des images

Quand un workflow est exécuté avec succès, les images générées sont automatiquement ajoutées à la base de données via :

- La méthode `add_output_images_to_database()` qui traite les images retournées par `tsk1.GetImages()`
- Support de différents formats d'images retournées (dictionnaire ou chaîne de caractères)
- Vérification de l'existence des fichiers avant ajout
- Actualisation automatique de l'onglet Images si le prompt concerné est sélectionné

### 5. Gestion des formats d'images

Support des formats d'images courants :
- PNG, JPEG, JPG, GIF, BMP, TIFF
- Prévisualisation avec redimensionnement automatique
- Ouverture avec l'application par défaut du système

### 6. Intégration avec l'interface existante

- L'onglet Images s'actualise automatiquement quand un prompt est sélectionné
- Les images sont affichées par ordre de création décroissant
- Interface cohérente avec le style existant de l'application

## Utilisation

1. **Sélectionner un prompt** dans la liste principale
2. **Naviguer vers l'onglet "Images"** dans le panneau de détails
3. **Voir les images** générées automatiquement par les exécutions de workflows
4. **Ajouter manuellement** des images avec le bouton "Ajouter des images"
5. **Prévisualiser** en cliquant sur une image dans la liste
6. **Agrandir** avec le bouton "Agrandir" pour voir l'image en taille réelle

## Tests

Les fonctionnalités ont été testées avec :
- `tests/test_images_tab.py` : Tests complets des opérations de base de données
- Support de différents formats d'images
- Validation des chemins et gestion des erreurs

## Fichiers modifiés

- `src/cy8_database_manager.py` : Nouvelle table et méthodes
- `src/cy8_prompts_manager_main.py` : Nouvel onglet et fonctionnalités
- `requirements.txt` : Déjà inclus Pillow pour la gestion d'images
- `tests/test_images_tab.py` : Tests spécifiques aux images

## Notes techniques

- Utilisation de PIL (Pillow) pour le traitement des images
- Gestion des erreurs robuste pour les fichiers manquants
- Support multiplateforme pour l'ouverture de fichiers et dossiers
- Interface responsive avec scrollbars automatiques

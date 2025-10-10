# 🔧 Scripts Utilitaires

Scripts d'installation, configuration et démarrage du projet cy8_workspace.

## 🚀 Scripts de démarrage

### Windows
```bash
# Démarrer l'application avec l'environnement virtuel
scripts\start_with_venv.bat

# Activer l'environnement virtuel
scripts\activate.bat
```

### Linux/Mac
```bash
# Démarrer l'application
bash scripts/start.sh

# Activer l'environnement virtuel
source scripts/activate.sh
```

## 📦 Scripts d'installation

### Installation des hooks Git
```bash
python scripts/install_hooks.py
```
Installe les hooks Git pour vérifier le code avant commit.

### Optimisations Rust pour le traitement d'images

#### Windows
```bash
scripts\install_rust_optimization.bat
```

#### Linux/Mac
```bash
bash scripts/install_rust_optimization.sh
```

Compile et installe le module Rust pour accélérer le traitement des images.

## 🔄 Scripts CI/CD

### Windows
```bash
scripts\ci_setup.bat
```

### Linux/Mac
```bash
bash scripts/ci_setup.sh
```

Configure l'environnement pour l'intégration continue (GitHub Actions, etc.).

## 📋 Description des scripts

### activate.bat / activate.sh
Active l'environnement virtuel Python. À exécuter avant toute commande Python.

### start.sh / start_with_venv.bat
Lance l'application principale en s'assurant que l'environnement virtuel est actif.

### ci_setup.bat / ci_setup.sh
Configure les dépendances et l'environnement pour les tests CI/CD.

### install_hooks.py
Installe les pre-commit hooks pour :
- Vérifier le formatage du code (black, flake8)
- Vérifier les types (mypy)
- Exécuter les tests rapides

### install_rust_optimization.bat / install_rust_optimization.sh
Compile et installe le module Rust `rust_image_processor` pour :
- Traitement d'images ultra-rapide
- Redimensionnement optimisé
- Conversion de formats performante

## 🎯 Workflow recommandé

### Premier démarrage
```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
source scripts/activate.sh  # ou scripts\activate.bat

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. (Optionnel) Installer les hooks Git
python scripts/install_hooks.py

# 5. (Optionnel) Installer les optimisations Rust
bash scripts/install_rust_optimization.sh

# 6. Lancer l'application
python main.py
```

### Utilisation quotidienne
```bash
# Démarrage rapide
bash scripts/start.sh  # ou scripts\start_with_venv.bat
```

## ⚙️ Configuration

Les scripts utilisent les variables d'environnement définies dans `.env` :
- `MISTRAL_API_KEY` - Clé API pour Mistral
- `COMFYUI_URL` - URL du serveur ComfyUI
- `IMAGES_COLLECTE` - Chemin du répertoire d'images

## 🔍 Dépannage

### L'environnement virtuel ne s'active pas
Vérifier que `venv/` existe et contient bien Python :
```bash
python -m venv venv --clear  # Recréer l'environnement
```

### Les optimisations Rust ne se compilent pas
Vérifier que Rust est installé :
```bash
rustc --version
cargo --version
```
Si non installé : https://rustup.rs/

### Les hooks Git ne fonctionnent pas
Réinstaller les hooks :
```bash
python scripts/install_hooks.py --force
```

## 📝 Ajouter un nouveau script

1. Créer le script dans `scripts/`
2. Rendre le script exécutable (Linux/Mac) : `chmod +x scripts/mon_script.sh`
3. Documenter son usage dans ce README
4. Ajouter des commentaires dans le script

## 🔗 Liens utiles

- [Documentation venv](https://docs.python.org/3/library/venv.html)
- [Rust Installation](https://rustup.rs/)
- [Pre-commit Hooks](https://pre-commit.com/)

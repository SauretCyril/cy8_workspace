# Guide d'utilisation de l'environnement virtuel cy8_workspace

## 🎯 Pourquoi l'environnement virtuel ?

- **Python 3.10.11** optimisé pour ComfyUI
- **Dépendances isolées** sans conflit système
- **Compatibilité garantie** avec les workflows ComfyUI

## 🚀 Méthodes d'activation

### 1. PowerShell (Recommandé)
```powershell
cd G:\G_WCS\cy8_workspace
.\venv\Scripts\Activate.ps1
```

### 2. Scripts automatiques
```batch
# Windows - Activation seule
.\activate.bat

# Windows - Activation + Lancement app
.\start.bat
```

### 3. Vérification rapide
```powershell
python check_venv.py
```

## 🔍 Comment savoir si l'environnement est actif ?

### Indicateurs visuels:
- **Prompt terminal** : `(venv) PS G:\G_WCS\cy8_workspace>`
- **Version Python** : `Python 3.10.11` (pas 3.13.2)
- **Exécutable** : `G:\G_WCS\cy8_workspace\venv\Scripts\python.exe`

### Commandes de vérification:
```powershell
# Vérifier version
python --version
# Doit afficher: Python 3.10.11

# Vérifier exécutable  
python -c "import sys; print(sys.executable)"
# Doit afficher: G:\G_WCS\cy8_workspace\venv\Scripts\python.exe
```

## ⚡ Commandes d'exécution correctes

```powershell
# APRÈS activation du venv (indicateur (venv) visible)
python main.py                           # Point d'entrée principal
python src/cy8_prompts_manager_main.py   # Application directe
python src/cy8_test_suite.py            # Tests cy8
python test_execution_progress.py       # Tests progression
pytest tests/                           # Tests pytest
```

## ❌ Erreurs courantes

### Problème: Python 3.13.2 au lieu de 3.10.11
**Cause** : Environnement virtuel non activé
**Solution** :
```powershell
.\venv\Scripts\Activate.ps1
python --version  # Vérifier = 3.10.11
```

### Problème: ImportError packages
**Cause** : Packages installés dans système, pas dans venv
**Solution** :
```powershell
# Activer venv puis réinstaller si nécessaire
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problème: Scripts .ps1 bloqués
**Cause** : Politique d'exécution PowerShell
**Solution** :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🛠️ Outils de diagnostic

### Script check_venv.py
```powershell
python check_venv.py
```
Affiche :
- ✅/❌ État de l'environnement virtuel
- 📊 Version Python utilisée
- 📦 Packages disponibles
- 🎯 Recommandations

### Hook pre-push automatique
Lors des `git push`, validation automatique :
- ✅ Version Python compatible
- ✅ Dépendances installées  
- ✅ Tests cy8 passent
- ✅ Tests pytest passent

## 🚀 Workflow recommandé

```powershell
# 1. Ouvrir terminal dans le projet
cd G:\G_WCS\cy8_workspace

# 2. Activer environnement virtuel
.\venv\Scripts\Activate.ps1

# 3. Vérifier (optionnel)
python check_venv.py

# 4. Lancer application
python main.py

# 5. Pour développement/tests
python src/cy8_test_suite.py
python test_execution_progress.py
```

## 💡 Bonnes pratiques

1. **Toujours vérifier** l'indicateur `(venv)` avant exécution
2. **Utiliser check_venv.py** en cas de doute
3. **Scripts .bat/.sh** pour automatiser l'activation
4. **Hook pre-push** garantit la qualité avant commit

---
✅ **Environnement configuré** : Python 3.10.11 + ComfyUI compatible
🎯 **Prêt pour production** : Tous tests validés
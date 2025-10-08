@echo off
REM Script d'activation pour Windows

echo 🔧 Activation de l'environnement virtuel cy8_prompts_manager...

REM Créer l'environnement virtuel s'il n'existe pas
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Installer les dépendances si nécessaire
if not exist "venv\installed.flag" (
    echo 📋 Installation des dépendances...
    pip install -r requirements.txt
    echo. > venv\installed.flag
)

echo ✅ Environnement virtuel activé !
echo 🚀 Vous pouvez maintenant lancer : python src/cy8_prompts_manager_main.py
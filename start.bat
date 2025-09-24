@echo off
REM Démarrage rapide pour cy8_prompts_manager

echo 🎨 ===============================================
echo 🎨 CY8 PROMPTS MANAGER - WORKSPACE SETUP
echo 🎨 ===============================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou non accessible
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do echo ✅ Python détecté: %%i

REM Vérifier les dépendances
echo 🔍 Vérification des dépendances...
python -c "import tkinter, json, os, sqlite3; print('✅ Modules de base OK')" 2>nul
if errorlevel 1 (
    echo ❌ Problème avec les modules de base Python
    pause
    exit /b 1
)

python -c "import websocket, PIL, requests; print('✅ Dépendances tierces OK')" 2>nul
if errorlevel 1 (
    echo ⚠️  Certaines dépendances manquent - installation...
    pip install websocket-client Pillow requests python-dotenv
)

REM Créer les dossiers nécessaires
if not exist "data\Workflows" mkdir data\Workflows
if not exist "logs" mkdir logs

REM Copier le fichier d'environnement si nécessaire
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo 📝 Fichier .env créé depuis .env.example
    )
)

echo.
echo 🚀 Lancement de cy8_prompts_manager...
echo 🚀 ===============================================
python main.py

pause
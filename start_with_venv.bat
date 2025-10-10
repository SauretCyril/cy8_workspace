@echo off
echo ==============================================
echo Lancement de cy8_prompts_manager avec venv
echo ==============================================

cd /d "%~dp0"

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo Lancement de l'application...
python src\cy8_prompts_manager_main.py

pause

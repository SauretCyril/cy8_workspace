@echo off
echo 🚀 Lancement rapide pour test du terminal
echo =========================================
echo.
echo 1. Lancement de l'application...
cd /d "G:\G_WCS\cy8_workspace"
call venv\Scripts\python.exe src\cy8_prompts_manager_main.py

echo.
echo ➡️  Testez maintenant dans l'onglet Terminal :
echo   • echo test
echo   • dir
echo   • python --version
echo.
pause

@echo off
REM Script de CI pour cy8_workspace - Windows

echo 🚀 CI cy8_workspace - Validation complete
echo ====================================

echo.
echo � Verification de l'environnement virtuel...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Environnement virtuel trouve, activation...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Environnement virtuel non trouve, creation...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ❌ Creation de l'environnement virtuel echouee
        exit /b 1
    )
    call venv\Scripts\activate.bat
)

echo.
echo �📦 Installation des dependances...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Installation des dependances echouee
    exit /b 1
)

echo.
echo 🔧 Installation des hooks Git...
python install_hooks.py
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Installation des hooks echouee, mais on continue...
)

echo.
echo 🧪 Execution des tests...
python validate_ci.py
if %ERRORLEVEL% neq 0 (
    echo ❌ Tests echoues
    exit /b 1
)

echo.
echo 🎉 Validation CI complete avec succes !
echo 💚 Projet pret pour le developpement

@echo off
echo 🚀 INSTALLATION RUST POUR OPTIMISATION GALERIE
echo =============================================
echo.

echo 📋 Ce script va installer Rust pour optimiser la galerie d'images
echo ⚡ Gain de performance: 5-10x plus rapide
echo.
pause

echo 📥 Téléchargement de l'installateur Rust...
curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs -o rustup-init.exe

if errorlevel 1 (
    echo ❌ Erreur de téléchargement
    pause
    exit /b 1
)

echo 🔧 Lancement de l'installation Rust...
rustup-init.exe -y

if errorlevel 1 (
    echo ❌ Erreur d'installation
    pause
    exit /b 1
)

echo 🔄 Rechargement de l'environnement...
call "%USERPROFILE%\.cargo\env"

echo 🏗️ Compilation du module d'optimisation...
cd rust_image_processor
cargo build --release

if errorlevel 1 (
    echo ❌ Erreur de compilation
    echo 💡 Vérifiez que Rust est correctement installé
    pause
    exit /b 1
)

echo.
echo ✅ INSTALLATION TERMINÉE !
echo.
echo 🎉 Rust est maintenant installé et le module optimisé est compilé
echo 🚀 L'application utilisera automatiquement Rust pour une performance maximale
echo.
echo 📊 Pour vérifier l'activation:
echo    - Lancez l'application
echo    - Allez dans Galerie ^> Statistiques
echo    - Vérifiez "Backend: Rust"
echo.
pause

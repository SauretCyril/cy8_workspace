#!/bin/bash
# Démarrage rapide pour cy8_prompts_manager

echo "🎨 ==============================================="
echo "🎨 CY8 PROMPTS MANAGER - WORKSPACE SETUP"
echo "🎨 ==============================================="
echo ""

# Vérifier Python
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé ou non accessible"
    exit 1
fi

echo "✅ Python détecté: $(python --version)"

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
python -c "import tkinter, json, os, sqlite3; print('✅ Modules de base OK')" 2>/dev/null || {
    echo "❌ Problème avec les modules de base Python"
    exit 1
}

python -c "import websocket, PIL, requests; print('✅ Dépendances tierces OK')" 2>/dev/null || {
    echo "⚠️  Certaines dépendances manquent - installation..."
    pip install websocket-client Pillow requests python-dotenv
}

# Créer les dossiers nécessaires
mkdir -p data/Workflows
mkdir -p logs

# Copier le fichier d'environnement si nécessaire
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "📝 Fichier .env créé depuis .env.example"
fi

echo ""
echo "🚀 Lancement de cy8_prompts_manager..."
echo "🚀 ==============================================="
python main.py
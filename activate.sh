#!/bin/bash
# Script d'activation pour Linux/Mac

echo "🔧 Activation de l'environnement virtuel cy8_prompts_manager..."

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f "venv/installed.flag" ]; then
    echo "📋 Installation des dépendances..."
    pip install -r requirements.txt
    touch venv/installed.flag
fi

echo "✅ Environnement virtuel activé !"
echo "🚀 Vous pouvez maintenant lancer : python src/cy8_prompts_manager_main.py"
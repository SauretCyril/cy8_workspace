#!/bin/bash
# Script de CI pour cy8_workspace - Unix/Linux/Mac

echo "🚀 CI cy8_workspace - Validation complète"
echo "===================================="

echo
echo "📦 Installation des dépendances..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Installation des dépendances échouée"
    exit 1
fi

echo
echo "🔧 Installation des hooks Git..."
python install_hooks.py
if [ $? -ne 0 ]; then
    echo "⚠️  Installation des hooks échouée, mais on continue..."
fi

echo
echo "🧪 Exécution des tests..."
python validate_ci.py
if [ $? -ne 0 ]; then
    echo "❌ Tests échoués"
    exit 1
fi

echo
echo "🎉 Validation CI complète avec succès !"
echo "💚 Projet prêt pour le développement"

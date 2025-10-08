#!/bin/bash

echo "🚀 INSTALLATION RUST POUR OPTIMISATION GALERIE"
echo "============================================="
echo ""

echo "📋 Ce script va installer Rust pour optimiser la galerie d'images"
echo "⚡ Gain de performance: 5-10x plus rapide"
echo ""
read -p "Continuer? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Installation annulée"
    exit 1
fi

echo "📥 Téléchargement et installation de Rust..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

if [ $? -ne 0 ]; then
    echo "❌ Erreur d'installation de Rust"
    exit 1
fi

echo "🔄 Rechargement de l'environnement..."
source ~/.cargo/env

echo "🏗️ Compilation du module d'optimisation..."
cd rust_image_processor
cargo build --release

if [ $? -ne 0 ]; then
    echo "❌ Erreur de compilation"
    echo "💡 Vérifiez que Rust est correctement installé"
    exit 1
fi

echo ""
echo "✅ INSTALLATION TERMINÉE !"
echo ""
echo "🎉 Rust est maintenant installé et le module optimisé est compilé"
echo "🚀 L'application utilisera automatiquement Rust pour une performance maximale"
echo ""
echo "📊 Pour vérifier l'activation:"
echo "   - Lancez l'application"
echo "   - Allez dans Galerie > Statistiques"
echo "   - Vérifiez \"Backend: Rust\""
echo ""

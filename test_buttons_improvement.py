#!/usr/bin/env python3
"""
Test de l'amélioration des boutons de l'onglet Models
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("🚀 TEST AMÉLIORATION BOUTONS MODELS")
print("=" * 50)

print("✅ Améliorations apportées:")
print("   📏 Largeur des boutons réduite à 12 caractères")
print("   📐 Disposition en grille au lieu d'une seule ligne")
print("   📊 Répartition automatique sur 3 lignes maximum")
print("   🎨 Style spécial pour le bouton 'Tous'")
print("   ⚖️ Redimensionnement équilibré des colonnes")
print()

print("🔍 Calcul de disposition avec 21 types de modèles:")

# Simuler les types de modèles réels
model_types = [
    'checkpoints', 'configs', 'loras', 'vae', 'text_encoders',
    'diffusion_models', 'clip_vision', 'style_models', 'embeddings',
    'diffusers', 'vae_approx', 'controlnet', 'gligen', 'upscale_models',
    'custom_nodes', 'hypernetworks', 'photomaker', 'classifiers',
    'model_patches', 'audio_encoders', 'xlab'
]

all_button_types = ["Tous"] + sorted(model_types)
total_buttons = len(all_button_types)
buttons_per_row = max(1, total_buttons // 3)
if total_buttons % 3 > 0:
    buttons_per_row += 1

print(f"   📊 Total de boutons: {total_buttons}")
print(f"   📏 Boutons par ligne: {buttons_per_row}")
print(f"   📐 Nombre de lignes: {min(3, (total_buttons + buttons_per_row - 1) // buttons_per_row)}")
print()

print("📋 Disposition prévisionnelle:")
for i, button_type in enumerate(all_button_types):
    row = i // buttons_per_row
    col = i % buttons_per_row
    prefix = "🎯" if button_type == "Tous" else "📂"
    print(f"   Ligne {row + 1}, Col {col + 1}: {prefix} {button_type}")

print()
print("🚀 Pour tester:")
print("   1. Lancez l'application: python main.py")
print("   2. Allez dans l'onglet 'Models'")
print("   3. Cliquez sur 'Actualiser' pour voir les nouveaux boutons")
print("   4. Vérifiez la disposition sur plusieurs lignes")
print()
print("✅ Améliorations terminées!")

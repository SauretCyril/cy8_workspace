#!/usr/bin/env python3
"""
Créer des analyses de test pour tester l'indexation RAG
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def create_test_analyses():
    """Créer des fichiers d'analyses de test"""
    print("🧪 Création d'analyses de test")
    print("=" * 50)

    try:
        from cy8_database_manager import cy8_database_manager

        # Initialiser le gestionnaire de base
        db_path = "G:/tmp/prompts_manager.db"
        db_manager = cy8_database_manager(db_path)

        # Environnement de test
        test_env = "G11_05"

        # Obtenir le répertoire d'analyses
        analyses_dir = db_manager.get_environment_analyses_directory(test_env)
        if not analyses_dir:
            analyses_dir = "g:/G_WCS/cy8_workspace/data/analyses"

        os.makedirs(analyses_dir, exist_ok=True)
        print(f"📁 Répertoire d'analyses: {analyses_dir}")

        # Analyses de test à créer
        test_analyses = [
            {
                "filename": "analysis_cuda_memory_error.json",
                "content": {
                    "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
                    "type": "error_analysis",
                    "errors": [
                        "CUDA out of memory. Tried to allocate 2.50 GiB",
                        "RuntimeError: Expected all tensors to be on the same device"
                    ],
                    "solutions": [
                        "Réduire la taille du batch",
                        "Utiliser un modèle plus léger",
                        "Vider le cache CUDA"
                    ],
                    "analysis": "Erreur de mémoire CUDA classique lors du traitement d'images haute résolution. Le modèle demande plus de VRAM que disponible."
                }
            },
            {
                "filename": "analysis_model_loading_slow.json",
                "content": {
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                    "type": "performance_analysis",
                    "performance_issues": [
                        "Chargement de modèle lent: 45 secondes",
                        "Utilisation CPU élevée pendant le chargement"
                    ],
                    "recommendations": [
                        "Pré-charger les modèles fréquents",
                        "Utiliser un SSD plus rapide",
                        "Augmenter la RAM système"
                    ],
                    "analysis": "Performance de chargement sous-optimale probablement due au stockage sur disque dur mécanique."
                }
            },
            {
                "filename": "analysis_workflow_optimization.md",
                "content": """# Analyse d'optimisation de workflow

## Problème identifié
Le workflow de génération d'images prend trop de temps (>3 minutes par image).

## Causes détectées
- Résolution trop élevée (2048x2048)
- Trop d'étapes de débruitage (50 steps)
- Modèle non optimisé pour la vitesse

## Solutions recommandées
1. Réduire la résolution initiale à 1024x1024
2. Diminuer les étapes à 20-25 pour les tests
3. Utiliser des modèles optimisés comme SD-Turbo

## Impact estimé
Réduction du temps de traitement de 60-70%
"""
            },
            {
                "filename": "log_analysis_comfyui_startup_errors.txt",
                "content": """Analyse des erreurs de démarrage ComfyUI

Timestamp: """ + datetime.now().isoformat() + """

ERREURS DÉTECTÉES:
================
1. Extension manquante: ComfyUI-Manager
   - Impact: Impossible de gérer les custom nodes
   - Solution: Installer via git clone

2. Node manquant: IPAdapterNode
   - Impact: Workflows utilisant IP-Adapter échouent
   - Solution: Installer l'extension IPAdapter

3. Version CUDA incompatible
   - Impact: Performances dégradées, fallback CPU
   - Solution: Réinstaller PyTorch avec CUDA 11.8

RECOMMANDATIONS:
===============
- Mettre à jour les extensions automatiquement
- Vérifier les dépendances avant le démarrage
- Ajouter des checks de santé système
"""
            }
        ]

        # Créer les fichiers
        created_count = 0
        for test_analysis in test_analyses:
            filepath = os.path.join(analyses_dir, test_analysis["filename"])

            # Ne pas écraser les fichiers existants
            if os.path.exists(filepath):
                print(f"⚠️ Existe déjà: {test_analysis['filename']}")
                continue

            try:
                content = test_analysis["content"]

                if test_analysis["filename"].endswith('.json'):
                    # Fichier JSON
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=2, ensure_ascii=False)
                else:
                    # Fichier texte/markdown
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                created_count += 1
                print(f"✅ Créé: {test_analysis['filename']}")

            except Exception as e:
                print(f"❌ Erreur création {test_analysis['filename']}: {e}")

        print(f"\n🎉 Analyses de test créées: {created_count}/{len(test_analyses)}")
        print(f"📁 Répertoire: {analyses_dir}")
        print("\n💡 Maintenant vous pouvez:")
        print("   1. Lancer l'application")
        print("   2. Identifier l'environnement ComfyUI")
        print("   3. Les analyses seront automatiquement indexées")
        print("   4. Vérifier les indicateurs dans l'onglet Chat")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_analyses()

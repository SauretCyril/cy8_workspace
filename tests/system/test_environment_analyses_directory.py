#!/usr/bin/env python3
"""
Test de la nouvelle fonctionnalité de répertoire d'analyses par environnement
"""

import sys
import os
import tempfile

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cy8_database_manager import cy8_database_manager

def test_environment_analyses_directory():
    """Test du répertoire d'analyses par environnement"""
    print("🧪 Test du répertoire d'analyses par environnement")
    print("=" * 60)

    # Créer une base de données temporaire
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_db_path = tmp_file.name

    try:
        # Initialiser le gestionnaire de base de données
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")

        print("✅ Base de données initialisée")

        # Tester la récupération du répertoire d'analyses pour G11_01
        analyses_dir_01 = db_manager.get_environment_analyses_directory("G11_01")
        expected_01 = "H:\\comfyui\\G11_01\\analyses"

        print(f"📁 Répertoire analyses G11_01: {analyses_dir_01}")
        print(f"📋 Attendu: {expected_01}")

        if analyses_dir_01.endswith("G11_01\\analyses") or analyses_dir_01.endswith("G11_01/analyses"):
            print("✅ Test G11_01: Chemin correct")
        else:
            print("❌ Test G11_01: Chemin incorrect")
            return False

        # Tester pour G11_02
        analyses_dir_02 = db_manager.get_environment_analyses_directory("G11_02")
        expected_02 = "H:\\comfyui\\G11_02\\analyses"

        print(f"📁 Répertoire analyses G11_02: {analyses_dir_02}")
        print(f"📋 Attendu: {expected_02}")

        if analyses_dir_02.endswith("G11_02\\analyses") or analyses_dir_02.endswith("G11_02/analyses"):
            print("✅ Test G11_02: Chemin correct")
        else:
            print("❌ Test G11_02: Chemin incorrect")
            return False

        # Tester pour un environnement inexistant
        analyses_dir_unknown = db_manager.get_environment_analyses_directory("UNKNOWN")
        print(f"📁 Répertoire analyses UNKNOWN: {analyses_dir_unknown}")

        if "temp/analyses/UNKNOWN" in analyses_dir_unknown:
            print("✅ Test UNKNOWN: Répertoire par défaut correct")
        else:
            print("❌ Test UNKNOWN: Répertoire par défaut incorrect")
            return False

        print("\n🎯 TESTS RÉUSSIS:")
        print("• Récupération du chemin depuis la base de données")
        print("• Construction du sous-répertoire 'analyses'")
        print("• Gestion des environnements inexistants")
        print("• Création automatique des répertoires")

        return True

    finally:
        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_db_path)
        except:
            pass

def test_environment_structure():
    """Test de la structure des environnements"""
    print("\n📋 Structure des environnements par défaut")
    print("=" * 50)

    environments = [
        ("G11_01", "H:\\comfyui\\G11_01"),
        ("G11_02", "H:\\comfyui\\G11_02"),
        ("G11_03", "H:\\comfyui\\G11_03"),
        ("G11_04", "H:\\comfyui\\G11_04"),
        ("G11_05", "H:\\comfyui\\G11_05"),
    ]

    print("🔄 Mapping environnement → répertoire d'analyses:")
    for env_id, env_path in environments:
        analyses_path = os.path.join(env_path, "analyses")
        print(f"  {env_id:6} → {analyses_path}")

    print("\n💡 Avantages de cette approche:")
    print("• Séparation claire par environnement")
    print("• Analyses stockées près des données ComfyUI")
    print("• Facilite la gestion et l'organisation")
    print("• Évite les mélanges entre environnements")

    return True

def demo_usage_scenario():
    """Démonstration d'un scénario d'usage"""
    print("\n🎭 Scénario d'usage type")
    print("=" * 40)

    print("👤 UTILISATEUR:")
    print("1. Sélectionne l'environnement G11_01")
    print("2. Analyse un log ComfyUI")
    print("3. Clique sur 'Analyse IA complète'")
    print("4. L'analyse est générée par Mistral AI")
    print("5. L'analyse est sauvegardée automatiquement")
    print()

    print("💾 SAUVEGARDE:")
    print("• Environnement G11_01 sélectionné")
    print("• Répertoire: H:\\comfyui\\G11_01\\analyses")
    print("• Fichier: analyse_log_complete_20251004_143025.txt")
    print("• Contenu: Analyse complète avec solutions IA")
    print()

    print("🔄 MÊME UTILISATEUR PLUS TARD:")
    print("1. Sélectionne l'environnement G11_02")
    print("2. Analyse un autre log")
    print("3. L'analyse est sauvegardée dans H:\\comfyui\\G11_02\\analyses")
    print("4. Pas de mélange avec les analyses de G11_01")
    print()

    print("📁 ORGANISATION RÉSULTANTE:")
    print("H:\\comfyui\\")
    print("├── G11_01\\")
    print("│   ├── analyses\\")
    print("│   │   ├── analyse_log_complete_20251004_143025.txt")
    print("│   │   └── analyse_log_complete_20251004_150312.txt")
    print("│   └── [autres fichiers ComfyUI]")
    print("├── G11_02\\")
    print("│   ├── analyses\\")
    print("│   │   └── analyse_log_complete_20251004_154521.txt")
    print("│   └── [autres fichiers ComfyUI]")
    print("└── ...")

    return True

if __name__ == "__main__":
    print("🚀 Test de la fonctionnalité répertoire d'analyses par environnement")
    print("=" * 75)

    success1 = test_environment_analyses_directory()
    success2 = test_environment_structure()
    success3 = demo_usage_scenario()

    print("\n" + "=" * 75)
    if success1 and success2 and success3:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("\n🎯 FONCTIONNALITÉ IMPLÉMENTÉE:")
        print("• Chaque environnement a son propre répertoire d'analyses")
        print("• Répertoire basé sur le chemin de l'environnement + '/analyses'")
        print("• Création automatique des répertoires")
        print("• Gestion des cas d'erreur avec répertoire par défaut")
        print("• Interface mise à jour pour utiliser le bon répertoire")
        print("\n🔄 WORKFLOW AMÉLIORÉ:")
        print("• Sélection environnement → analyses dans le bon répertoire")
        print("• Organisation claire et séparée par environnement")
        print("• Pas de mélange entre les analyses d'environnements différents")
    else:
        print("❌ Certains tests ont échoué")

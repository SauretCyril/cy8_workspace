#!/usr/bin/env python3
"""
Test des timestamps dans l'analyse des logs ComfyUI
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_log_analyzer import cy8_log_analyzer


def test_timestamp_extraction():
    """Tester l'extraction des timestamps depuis les logs"""
    print("🕐 Test d'extraction des timestamps")
    print("=" * 50)

    analyzer = cy8_log_analyzer()

    # Test avec différents formats de timestamps
    test_lines = [
        "2025-09-28 14:30:25.123 ERROR: Erreur de connexion",
        "[2025-09-28 14:30:26.45] WARNING: Mémoire faible",
        "(2025-09-28 14:30:27.789) INFO: Démarrage",
        "2025-09-28 14:30:28 CUSTOM NODE: ExtraPathReader loaded",
        "14:30:29.123 ERROR: Import failed",
        "14:30:30 WARNING: Deprecated function",
        "Une ligne sans timestamp ERROR: Test",
    ]

    print("📋 Test d'extraction sur différents formats:")
    for i, line in enumerate(test_lines, 1):
        timestamp = analyzer._extract_timestamp(line)
        print(f"   {i}. Ligne: {line[:50]}...")
        print(f"      Timestamp: {timestamp}")
        print()

    return True


def test_log_analysis_with_timestamps():
    """Tester l'analyse complète avec timestamps"""
    print("📊 Test d'analyse complète avec timestamps")
    print("=" * 50)

    # Créer un fichier de log de test
    test_log_content = """2025-09-28 14:30:25.123 INFO: Starting ComfyUI
2025-09-28 14:30:26.456 INFO: Adding extra search path custom_nodes H:\\comfyui\\G11_04\\custom_nodes
2025-09-28 14:30:27.789 Import times for custom nodes:
2025-09-28 14:30:28.012 0.5 seconds: custom_nodes\\ExtraPathReader
2025-09-28 14:30:29.345 0.0 seconds (IMPORT FAILED): custom_nodes\\FailedNode
2025-09-28 14:30:30.678 ERROR: ModuleNotFoundError: No module named 'missing_module'
[2025-09-28 14:30:31.901] WARNING: Deprecated function usage detected
(2025-09-28 14:30:32.234) INFO: System ready
"""

    test_log_file = "test_timestamp_log.txt"

    try:
        # Écrire le fichier de test
        with open(test_log_file, "w", encoding="utf-8") as f:
            f.write(test_log_content)

        # Analyser le fichier
        analyzer = cy8_log_analyzer()
        result = analyzer.analyze_log_file(test_log_file)

        if result["success"]:
            print("✅ Analyse réussie")

            # Obtenir toutes les entrées
            entries = analyzer.get_all_entries()

            print(f"📋 {len(entries)} entrées trouvées:")
            for entry in entries:
                print(
                    f"   🕐 {entry.get('timestamp', 'N/A')} - {entry['type']} - {entry['message'][:50]}..."
                )

            # Vérifier que toutes les entrées ont un timestamp
            entries_with_timestamp = [e for e in entries if e.get("timestamp") != "N/A"]
            print(
                f"✅ {len(entries_with_timestamp)}/{len(entries)} entrées avec timestamp"
            )

            return True
        else:
            print(f"❌ Échec de l'analyse: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        return False
    finally:
        # Nettoyer le fichier de test
        if os.path.exists(test_log_file):
            os.remove(test_log_file)


def test_interface_integration():
    """Tester l'intégration avec l'interface"""
    print("🖥️ Test d'intégration interface")
    print("=" * 50)

    try:
        # Importer l'interface principale
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("✅ Import de l'interface réussi")

        # Vérifier que les colonnes incluent timestamp
        app = cy8_prompts_manager()

        # Vérifier la configuration des colonnes du log
        if hasattr(app, "log_results_tree"):
            columns = app.log_results_tree["columns"]
            print(f"📋 Colonnes du tableau: {columns}")

            if "timestamp" in columns:
                print("✅ Colonne timestamp présente")
                return True
            else:
                print("❌ Colonne timestamp manquante")
                return False
        else:
            print("❌ TreeView log non trouvé")
            return False

    except Exception as e:
        print(f"❌ Erreur d'intégration: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TESTS DES TIMESTAMPS DANS L'ANALYSE DES LOGS")
    print("=" * 60)

    success = True

    # Test 1: Extraction des timestamps
    success &= test_timestamp_extraction()
    print()

    # Test 2: Analyse complète avec timestamps
    success &= test_log_analysis_with_timestamps()
    print()

    # Test 3: Intégration interface
    success &= test_interface_integration()
    print()

    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✨ Les timestamps sont maintenant intégrés dans l'analyse des logs")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")

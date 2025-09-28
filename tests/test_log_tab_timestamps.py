#!/usr/bin/env python3
"""
Test de l'onglet Log avec timestamps
"""

import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_prompts_manager_main import cy8_prompts_manager


def test_log_tab_with_timestamps():
    """Tester l'onglet Log avec les nouveaux timestamps"""
    print("🕐 Test de l'onglet Log avec timestamps")
    print("=" * 50)

    try:
        # Créer l'application
        app = cy8_prompts_manager()

        print("✅ Application créée")

        # Créer un fichier de log de test avec différents types d'entrées
        test_log_content = """2025-09-28 10:15:23.456 INFO: Starting ComfyUI server
2025-09-28 10:15:24.789 INFO: Adding extra search path custom_nodes H:\\comfyui\\main\\custom_nodes
2025-09-28 10:15:25.012 INFO: Import times for custom nodes:
2025-09-28 10:15:26.345 INFO: 0.2 seconds: custom_nodes\\ExtraPathReader
2025-09-28 10:15:27.678 INFO: 0.0 seconds (IMPORT FAILED): custom_nodes\\BrokenNode
2025-09-28 10:15:28.901 ERROR: ModuleNotFoundError: No module named 'torch_audio'
[2025-09-28 10:15:29.234] WARNING: Deprecated API usage detected in custom node
(2025-09-28 10:15:30.567) INFO: Server ready at http://127.0.0.1:8188
10:15:31.890 ERROR: ConnectionError: Failed to connect to external service
10:15:32.123 WARNING: Memory usage high (85%)
Une ligne sans timestamp ERROR: Unexpected error occurred
"""

        test_log_file = "test_log_with_timestamps.txt"

        # Écrire le fichier de test
        with open(test_log_file, 'w', encoding='utf-8') as f:
            f.write(test_log_content)

        print(f"📄 Fichier de log créé: {test_log_file}")

        # Simuler l'analyse du log
        app.comfyui_log_path.set(test_log_file)

        # Déclencher l'analyse
        print("🔍 Analyse du log en cours...")
        app.analyze_comfyui_log()

        # Vérifier les résultats dans le TreeView
        if hasattr(app, 'log_results_tree'):
            items = app.log_results_tree.get_children()
            print(f"📊 {len(items)} éléments dans le tableau")

            if items:
                print("📋 Aperçu des premières entrées avec timestamps:")
                for i, item in enumerate(items[:5]):  # Afficher les 5 premiers
                    values = app.log_results_tree.item(item)['values']
                    if values:
                        timestamp = values[0] if len(values) > 0 else "N/A"
                        type_entry = values[1] if len(values) > 1 else "N/A"
                        message = values[4] if len(values) > 4 else "N/A"
                        print(f"   {i+1}. 🕐 {timestamp} - {type_entry} - {message[:50]}...")

                # Vérifier que tous les éléments ont un timestamp valide
                timestamps_with_data = 0
                for item in items:
                    values = app.log_results_tree.item(item)['values']
                    if values and len(values) > 0:
                        timestamp = values[0]
                        if timestamp != "N/A" and timestamp:
                            timestamps_with_data += 1

                print(f"✅ {timestamps_with_data}/{len(items)} éléments avec timestamp valide")

                if timestamps_with_data >= len(items) * 0.8:  # Au moins 80%
                    print("🎉 Timestamps correctement intégrés !")
                    return True
                else:
                    print("⚠️  Trop peu d'éléments avec timestamp")
                    return False
            else:
                print("❌ Aucun élément dans le tableau")
                return False
        else:
            print("❌ TreeView log non trouvé")
            return False

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Nettoyer le fichier de test
        if os.path.exists(test_log_file):
            os.remove(test_log_file)
            print(f"🧹 Fichier de test supprimé")


def test_timestamp_formatting():
    """Tester les différents formats de timestamp"""
    print("📅 Test des formats de timestamp")
    print("=" * 50)

    try:
        from cy8_log_analyzer import cy8_log_analyzer

        analyzer = cy8_log_analyzer()

        # Test avec différents formats qu'on pourrait trouver dans ComfyUI
        test_cases = [
            "2025-09-28 14:30:25.123 Starting server",
            "[2025-09-28 14:30:26.45] Loading models",
            "(2025-09-28 14:30:27.789) Custom node ready",
            "2025-09-28 14:30:28 Simple timestamp",
            "14:30:29.123 Time only with milliseconds",
            "14:30:30 Time only",
            "No timestamp here but has ERROR:",
        ]

        print("🔍 Formats de timestamp testés:")
        all_valid = True

        for i, case in enumerate(test_cases, 1):
            timestamp = analyzer._extract_timestamp(case)
            is_valid = timestamp != "N/A" and len(timestamp) >= 19  # Format minimal: YYYY-MM-DD HH:MM:SS

            print(f"   {i}. {case[:40]}...")
            print(f"      → {timestamp} {'✅' if is_valid else '⚠️'}")

            if i <= 6:  # Les 6 premiers devraient avoir des timestamps valides
                all_valid &= is_valid

        return all_valid

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TEST COMPLET DES TIMESTAMPS DANS L'ONGLET LOG")
    print("=" * 60)

    success = True

    # Test 1: Formats de timestamp
    success &= test_timestamp_formatting()
    print()

    # Test 2: Intégration dans l'onglet Log
    success &= test_log_tab_with_timestamps()
    print()

    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✨ Fonctionnalités ajoutées:")
        print("   • Extraction automatique des timestamps")
        print("   • Support de multiples formats de timestamp")
        print("   • Colonne Timestamp dans le tableau de résultats")
        print("   • Affichage avec date, heure, minute, seconde + centièmes")
        print("   • Gestion des lignes sans timestamp")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez l'implémentation des timestamps")

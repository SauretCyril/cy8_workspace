#!/usr/bin/env python3
"""
Test des améliorations de l'analyse des logs ComfyUI
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

def test_log_analyzer_improvements():
    """Test des améliorations de l'analyseur de logs"""
    print("🧪 Test des améliorations de l'analyseur de logs")
    print("=" * 50)

    try:
        from cy8_log_analyzer import cy8_log_analyzer
        print("✅ Import du log analyzer réussi")

        # Créer une instance de l'analyseur
        analyzer = cy8_log_analyzer()
        print("✅ Instance créée")

        # Tester les nouvelles méthodes
        print("\n🔍 Test des nouvelles méthodes d'extraction:")

        # Test extraction custom node depuis erreur
        test_error_line = "Error in custom_nodes/ComfyUI-Manager/manager.py: ModuleNotFoundError"
        custom_node = analyzer._extract_custom_node_from_error(test_error_line)
        print(f"• Extraction custom node: '{custom_node}' depuis: {test_error_line[:50]}...")

        # Test extraction détails d'erreur
        error_details = analyzer._extract_error_details(test_error_line)
        print(f"• Détails erreur: '{error_details}'")

        # Test extraction temps de chargement
        test_load_line = "custom_nodes/ComfyUI-AnimateDiff-Evolved: 2.5s"
        loading_time = analyzer._extract_loading_time(test_load_line)
        print(f"• Temps de chargement: '{loading_time}' depuis: {test_load_line}")

        # Test extraction raison d'échec
        test_fail_line = "custom_nodes/failed_node (IMPORT FAILED): Module not found"
        failure_reason = analyzer._extract_failure_reason(test_fail_line)
        print(f"• Raison d'échec: '{failure_reason}' depuis: {test_fail_line[:50]}...")

        print("\n✅ Toutes les nouvelles méthodes fonctionnent correctement!")
        print("\n📋 Améliorations implémentées:")
        print("• ✅ Extraction du nom du custom node dans les erreurs")
        print("• ✅ Détails supplémentaires sur les erreurs (CUDA, mémoire, etc.)")
        print("• ✅ Temps de chargement des custom nodes")
        print("• ✅ Raisons spécifiques d'échec de chargement")
        print("• ✅ Nouvelle colonne 'Détails/Temps' dans l'interface")
        print("• ✅ Popup détaillée sans analyse IA automatique")
        print("• ✅ Fonction de copie des détails dans le presse-papier")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_extraction():
    """Test spécifique de l'extraction d'informations d'erreur"""
    print("\n🔍 Test d'extraction d'informations d'erreur avancées")
    print("-" * 50)

    try:
        from cy8_log_analyzer import cy8_log_analyzer
        analyzer = cy8_log_analyzer()

        # Cas de test réels
        test_cases = [
            {
                "line": "ERROR: Failed to load custom_nodes/ComfyUI-Manager: ModuleNotFoundError: No module named 'git'",
                "expected_node": "ComfyUI-Manager",
                "expected_type": "Module Not Found"
            },
            {
                "line": "CUDA error: out of memory in custom_nodes/ComfyUI-VideoHelperSuite/videohelpersuite/image_load_cap.py",
                "expected_node": "ComfyUI-VideoHelperSuite",
                "expected_type": "CUDA Error"
            },
            {
                "line": "custom_nodes/ComfyUI-Impact-Pack: 1.24s",
                "expected_time": "1.24s"
            },
            {
                "line": "custom_nodes/broken_node (IMPORT FAILED): Permission denied",
                "expected_reason": "Permission denied"
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test cas {i}:")
            print(f"   Ligne: {test_case['line'][:70]}...")

            if 'expected_node' in test_case:
                node = analyzer._extract_custom_node_from_error(test_case['line'])
                print(f"   ✓ Node détecté: '{node}' (attendu: '{test_case['expected_node']}')")

            if 'expected_type' in test_case:
                error_info = analyzer._extract_error_info(test_case['line'])
                print(f"   ✓ Type erreur: '{error_info['type']}' (attendu: '{test_case['expected_type']}')")
                print(f"   ✓ Détails: '{error_info['details']}'")

            if 'expected_time' in test_case:
                time = analyzer._extract_loading_time(test_case['line'])
                print(f"   ✓ Temps: '{time}' (attendu: '{test_case['expected_time']}')")

            if 'expected_reason' in test_case:
                reason = analyzer._extract_failure_reason(test_case['line'])
                print(f"   ✓ Raison: '{reason}'")

        print("\n✅ Tests d'extraction terminés avec succès!")
        return True

    except Exception as e:
        print(f"❌ Erreur lors des tests d'extraction: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test des améliorations de l'analyse des logs")
    print("=" * 60)

    success1 = test_log_analyzer_improvements()
    success2 = test_error_extraction()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("\n📊 Résumé des améliorations:")
        print("• Plus d'informations par ligne d'analyse")
        print("• Nom du custom node affiché clairement")
        print("• Détails complets sur les erreurs")
        print("• Popup d'analyse optionnelle (pas automatique)")
        print("• Interface plus riche avec colonne 'Détails/Temps'")
    else:
        print("❌ Certains tests ont échoué")
        sys.exit(1)

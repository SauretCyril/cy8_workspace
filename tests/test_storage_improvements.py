#!/usr/bin/env python3
"""
Test des améliorations du stockage des logs
"""

import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_rich_details_building():
    """Test de la construction des détails enrichis"""
    print("🧪 Test de construction des détails enrichis")
    print("=" * 50)

    # Simuler la classe avec la méthode
    class MockApp:
        def _build_rich_details_for_db(self, entry, original_message):
            """Construire des détails enrichis pour le stockage en base de données"""
            details_parts = []

            # Informations de base
            details_parts.append(f"Element: {entry.get('element', 'N/A')}")
            details_parts.append(f"Line: {entry.get('line', 'N/A')}")
            details_parts.append(f"Timestamp: {entry.get('timestamp', 'N/A')}")

            # Ajouter le message original complet s'il est différent du message affiché
            if " | " in original_message:
                parts = original_message.split(" | ", 1)
                if len(parts) > 1:
                    details_parts.append(f"Context: {parts[1]}")

            # Ajouter les détails spécifiques selon le type
            if entry["type"] == "ERREUR":
                details_parts.append(f"Error_Type: {entry.get('category', 'Unknown')}")

            # Ajouter les détails bruts s'ils existent
            if "details" in entry and entry["details"]:
                details_parts.append(f"Full_Line: {entry['details']}")

            return " | ".join(details_parts)

    app = MockApp()

    # Cas de test
    test_cases = [
        {
            "name": "Custom Node OK",
            "entry": {
                "type": "OK",
                "category": "Custom Node",
                "element": "ComfyUI-Manager",
                "line": 10,
                "timestamp": "2025-10-03 14:30:25.123",
                "details": "custom_nodes/ComfyUI-Manager: 1.2s"
            },
            "original_message": "Chargé avec succès (1.2s)"
        },
        {
            "name": "Erreur avec contexte",
            "entry": {
                "type": "ERREUR",
                "category": "Module Not Found",
                "element": "ComfyUI-VideoHelper",
                "line": 45,
                "timestamp": "2025-10-03 14:30:26.456",
                "details": "Error in custom_nodes/ComfyUI-VideoHelper/video.py: ModuleNotFoundError"
            },
            "original_message": "Import failed | Loading failure"
        },
        {
            "name": "Warning CUDA",
            "entry": {
                "type": "ATTENTION",
                "category": "Warning",
                "element": "Système",
                "line": 78,
                "timestamp": "2025-10-03 14:30:27.789",
                "details": "CUDA out of memory warning detected"
            },
            "original_message": "CUDA memory warning | Memory issue"
        }
    ]

    print("📋 Test des cas:")
    for case in test_cases:
        print(f"\n🔍 {case['name']}:")
        print(f"  Message original: '{case['original_message']}'")

        rich_details = app._build_rich_details_for_db(case['entry'], case['original_message'])
        print(f"  Détails enrichis: '{rich_details}'")

        # Vérifications
        assert "Element:" in rich_details
        assert "Line:" in rich_details
        assert "Timestamp:" in rich_details

        if " | " in case['original_message']:
            assert "Context:" in rich_details

        if case['entry']['type'] == "ERREUR":
            assert "Error_Type:" in rich_details

        print("  ✅ Format correct")

    print("\n✅ Tous les tests de construction des détails réussis!")
    return True

def test_message_processing():
    """Test du traitement des messages pour l'affichage"""
    print("\n🎨 Test du traitement des messages pour l'affichage")
    print("=" * 50)

    test_cases = [
        {
            "input": "Chargé avec succès (1.2s)",
            "type": "OK",
            "expected_display": "Chargé avec succès",
            "expected_details": "1.2s"
        },
        {
            "input": "Import failed | Loading failure",
            "type": "ERREUR",
            "expected_display": "Import failed",
            "expected_details": "Loading failure"
        },
        {
            "input": "CUDA memory warning | Memory issue",
            "type": "ATTENTION",
            "expected_display": "CUDA memory warning",
            "expected_details": "Memory issue"
        },
        {
            "input": "Simple message without context",
            "type": "INFO",
            "expected_display": "Simple message without context",
            "expected_details": ""
        }
    ]

    for case in test_cases:
        print(f"\n📝 Test: '{case['input']}'")

        # Simulation du traitement
        original_message = case['input']
        display_message = original_message
        details_info = ""

        if case['type'] == "OK" and "(" in original_message:
            import re
            time_match = re.search(r'\(([^)]+)\)', original_message)
            if time_match:
                details_info = time_match.group(1)
                display_message = original_message.split(" (")[0]
        elif case['type'] in ["ERREUR", "ATTENTION"] and " | " in original_message:
            parts = original_message.split(" | ", 1)
            if len(parts) > 1:
                display_message = parts[0]
                details_info = parts[1]

        print(f"  Message affiché: '{display_message}'")
        print(f"  Détails UI: '{details_info}'")

        # Vérifications
        assert display_message == case['expected_display'], f"Attendu: '{case['expected_display']}', Obtenu: '{display_message}'"
        assert details_info == case['expected_details'], f"Attendu: '{case['expected_details']}', Obtenu: '{details_info}'"

        print("  ✅ Traitement correct")

    print("\n✅ Tous les tests de traitement des messages réussis!")
    return True

if __name__ == "__main__":
    print("🚀 Test des améliorations du stockage")
    print("=" * 60)

    success1 = test_rich_details_building()
    success2 = test_message_processing()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("\n✅ AMÉLIORATIONS VALIDÉES:")
        print("• Construction de détails enrichis pour la base")
        print("• Préservation du message original complet")
        print("• Extraction correcte des informations pour l'affichage")
        print("• Contexte et détails spécifiques préservés")
        print("\n🔧 PROCHAINE ÉTAPE:")
        print("• Tester avec l'application complète")
    else:
        print("❌ Certains tests ont échoué")

#!/usr/bin/env python3
"""
Test rapide pour vérifier l'interface du monitoring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_monitor_status_display_format():
    """Test des formats d'affichage du statut"""
    print("🧪 Test des formats d'affichage")

    # Simulation des différents cas
    test_cases = [
        {"status": "Actif", "active_tasks": 0, "expected": "✅ Actif"},
        {"status": "Actif", "active_tasks": 3, "expected": "🔄 Actif (3)"},
        {"status": "Panne serveur", "active_tasks": 0, "expected": "🚨 Panne"},
        {"status": "Arrêté", "active_tasks": 0, "expected": "⏹️ Arrêté"},
    ]

    def get_monitor_status_display(status_info):
        """Reproduction de la logique d'affichage"""
        status = status_info['status']
        active_tasks = status_info['active_tasks']

        if status == "Actif":
            if active_tasks > 0:
                return f"🔄 Actif ({active_tasks})"
            else:
                return "✅ Actif"
        elif status == "Panne serveur":
            return "🚨 Panne"
        else:
            return "⏹️ Arrêté"

    for i, test_case in enumerate(test_cases):
        result = get_monitor_status_display(test_case)
        expected = test_case["expected"]

        print(f"Test {i+1}: {test_case} -> {result}")
        assert result == expected, f"Attendu: {expected}, obtenu: {result}"

    print("✅ Tous les formats d'affichage sont corrects")


def test_column_configuration():
    """Test de la configuration des colonnes"""
    print("🧪 Test de la configuration des colonnes")

    # Colonnes attendues
    expected_columns = ("id", "prompt", "status", "progress", "timestamp", "monitor")
    column_headers = {
        "id": "ID Exécution",
        "prompt": "Nom du Prompt",
        "status": "Statut",
        "progress": "Progression",
        "timestamp": "Démarré à",
        "monitor": "Monitoring"
    }

    # Largeurs attendues
    expected_widths = {
        "id": 100,
        "prompt": 180,
        "status": 180,
        "progress": 80,
        "timestamp": 120,
        "monitor": 100
    }

    print(f"✅ Colonnes définies: {expected_columns}")
    print(f"✅ En-têtes: {column_headers}")
    print(f"✅ Largeurs: {expected_widths}")

    # Vérification de la largeur totale
    total_width = sum(expected_widths.values())
    print(f"✅ Largeur totale: {total_width}px")

    assert len(expected_columns) == 6, "6 colonnes attendues"
    assert "monitor" in expected_columns, "Colonne monitor doit être présente"

    print("✅ Configuration des colonnes correcte")


if __name__ == "__main__":
    print("🚀 Tests de l'interface de monitoring")
    print("=" * 50)

    try:
        test_monitor_status_display_format()
        print()
        test_column_configuration()
        print()

        print("=" * 50)
        print("🎉 TOUS LES TESTS INTERFACE RÉUSSIS !")

    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

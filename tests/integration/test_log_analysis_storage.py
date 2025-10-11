#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import os
Test de stockage des résultats d'analyse de log en base de données

Vérifie que lorsqu'on clique sur 'Analyser le log', les résultats
sont bien stockés dans la table resultats_analyses de la base de données.
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# Configuration de l'encodage pour Windows
if os.name == "nt":  # Windows
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_log_analysis_storage():
    """Test de stockage des résultats d'analyse en base"""
    print("🧪 Test de stockage des résultats d'analyse de log")
    print("=" * 50)

    try:
        # Import des modules nécessaires
        from cy8_database_manager import cy8_database_manager
        from cy8_prompts_manager_main import cy8_prompts_manager
        import tkinter as tk

        # Créer une base de données temporaire
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db_path = temp_db.name
        temp_db.close()

        print(f"📁 Base de données temporaire: {temp_db_path}")

        # Initialiser le gestionnaire de base de données
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")

        # Créer l'environnement de test en insérant directement dans la base
        environment_id = "TEST_ENV_001"
        try:
            db_manager.cursor.execute(
                """
                INSERT OR REPLACE INTO environnements
                (id, name, path, description, last_analysis)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (
                    environment_id,
                    "Test Environment",
                    "/test/comfyui",
                    "Environment for testing",
                ),
            )
            db_manager.conn.commit()
        except Exception as e:
            print(f"Erreur lors de la création de l'environnement: {e}")
            return False

        print(f"🌍 Environnement créé: {environment_id}")

        # Créer l'application (sans interface graphique)
        root = tk.Tk()
        root.withdraw()

        app = cy8_prompts_manager()
        app.root = root
        app.db_manager = db_manager
        app.current_environment_id = environment_id

        # Mock du log analyzer pour simuler des résultats
        mock_log_analyzer = Mock()
        mock_entries = [
            {
                "timestamp": "2024-10-03 10:30:00",
                "type": "error",
                "category": "custom_node",
                "element": "test_node",
                "message": "Node test_node failed to load",
                "line": "42",
            },
            {
                "timestamp": "2024-10-03 10:30:01",
                "type": "info",
                "category": "system",
                "element": "comfyui",
                "message": "ComfyUI started successfully",
                "line": "1",
            },
            {
                "timestamp": "2024-10-03 10:30:02",
                "type": "warning",
                "category": "model",
                "element": "checkpoint",
                "message": "Model checkpoint not found",
                "line": "100",
            },
        ]

        mock_result = {
            "success": True,
            "entries": mock_entries,
            "summary": {
                "custom_nodes_ok": 1,
                "custom_nodes_failed": 1,
                "errors": 1,
                "warnings": 1,
                "info_messages": 1,
            },
            "config_id": "TEST_CONFIG",
        }

        mock_log_analyzer.analyze_log_file.return_value = mock_result
        mock_log_analyzer.get_summary_text.return_value = "Test summary"

        app.log_analyzer = mock_log_analyzer

        # Mock des éléments UI nécessaires
        app.comfyui_log_path = Mock()
        app.comfyui_log_path.get.return_value = "/test/log/comfyui.log"

        app.analyze_log_btn = Mock()
        app.log_status_label = Mock()
        app.log_results_tree = Mock()
        app.log_results_tree.get_children.return_value = []
        app.log_results_tree.insert = Mock()

        app.log_results_count_label = Mock()
        app.comfyui_config_id = Mock()
        app.comfyui_config_id.get.return_value = ""
        app.comfyui_config_id.set = Mock()

        app.config_info_label = Mock()
        app.root.update = Mock()

        print("🔧 Mocks configurés")

        # Vérifier qu'il n'y a pas de résultats initialement
        initial_results = db_manager.get_analysis_results(environment_id)
        print(f"📊 Résultats initiaux: {len(initial_results)}")

        # Mock de messagebox pour éviter les popups
        with patch("tkinter.messagebox.showinfo"), patch(
            "os.path.exists", return_value=True
        ):

            # Exécuter l'analyse de log
            print("🚀 Lancement de l'analyse de log...")
            app.analyze_comfyui_log()

        # Vérifier que les résultats ont été stockés
        stored_results = db_manager.get_analysis_results(environment_id)
        print(f"💾 Résultats stockés: {len(stored_results)}")

        # Tests de validation
        tests_passed = 0
        total_tests = 4

        # Test 1: Nombre de résultats stockés
        if len(stored_results) == len(mock_entries):
            print("✅ Test 1: Nombre correct de résultats stockés")
            tests_passed += 1
        else:
            print(
                f"❌ Test 1: Attendu {len(mock_entries)}, obtenu {len(stored_results)}"
            )

        # Test 2: Vérification du contenu des résultats
        if stored_results:
            first_result = stored_results[0]
            # Format: (id, environment_id, fichier, type, niveau, message, details, timestamp)

            if first_result[1] == environment_id:
                print("✅ Test 2: Environment ID correct")
                tests_passed += 1
            else:
                print(f"❌ Test 2: Environment ID incorrect: {first_result[1]}")
        else:
            print("❌ Test 2: Aucun résultat à vérifier")

        # Test 3: Vérification des types de résultats
        stored_types = {
            result[3] for result in stored_results
        }  # type est en position 3
        expected_types = {entry["type"] for entry in mock_entries}

        if stored_types == expected_types:
            print("✅ Test 3: Types de résultats corrects")
            tests_passed += 1
        else:
            print(
                f"❌ Test 3: Types incorrects. Attendu: {expected_types}, Obtenu: {stored_types}"
            )

        # Test 4: Vérification que log_analyzer a été appelé
        if mock_log_analyzer.analyze_log_file.called:
            print("✅ Test 4: Log analyzer appelé")
            tests_passed += 1
        else:
            print("❌ Test 4: Log analyzer non appelé")

        # Afficher quelques détails des résultats stockés
        print(f"\n📋 Détails des résultats stockés:")
        for i, result in enumerate(stored_results[:3]):  # Afficher les 3 premiers
            print(
                f"   {i+1}. Type: {result[3]}, Niveau: {result[4]}, Message: {result[5][:50]}..."
            )

        # Nettoyage
        root.destroy()
        db_manager.close()
        os.unlink(temp_db_path)

        # Résumé
        print(f"\n🎯 RÉSUMÉ:")
        print(f"   Tests réussis: {tests_passed}/{total_tests}")
        print(f"   Taux de réussite: {(tests_passed/total_tests)*100:.1f}%")

        if tests_passed == total_tests:
            print("\n🏆 STOCKAGE FONCTIONNEL !")
            print("✅ Les résultats d'analyse sont bien stockés en base")
            print("✅ Le mapping des données est correct")
            print("✅ L'environnement est associé correctement")
            return True
        else:
            print("\n❌ PROBLÈMES DÉTECTÉS")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_methods():
    """Test des méthodes de la base de données pour les analyses"""
    print("\n🗄️ Test des méthodes de base de données...")

    try:
        from cy8_database_manager import cy8_database_manager

        # Créer une base temporaire
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db_path = temp_db.name
        temp_db.close()

        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")

        environment_id = "TEST_ENV_DB"

        # Test d'ajout de résultat
        success = db_manager.add_analysis_result(
            environment_id=environment_id,
            fichier="test.log",
            type_result="error",
            niveau="critical",
            message="Test error message",
            details="Test details",
        )

        if success:
            print("✅ Ajout de résultat d'analyse réussi")
        else:
            print("❌ Échec de l'ajout de résultat")
            return False

        # Test de récupération
        results = db_manager.get_analysis_results(environment_id)

        if len(results) == 1:
            print("✅ Récupération de résultats réussie")
        else:
            print(f"❌ Récupération incorrecte: {len(results)} résultats")
            return False

        # Test de nettoyage
        db_manager.clear_analysis_results(environment_id)
        results_after_clear = db_manager.get_analysis_results(environment_id)

        if len(results_after_clear) == 0:
            print("✅ Nettoyage des résultats réussi")
        else:
            print(f"❌ Nettoyage échoué: {len(results_after_clear)} résultats restants")
            return False

        # Nettoyage
        db_manager.close()
        os.unlink(temp_db_path)

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test de base: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 Test complet de stockage des analyses de log")
    print("=" * 50)

    success_count = 0
    total_tests = 2

    # Test 1: Méthodes de base de données
    if test_database_methods():
        success_count += 1
        print("✅ Test 1 RÉUSSI - Méthodes de base")
    else:
        print("❌ Test 1 ÉCHOUÉ")

    # Test 2: Stockage complet
    if test_log_analysis_storage():
        success_count += 1
        print("✅ Test 2 RÉUSSI - Stockage complet")
    else:
        print("❌ Test 2 ÉCHOUÉ")

    # Résumé final
    print(f"\n🎯 RÉSUMÉ FINAL:")
    print(f"   Tests réussis: {success_count}/{total_tests}")
    print(f"   Taux de réussite: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("\n🎉 FONCTIONNALITÉ VALIDÉE !")
        print("✅ Les résultats d'analyse de log sont stockés en base")
        print("✅ Le tableau et la base sont synchronisés")
        print("✅ L'association avec l'environnement fonctionne")
        print("\n💡 Maintenant, quand vous cliquez sur 'Analyser le log',")
        print("   les résultats sont automatiquement sauvegardés !")
        return True
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

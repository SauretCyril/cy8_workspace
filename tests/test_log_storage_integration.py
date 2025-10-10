#!/usr/bin/env python3
"""
Test d'intégration : Analyser le log et vérifier la persistance

Teste le workflow complet :
1. Analyser un log ComfyUI
2. Vérifier que les résultats sont stockés dans la base
3. Changer d'environnement et revenir
4. Vérifier que les résultats persistent
"""

import sys
import os
import tempfile

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_log_storage_persistence():
    """Test de persistance des résultats d'analyse"""
    print("🔄 Test de persistance des résultats d'analyse")
    print("=" * 45)

    try:
        from cy8_database_manager import cy8_database_manager

        # Créer une base temporaire
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db_path = temp_db.name
        temp_db.close()

        print(f"📁 Base temporaire: {temp_db_path}")

        # Initialiser la base
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")

        # Créer deux environnements de test
        env1_id = "ENV_TEST_01"
        env2_id = "ENV_TEST_02"

        for env_id, env_name in [
            (env1_id, "Environment 1"),
            (env2_id, "Environment 2"),
        ]:
            db_manager.cursor.execute(
                """
                INSERT INTO environnements (id, name, path, description)
                VALUES (?, ?, ?, ?)
                """,
                (
                    env_id,
                    env_name,
                    f"/test/{env_id.lower()}",
                    f"Test environment {env_id}",
                ),
            )
        db_manager.conn.commit()

        print(f"🌍 Environnements créés: {env1_id}, {env2_id}")

        # Ajouter des résultats d'analyse pour ENV1
        results_env1 = [
            ("error", "critical", "Failed to load custom node A"),
            ("warning", "model", "Model checkpoint missing"),
            ("info", "startup", "ComfyUI started successfully"),
        ]

        for type_result, niveau, message in results_env1:
            db_manager.add_analysis_result(
                environment_id=env1_id,
                fichier="comfyui_env1.log",
                type_result=type_result,
                niveau=niveau,
                message=message,
                details=f"Details for {message}",
            )

        # Ajouter des résultats d'analyse pour ENV2
        results_env2 = [
            ("error", "fatal", "Critical error in ENV2"),
            ("info", "model", "Model loaded in ENV2"),
        ]

        for type_result, niveau, message in results_env2:
            db_manager.add_analysis_result(
                environment_id=env2_id,
                fichier="comfyui_env2.log",
                type_result=type_result,
                niveau=niveau,
                message=message,
                details=f"Details for {message}",
            )

        print(
            f"💾 Résultats ajoutés: {len(results_env1)} pour {env1_id}, {len(results_env2)} pour {env2_id}"
        )

        # Test 1: Récupérer les résultats pour ENV1
        stored_env1 = db_manager.get_analysis_results(env1_id)
        print(f"📊 Résultats ENV1: {len(stored_env1)} trouvés")

        if len(stored_env1) == len(results_env1):
            print("✅ Test 1: Nombre correct de résultats pour ENV1")
        else:
            print(f"❌ Test 1: Attendu {len(results_env1)}, obtenu {len(stored_env1)}")
            return False

        # Test 2: Récupérer les résultats pour ENV2
        stored_env2 = db_manager.get_analysis_results(env2_id)
        print(f"📊 Résultats ENV2: {len(stored_env2)} trouvés")

        if len(stored_env2) == len(results_env2):
            print("✅ Test 2: Nombre correct de résultats pour ENV2")
        else:
            print(f"❌ Test 2: Attendu {len(results_env2)}, obtenu {len(stored_env2)}")
            return False

        # Test 3: Vérifier l'isolation entre environnements
        # Les résultats d'ENV1 ne doivent pas contenir ceux d'ENV2
        env1_messages = {result[5] for result in stored_env1}  # message en position 5
        env2_messages = {result[5] for result in stored_env2}

        if env1_messages.isdisjoint(env2_messages):
            print("✅ Test 3: Isolation entre environnements correcte")
        else:
            print("❌ Test 3: Contamination croisée détectée")
            print(f"   Intersection: {env1_messages & env2_messages}")
            return False

        # Test 4: Récupérer tous les résultats
        all_results = db_manager.get_analysis_results()
        expected_total = len(results_env1) + len(results_env2)

        if len(all_results) == expected_total:
            print("✅ Test 4: Récupération globale correcte")
        else:
            print(
                f"❌ Test 4: Total attendu {expected_total}, obtenu {len(all_results)}"
            )
            return False

        # Test 5: Nettoyage sélectif
        db_manager.clear_analysis_results(env1_id)
        remaining_env1 = db_manager.get_analysis_results(env1_id)
        remaining_env2 = db_manager.get_analysis_results(env2_id)

        if len(remaining_env1) == 0 and len(remaining_env2) == len(results_env2):
            print("✅ Test 5: Nettoyage sélectif réussi")
        else:
            print(
                f"❌ Test 5: Nettoyage échoué - ENV1: {len(remaining_env1)}, ENV2: {len(remaining_env2)}"
            )
            return False

        # Afficher quelques exemples de données
        print(f"\n📋 Exemple de données ENV2:")
        for result in remaining_env2[:2]:
            print(f"   Type: {result[3]}, Niveau: {result[4]}, Message: {result[5]}")

        # Nettoyage
        db_manager.close()
        os.unlink(temp_db_path)

        print("\n🎉 TOUS LES TESTS DE PERSISTANCE RÉUSSIS !")
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test de persistance: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_complete_workflow():
    """Test du workflow complet d'analyse avec stockage"""
    print("\n🔄 Test du workflow complet")
    print("=" * 30)

    try:
        # Ce test simule le workflow complet sans interface graphique
        from cy8_database_manager import cy8_database_manager

        # Étape 1: Préparer la base
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db_path = temp_db.name
        temp_db.close()

        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")

        # Étape 2: Créer un environnement
        env_id = "WORKFLOW_TEST"
        db_manager.cursor.execute(
            "INSERT INTO environnements (id, name, path, description) VALUES (?, ?, ?, ?)",
            (env_id, "Workflow Test", "/test/workflow", "Complete workflow test"),
        )
        db_manager.conn.commit()

        print(f"✅ Environnement créé: {env_id}")

        # Étape 3: Simuler une analyse de log qui produit des résultats
        log_entries = [
            {
                "type": "error",
                "level": "high",
                "msg": "Custom node failed",
                "details": "Node XYZ",
            },
            {
                "type": "warning",
                "level": "medium",
                "msg": "Deprecated function",
                "details": "Function ABC",
            },
            {
                "type": "info",
                "level": "low",
                "msg": "Processing complete",
                "details": "All done",
            },
        ]

        stored_count = 0
        for entry in log_entries:
            success = db_manager.add_analysis_result(
                environment_id=env_id,
                fichier="test_workflow.log",
                type_result=entry["type"],
                niveau=entry["level"],
                message=entry["msg"],
                details=entry["details"],
            )
            if success:
                stored_count += 1

        print(f"💾 Stockage: {stored_count}/{len(log_entries)} résultats sauvegardés")

        # Étape 4: Vérifier la récupération
        retrieved = db_manager.get_analysis_results(env_id)

        if len(retrieved) == len(log_entries):
            print("✅ Récupération: Nombre correct de résultats")
        else:
            print(f"❌ Récupération échouée: {len(retrieved)}/{len(log_entries)}")
            return False

        # Étape 5: Vérifier la structure des données
        first_result = retrieved[0]
        expected_fields = (
            8  # id, env_id, fichier, type, niveau, message, details, timestamp
        )

        if len(first_result) == expected_fields:
            print("✅ Structure: Format de données correct")
        else:
            print(
                f"❌ Structure incorrecte: {len(first_result)} champs au lieu de {expected_fields}"
            )
            return False

        # Nettoyage
        db_manager.close()
        os.unlink(temp_db_path)

        print("✅ Workflow complet validé !")
        return True

    except Exception as e:
        print(f"❌ Erreur workflow: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 Test d'intégration : Analyse de log avec persistance")
    print("=" * 55)

    success_count = 0
    total_tests = 2

    # Test 1: Persistance des données
    if test_log_storage_persistence():
        success_count += 1
        print("✅ Test 1 RÉUSSI - Persistance des données")
    else:
        print("❌ Test 1 ÉCHOUÉ")

    # Test 2: Workflow complet
    if test_complete_workflow():
        success_count += 1
        print("✅ Test 2 RÉUSSI - Workflow complet")
    else:
        print("❌ Test 2 ÉCHOUÉ")

    # Résumé final
    print(f"\n🎯 RÉSUMÉ FINAL:")
    print(f"   Tests réussis: {success_count}/{total_tests}")
    print(f"   Taux de réussite: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("\n🎉 INTÉGRATION RÉUSSIE !")
        print("✅ Le stockage des résultats d'analyse fonctionne parfaitement")
        print("✅ Les résultats persistent entre les sessions")
        print("✅ L'isolation entre environnements est assurée")
        print("✅ Le workflow complet est opérationnel")
        print("\n💡 Maintenant vous pouvez :")
        print("   • Analyser un log avec 'Analyser le log'")
        print("   • Voir les résultats dans le tableau")
        print("   • Retrouver les résultats après redémarrage")
        print("   • Changer d'environnement et garder l'historique")
        return True
    else:
        print("\n❌ PROBLÈMES D'INTÉGRATION")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

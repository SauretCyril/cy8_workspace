"""Test du tableau des environnements dans l'onglet Log"""

import os
import sys
import tempfile

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_environments_integration():
    """Test d'intégration du tableau des environnements"""
    print("🧪 Test d'intégration du tableau des environnements")
    print("=" * 60)

    try:
        # Import des modules
        from cy8_database_manager import cy8_database_manager

        # Créer une base temporaire
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            temp_db_path = tmp_file.name

        # Initialiser la base
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="init")

        print("✅ Base de données initialisée")

        # Vérifier les environnements par défaut
        environments = db_manager.get_all_environments()
        print(f"📋 Environnements trouvés : {len(environments)}")

        for env in environments:
            env_id, name, path, description, last_analysis, created_at, updated_at = env
            print(f"  🌍 {env_id}: {name} → {path}")

        # Test de l'analyse d'un environnement
        test_env = "G11_01"
        print(f"\n🔍 Test d'analyse pour {test_env}")

        # Mise à jour de la date d'analyse
        success = db_manager.update_environment_analysis(test_env)
        print(f"  ✅ Mise à jour date d'analyse: {success}")

        # Ajout de résultats d'analyse
        test_results = [
            ("comfyui.log", "INFO", "Normal", "Démarrage de ComfyUI", "Version 1.0"),
            (
                "comfyui.log",
                "WARNING",
                "Attention",
                "Modèle introuvable",
                "model.safetensors manquant",
            ),
            (
                "comfyui.log",
                "ERROR",
                "Erreur",
                "Module manquant",
                "custom_nodes non installé",
            ),
        ]

        for fichier, type_result, niveau, message, details in test_results:
            db_manager.add_analysis_result(
                test_env, fichier, type_result, niveau, message, details
            )

        print(f"  ✅ {len(test_results)} résultats d'analyse ajoutés")

        # Récupération des résultats
        results = db_manager.get_analysis_results(test_env)
        print(f"  📊 Résultats récupérés : {len(results)}")

        for result in results:
            (
                result_id,
                env_id,
                fichier,
                type_result,
                niveau,
                message,
                details,
                timestamp,
            ) = result
            print(f"    - {type_result}: {message}")

        # Test avec un autre environnement
        test_env2 = "G11_02"
        db_manager.add_analysis_result(
            test_env2, "debug.log", "INFO", "Normal", "Test environnement 2", ""
        )

        results_env2 = db_manager.get_analysis_results(test_env2)
        print(f"\n🌍 Environnement {test_env2} : {len(results_env2)} résultats")

        # Test de suppression des résultats
        db_manager.clear_analysis_results(test_env)
        results_after_clear = db_manager.get_analysis_results(test_env)
        print(
            f"  🗑️ Après suppression {test_env} : {len(results_after_clear)} résultats"
        )

        db_manager.close()

        # Nettoyer
        os.unlink(temp_db_path)

        print("\n🎉 Test d'intégration réussi !")

        # Instructions pour tester l'interface
        print("\n📋 Pour tester l'interface complète :")
        print("1. Lancez l'application : python src/cy8_prompts_manager_main.py")
        print("2. Allez dans l'onglet '📊 Log'")
        print("3. Vérifiez la section '🌍 Environnements ComfyUI'")
        print("4. Cliquez sur un environnement pour voir ses résultats")
        print("5. Utilisez 'Analyser environnement sélectionné' pour tester")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_environments_integration()

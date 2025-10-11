"""Test des nouvelles tables d'environnement et de résultats d'analyses"""

import os
import sys
import tempfile
import sqlite3

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cy8_database_manager import cy8_database_manager


def test_environment_tables():
    """Test de création et utilisation des tables d'environnement"""
    # Créer une base temporaire
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        temp_db_path = tmp_file.name

    try:
        # Initialiser la base avec les nouvelles tables
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="init")

        print("✅ Base de données initialisée avec succès")

        # Vérifier que les tables ont été créées
        db_manager.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db_manager.cursor.fetchall()]

        expected_tables = [
            "prompts",
            "prompt_image",
            "environnements",
            "resultats_analyses",
        ]
        for table in expected_tables:
            if table in tables:
                print(f"✅ Table '{table}' créée")
            else:
                print(f"❌ Table '{table}' manquante")

        # Tester les environnements par défaut
        environments = db_manager.get_all_environments()
        print(f"\n📋 Environnements créés : {len(environments)}")
        for env in environments:
            env_id, name, path, description, last_analysis, created_at, updated_at = env
            print(f"  - {env_id}: {name} ({path})")

        # Tester l'ajout d'un résultat d'analyse
        test_env_id = "G11_01"
        db_manager.add_analysis_result(
            environment_id=test_env_id,
            fichier="test.log",
            type_result="INFO",
            niveau="Normal",
            message="Test d'analyse",
            details="Détails du test",
        )

        # Récupérer les résultats d'analyse
        results = db_manager.get_analysis_results(test_env_id)
        print(f"\n📊 Résultats d'analyse pour {test_env_id} : {len(results)}")
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
            print(f"  - {type_result}: {message} ({fichier})")

        # Tester la mise à jour de l'environnement
        success = db_manager.update_environment_analysis(test_env_id)
        print(
            f"\n🔄 Mise à jour environnement {test_env_id}: {'✅' if success else '❌'}"
        )

        # Vérifier la structure de la table environnements
        db_manager.cursor.execute("PRAGMA table_info(environnements)")
        columns_info = db_manager.cursor.fetchall()
        print(f"\n🏗️ Structure table 'environnements':")
        for col in columns_info:
            print(f"  - {col[1]} ({col[2]})")

        # Vérifier la structure de la table resultats_analyses
        db_manager.cursor.execute("PRAGMA table_info(resultats_analyses)")
        columns_info = db_manager.cursor.fetchall()
        print(f"\n🏗️ Structure table 'resultats_analyses':")
        for col in columns_info:
            print(f"  - {col[1]} ({col[2]})")

        db_manager.close()
        print("\n🎉 Test des tables d'environnement réussi !")

    except Exception as e:
        print(f"\n❌ Erreur lors du test : {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_dev_mode():
    """Test du mode dev avec les nouvelles tables"""
    # Créer une base temporaire
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        temp_db_path = tmp_file.name

    try:
        # Initialiser en mode dev
        db_manager = cy8_database_manager(temp_db_path)
        db_manager.init_database(mode="dev")

        print("✅ Mode dev initialisé avec succès")

        # Vérifier les tables
        db_manager.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db_manager.cursor.fetchall()]
        print(f"📋 Tables créées en mode dev : {tables}")

        # Vérifier les environnements
        environments = db_manager.get_all_environments()
        print(f"🌍 Environnements en mode dev : {len(environments)}")

        db_manager.close()
        print("🎉 Test mode dev réussi !")

    except Exception as e:
        print(f"❌ Erreur lors du test mode dev : {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


if __name__ == "__main__":
    print("🧪 Test des nouvelles tables d'environnement")
    print("=" * 50)

    test_environment_tables()

    print("\n" + "=" * 50)
    print("🧪 Test du mode dev")
    print("=" * 50)

    test_dev_mode()

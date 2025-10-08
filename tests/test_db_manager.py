#!/usr/bin/env python3
"""
Test simple du database_manager
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager

def test_db_manager():
    """Test du database_manager"""
    print("🧪 === TEST DATABASE MANAGER ===")

    # Créer le manager
    db_manager = cy8_database_manager("data/prompts.db")
    print(f"✅ Database manager créé")
    print(f"   - db_path: {db_manager.db_path}")
    print(f"   - cursor: {db_manager.cursor}")

    # Initialiser
    db_manager.init_database("dev")
    print(f"✅ Database initialisée")
    print(f"   - cursor après init: {db_manager.cursor}")

    # Test de la méthode problématique
    try:
        print("   🔍 Test de get_environment_analyses_directory...")
        result = db_manager.get_environment_analyses_directory("test_env")
        print(f"   ✅ Répertoire analyses récupéré: {result}")
        print(f"   📍 Type du résultat: {type(result)}")
    except Exception as e:
        print(f"   ❌ Erreur get_environment_analyses_directory: {e}")
        import traceback
        traceback.print_exc()

        # Test de la requête directe
        try:
            print("   🔍 Test requête SQL directe...")
            db_manager.cursor.execute("SELECT id, path FROM environnements WHERE id = ?", ("test_env",))
            env_result = db_manager.cursor.fetchone()
            print(f"   📊 Environnement 'test_env' trouvé: {env_result}")

            # Lister tous les environnements
            db_manager.cursor.execute("SELECT id, name, path FROM environnements")
            all_envs = db_manager.cursor.fetchall()
            print(f"   📊 Tous les environnements: {all_envs}")
        except Exception as e2:
            print(f"   ❌ Erreur requête environnements: {e2}")

if __name__ == "__main__":
    test_db_manager()

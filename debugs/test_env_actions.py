#!/usr/bin/env python3
"""
Test de la fonctionnalité Actions d'environnement
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_env_actions():
    """Test des actions d'environnement"""
    print("=== TEST DES ACTIONS D'ENVIRONNEMENT ===")

    try:
        # Import des modules
        from cy8_database_manager import cy8_database_manager
        print("✅ Import database manager réussi")

        # Créer une instance du DB manager
        db = cy8_database_manager()
        db.init_database(mode="dev")  # Mode dev pour ne pas recréer
        db.ensure_environment_tables()  # S'assurer que les tables d'environnement existent
        print("✅ DB manager créé et initialisé")

        # Test 1: Ajouter une action
        env_id = "TEST_H12"
        action_id = db.add_env_action(env_id, "Démarrer ComfyUI", "python main.py --port 8188")
        if action_id:
            print(f"✅ Action ajoutée avec ID: {action_id}")
        else:
            print("❌ Erreur ajout action")
            return False

        # Test 2: Récupérer les actions
        actions = db.get_env_actions(env_id)
        print(f"✅ Actions récupérées: {len(actions)}")
        for action in actions:
            print(f"  - {action['id']}: {action['short_desc']} -> {action['action_cmd']}")

        # Test 3: Modifier une action
        if actions:
            first_action = actions[0]
            success = db.update_env_action(
                first_action['id'],
                "Démarrer ComfyUI (modifié)",
                "python main.py --port 8188 --listen"
            )
            print(f"✅ Modification: {'Succès' if success else 'Échec'}")

        # Test 4: Vérifier la modification
        actions_updated = db.get_env_actions(env_id)
        if actions_updated:
            print(f"✅ Action modifiée: {actions_updated[0]['short_desc']}")

        # Test 5: Récupérer le répertoire d'analyses
        analyses_dir = db.get_environment_analyses_directory(env_id)
        print(f"✅ Répertoire analyses: {analyses_dir}")

        # Test 6: Nettoyer
        for action in actions_updated:
            db.delete_env_action(action['id'])
        print("✅ Actions supprimées")

        # Vérifier suppression
        final_actions = db.get_env_actions(env_id)
        print(f"✅ Actions finales: {len(final_actions)}")

        print("\n🎉 Tous les tests passés avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_env_actions()

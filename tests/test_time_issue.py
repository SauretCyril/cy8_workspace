#!/usr/bin/env python3
"""
Test simple pour isoler le problème avec time
"""

import sys
import os
import time

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cy8_database_manager import cy8_database_manager


def test_basic_database_operations():
    """Test de base pour les opérations de base de données"""
    print("=== Test de base pour les opérations de base de données ===")

    # Créer une base de données temporaire
    db_path = "test_temp.db"

    try:
        # Initialiser la base de données
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database("init")

        print("✓ Base de données initialisée")

        # Créer un prompt de test
        prompt_id = db_manager.create_prompt(
            name="test_prompt_simple",
            prompt_values='{"1": {"id": "6", "type": "prompt", "value": "test"}}',
            workflow='{"6": {"inputs": {"text": "test"}, "class_type": "CLIPTextEncode"}}',
            url="",
            model="test.ckpt",
            status="test",
            comment="Test prompt",
        )

        print(f"✓ Prompt créé avec ID: {prompt_id}")

        # Test avec time
        print(f"✓ time.time() = {time.time()}")

        # Test ajout d'image
        test_image_path = "c:/temp/nonexistent_image.png"
        success = db_manager.add_prompt_image(prompt_id, test_image_path)
        print(f"✓ Ajout d'image: {success}")

        # Test récupération d'images
        images = db_manager.get_prompt_images(prompt_id)
        print(f"✓ Images récupérées: {len(images)}")

        for image_id, image_path, environment_id, created_at in images:
            print(f"  - Image: ID={image_id}, Path={image_path}, Env={environment_id}, Date={created_at}")
            print(f"  - test time.time() après boucle: {time.time()}")

        print("✓ Test terminé avec succès")

        # Nettoyer
        db_manager.close()

        return True

    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    success = test_basic_database_operations()
    print(f"\nRésultat: {'SUCCÈS' if success else 'ÉCHEC'}")
    sys.exit(0 if success else 1)

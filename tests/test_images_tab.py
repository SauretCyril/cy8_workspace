#!/usr/bin/env python3
"""
Test de l'onglet Images et de la gestion des images générées
Test pour cy8_prompts_manager - Version cy8
"""

import os
import sys
import tempfile
import shutil
from PIL import Image

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_database_manager import cy8_database_manager


def create_test_image(path, size=(100, 100), color=(255, 0, 0)):
    """Créer une image de test"""
    img = Image.new("RGB", size, color)
    img.save(path)
    return path


def test_prompt_image_database():
    """Test des opérations de base de données pour les images"""
    print("=== Test des opérations de base de données pour les images ===")

    # Créer une base de données temporaire
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        # Initialiser la base de données
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database("init")

        # Créer un prompt de test
        prompt_id = db_manager.create_prompt(
            name="test_prompt_images",
            prompt_values='{"1": {"id": "6", "type": "prompt", "value": "test image"}}',
            workflow='{"6": {"inputs": {"text": "test"}, "class_type": "CLIPTextEncode"}}',
            url="",
            model="test_model.ckpt",
            status="test",
            comment="Test prompt pour images",
        )

        print(f"✓ Prompt créé avec ID: {prompt_id}")

        # Créer des images de test temporaires
        temp_dir = tempfile.mkdtemp()
        test_images = []

        for i in range(3):
            img_path = os.path.join(temp_dir, f"test_image_{i}.png")
            create_test_image(img_path, color=(255, i * 50, i * 100))
            test_images.append(img_path)

        print(f"✓ {len(test_images)} images de test créées")

        # Test ajout d'images
        for img_path in test_images:
            success = db_manager.add_prompt_image(prompt_id, img_path)
            assert success, f"Échec ajout image: {img_path}"

        print(f"✓ {len(test_images)} images ajoutées à la base")

        # Test récupération des images
        retrieved_images = db_manager.get_prompt_images(prompt_id)
        assert len(retrieved_images) == len(
            test_images
        ), f"Nombre d'images incorrect: {len(retrieved_images)} vs {len(test_images)}"

        print(f"✓ {len(retrieved_images)} images récupérées de la base")

        # Vérifier les données récupérées
        for i, (image_id, image_path, created_at) in enumerate(retrieved_images):
            assert os.path.basename(image_path) in [
                os.path.basename(p) for p in test_images
            ], f"Image inattendue: {image_path}"
            assert created_at is not None, "Date de création manquante"
            print(
                f"✓ Image {i+1}: ID={image_id}, Path={os.path.basename(image_path)}, Date={created_at}"
            )

        # Test suppression d'une image
        first_image_id = retrieved_images[0][0]
        success = db_manager.delete_prompt_image(first_image_id)
        assert success, "Échec suppression image"

        remaining_images = db_manager.get_prompt_images(prompt_id)
        assert (
            len(remaining_images) == len(test_images) - 1
        ), f"Nombre d'images après suppression incorrect: {len(remaining_images)}"

        print(
            f"✓ Suppression d'image réussie, {len(remaining_images)} images restantes"
        )

        # Test suppression de toutes les images du prompt
        success = db_manager.delete_prompt_images(prompt_id)
        assert success, "Échec suppression de toutes les images"

        final_images = db_manager.get_prompt_images(prompt_id)
        assert (
            len(final_images) == 0
        ), f"Images restantes après suppression complète: {len(final_images)}"

        print("✓ Suppression de toutes les images réussie")

        # Nettoyer
        db_manager.close()
        shutil.rmtree(temp_dir)

        print("✓ Test des opérations de base de données terminé avec succès")
        return True

    except Exception as e:
        print(f"✗ Erreur dans test_prompt_image_database: {e}")
        return False

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_image_format_handling():
    """Test de gestion de différents formats d'images"""
    print("\n=== Test de gestion des formats d'images ===")

    temp_dir = tempfile.mkdtemp()

    try:
        # Créer des images dans différents formats
        formats = [
            ("test.png", "PNG"),
            ("test.jpg", "JPEG"),
            ("test.bmp", "BMP"),
        ]

        created_images = []

        for filename, format_name in formats:
            img_path = os.path.join(temp_dir, filename)
            img = Image.new("RGB", (50, 50), (255, 128, 0))
            img.save(img_path, format_name)
            created_images.append(img_path)

            # Vérifier que l'image peut être ouverte
            test_img = Image.open(img_path)
            assert test_img.size == (50, 50), f"Taille incorrecte pour {filename}"
            test_img.close()  # Fermer l'image pour libérer le fichier
            print(f"✓ Image {filename} créée et validée")

        print(f"✓ {len(created_images)} images de différents formats créées")

        # Nettoyer
        shutil.rmtree(temp_dir)

        print("✓ Test des formats d'images terminé avec succès")
        return True

    except Exception as e:
        print(f"✗ Erreur dans test_image_format_handling: {e}")
        return False


def test_image_path_validation():
    """Test de validation des chemins d'images"""
    print("\n=== Test de validation des chemins d'images ===")

    # Créer une base de données temporaire
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
        db_path = tmp_db.name

    try:
        db_manager = cy8_database_manager(db_path)
        db_manager.init_database("init")

        # Créer un prompt de test
        prompt_id = db_manager.create_prompt(
            name="test_path_validation",
            prompt_values="{}",
            workflow="{}",
            url="",
            model="test.ckpt",
            status="test",
            comment="Test validation chemins",
        )

        # Test avec un chemin valide
        temp_dir = tempfile.mkdtemp()
        valid_path = os.path.join(temp_dir, "valid_image.png")
        create_test_image(valid_path)

        success = db_manager.add_prompt_image(prompt_id, valid_path)
        assert success, "Échec ajout image avec chemin valide"
        print("✓ Ajout d'image avec chemin valide réussi")

        # Test avec un chemin invalide (fichier inexistant)
        invalid_path = os.path.join(temp_dir, "nonexistent_image.png")
        success = db_manager.add_prompt_image(prompt_id, invalid_path)
        # L'ajout devrait réussir même si le fichier n'existe pas (on stocke juste le chemin)
        print(f"✓ Ajout d'image avec chemin inexistant: {success}")

        # Vérifier les images récupérées
        images = db_manager.get_prompt_images(prompt_id)
        valid_images = [img for img in images if os.path.exists(img[1])]
        print(f"✓ Images existantes: {len(valid_images)} sur {len(images)}")

        # Nettoyer
        db_manager.close()
        shutil.rmtree(temp_dir)

        print("✓ Test de validation des chemins terminé avec succès")
        return True

    except Exception as e:
        print(f"✗ Erreur dans test_image_path_validation: {e}")
        return False

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Fonction principale de test"""
    print("Tests de l'onglet Images - cy8_prompts_manager")
    print("=" * 50)

    tests = [
        test_prompt_image_database,
        test_image_format_handling,
        test_image_path_validation,
    ]

    results = []

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Erreur dans {test.__name__}: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("RÉSUMÉ DES TESTS:")

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test.__name__}")

    print(f"\nRésultat: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests sont passés!")
        return True
    else:
        print("❌ Certains tests ont échoué")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

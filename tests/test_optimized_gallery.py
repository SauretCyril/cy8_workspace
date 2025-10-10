#!/usr/bin/env python3
"""
Test de la galerie optimisée avec index et gestion de suppression
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import tempfile
from PIL import Image
import time
import sqlite3

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def create_test_images(temp_dir, count=5):
    """Créer des images de test"""
    image_paths = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

    for i in range(count):
        # Créer une image colorée simple
        img = Image.new("RGB", (300, 300), color=colors[i % len(colors)])
        image_path = os.path.join(temp_dir, f"test_image_{i+1}.png")
        img.save(image_path)
        image_paths.append(image_path)

    return image_paths


def test_image_index_manager():
    """Tester le gestionnaire d'index d'images"""
    print("🧪 Test du gestionnaire d'index...")

    try:
        from cy8_image_index_manager import ImageIndexManager

        # Créer un répertoire temporaire avec des images
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Répertoire de test: {temp_dir}")

            # Créer des images de test
            image_paths = create_test_images(temp_dir, 5)
            print(f"✅ {len(image_paths)} images créées")

            # Créer un index temporaire
            index_db = os.path.join(temp_dir, "test_index.db")
            index_manager = ImageIndexManager(index_db)

            # Tester le scan
            print("🔄 Test du scan...")
            stats = index_manager.scan_directory(temp_dir)
            assert (
                stats["total_files"] == 5
            ), f"Attendu 5 fichiers, trouvé {stats['total_files']}"
            assert (
                stats["new_files"] == 5
            ), f"Attendu 5 nouveaux, trouvé {stats['new_files']}"
            print("✅ Scan réussi")

            # Tester la récupération des images
            print("📋 Test de récupération...")
            images = index_manager.get_images(temp_dir)
            assert len(images) == 5, f"Attendu 5 images, trouvé {len(images)}"
            print("✅ Récupération réussie")

            # Tester les miniatures
            print("🖼️ Test des miniatures...")
            for image_data in images:
                thumbnail = index_manager.get_thumbnail(image_data["file_path"])
                assert (
                    thumbnail is not None
                ), f"Miniature manquante pour {image_data['file_name']}"
            print("✅ Miniatures générées")

            # Tester la suppression soft
            print("🗑️ Test de suppression soft...")
            test_image = images[0]["file_path"]
            index_manager.mark_deleted(test_image)

            # Vérifier que l'image est marquée comme supprimée
            updated_images = index_manager.get_images(temp_dir, include_deleted=True)
            deleted_image = next(
                img for img in updated_images if img["file_path"] == test_image
            )
            assert deleted_image["is_deleted"], "Image pas marquée comme supprimée"
            print("✅ Suppression soft réussie")

            # Tester la restauration
            print("♻️ Test de restauration...")
            index_manager.restore_deleted(test_image)
            restored_images = index_manager.get_images(temp_dir)
            assert len(restored_images) == 5, "Image pas restaurée"
            print("✅ Restauration réussie")

            # Tester les statistiques
            print("📊 Test des statistiques...")
            stats = index_manager.get_stats()
            assert stats["total_images"] == 5, f"Stats incorrectes: {stats}"
            print("✅ Statistiques correctes")

            index_manager.close()
            print("✅ Index fermé")

            return True

    except Exception as e:
        print(f"❌ Erreur lors du test de l'index: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_fast_image_processor():
    """Tester le processeur d'images rapide"""
    print("🧪 Test du processeur d'images...")

    try:
        from cy8_fast_image_processor import get_image_processor

        # Créer une image de test
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image = os.path.join(temp_dir, "test.png")
            img = Image.new("RGB", (500, 500), (128, 128, 128))
            img.save(test_image)

            processor = get_image_processor()
            print(f"🔧 Backend: {processor.get_performance_info()['backend']}")

            # Tester la création de miniature
            thumbnail_data = processor.create_thumbnail(test_image, 150, 150)
            assert thumbnail_data is not None, "Miniature non générée"
            assert len(thumbnail_data) > 0, "Données de miniature vides"
            print("✅ Miniature générée")

            # Tester les dimensions
            dimensions = processor.get_dimensions(test_image)
            assert dimensions == (500, 500), f"Dimensions incorrectes: {dimensions}"
            print("✅ Dimensions correctes")

            # Tester le hash
            hash_value = processor.calculate_hash(test_image)
            assert len(hash_value) > 0, "Hash non généré"
            print("✅ Hash calculé")

            return True

    except Exception as e:
        print(f"❌ Erreur lors du test du processeur: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_gallery_integration():
    """Tester l'intégration avec la galerie principale"""
    print("🧪 Test de l'intégration galerie...")

    try:
        # Créer un répertoire temporaire avec des images
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Répertoire de test: {temp_dir}")

            # Créer des images de test
            image_paths = create_test_images(temp_dir, 3)
            print(f"✅ {len(image_paths)} images créées")

            # Configurer la variable d'environnement
            os.environ["IMAGES_COLLECTE"] = temp_dir

            # Importer et créer l'application
            from cy8_prompts_manager_main import cy8_prompts_manager

            root = tk.Tk()
            root.withdraw()  # Cacher la fenêtre principale

            app = cy8_prompts_manager(root)

            # Vérifier que l'index est initialisé
            assert hasattr(app, "image_index"), "Index d'images manquant"
            assert hasattr(app, "fast_processor"), "Processeur rapide manquant"
            print("✅ Gestionnaires initialisés")

            # Vérifier les nouvelles méthodes
            assert hasattr(app, "refresh_gallery_with_scan"), "Méthode scan manquante"
            assert hasattr(
                app, "force_refresh_gallery"
            ), "Méthode force refresh manquante"
            assert hasattr(
                app, "mark_gallery_image_deleted"
            ), "Méthode suppression soft manquante"
            assert hasattr(
                app, "restore_gallery_image"
            ), "Méthode restauration manquante"
            assert hasattr(app, "show_gallery_stats"), "Méthode statistiques manquante"
            print("✅ Nouvelles méthodes présentes")

            # Tester un scan rapide
            stats = app.image_index.scan_directory(temp_dir)
            assert stats["total_files"] == 3, "Scan incorrect"
            print("✅ Scan fonctionnel")

            # Tester la création de grille depuis l'index
            indexed_images = app.image_index.get_images(temp_dir)
            assert len(indexed_images) == 3, "Index incorrect"
            print("✅ Index fonctionnel")

            root.destroy()
            print("✅ Test terminé avec succès")

            return True

    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Fonction principale de test"""
    print("🧪 TESTS DE LA GALERIE OPTIMISÉE")
    print("=" * 50)

    tests = [
        ("Gestionnaire d'index", test_image_index_manager),
        ("Processeur d'images rapide", test_fast_image_processor),
        ("Intégration galerie", test_gallery_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: RÉUSSI")
                passed += 1
            else:
                print(f"❌ {test_name}: ÉCHEC")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {str(e)}")

    print(f"\n📊 RÉSULTAT: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests sont passés!")
        print("\n🚀 OPTIMISATIONS DISPONIBLES:")
        print("• ⚡ Chargement rapide via index SQLite")
        print("• 🗑️ Suppression soft avec icône corbeille")
        print("• 📊 Statistiques détaillées de la galerie")
        print("• 🔄 Actualisation manuelle (pas automatique)")
        print("• 🧠 Cache mémoire optimisé")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

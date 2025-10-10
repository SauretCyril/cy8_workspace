#!/usr/bin/env python3
"""
Test de la fonctionnalité de sélection d'images dans la galerie
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import tempfile
from PIL import Image
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def create_test_images(temp_dir, count=3):
    """Créer des images de test"""
    image_paths = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Rouge, Vert, Bleu

    for i in range(count):
        # Créer une image colorée simple
        img = Image.new("RGB", (200, 200), color=colors[i])
        image_path = os.path.join(temp_dir, f"test_image_{i+1}.png")
        img.save(image_path)
        image_paths.append(image_path)

    return image_paths


def test_gallery_selection_functionality():
    """Tester les fonctionnalités de sélection dans la galerie"""
    print("🧪 Test de la fonctionnalité de sélection d'images...")

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

            # Vérifier que les nouvelles variables de sélection existent
            assert hasattr(
                app, "selected_gallery_image"
            ), "Variable selected_gallery_image manquante"
            assert hasattr(
                app, "selected_gallery_button"
            ), "Variable selected_gallery_button manquante"
            print("✅ Variables de sélection présentes")

            # Vérifier que la barre contextuelle existe
            assert hasattr(app, "gallery_context_frame"), "Barre contextuelle manquante"
            assert hasattr(app, "gallery_selected_label"), "Label de sélection manquant"
            print("✅ Interface de sélection présente")

            # Vérifier que les méthodes de sélection existent
            assert hasattr(
                app, "select_gallery_image"
            ), "Méthode select_gallery_image manquante"
            assert hasattr(
                app, "delete_selected_gallery_image"
            ), "Méthode de suppression manquante"
            assert hasattr(
                app, "open_selected_gallery_image"
            ), "Méthode d'ouverture manquante"
            assert hasattr(
                app, "copy_selected_gallery_path"
            ), "Méthode de copie manquante"
            print("✅ Méthodes de sélection présentes")

            # Tester le rafraîchissement de la galerie
            if hasattr(app, "refresh_gallery"):
                app.refresh_gallery()
                print("✅ Rafraîchissement de la galerie testé")

            # Vérifier l'initialisation des variables de sélection
            assert (
                app.selected_gallery_image is None
            ), "selected_gallery_image devrait être None au départ"
            assert (
                app.selected_gallery_button is None
            ), "selected_gallery_button devrait être None au départ"
            print("✅ Initialisation des variables validée")

            root.destroy()
            print("✅ Test terminé avec succès")

            return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Fonction principale de test"""
    print("🧪 TESTS DE LA GALERIE AVEC SÉLECTION")
    print("=" * 50)

    tests = [
        ("Fonctionnalité de sélection", test_gallery_selection_functionality),
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
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

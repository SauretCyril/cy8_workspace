#!/usr/bin/env python3
"""
Test du système de gestion des images simplifiée - IMAGES_COLLECTE uniquement
"""

import os
import sys
import tempfile
import shutil

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cy8_prompts_manager_main import cy8_prompts_manager
import tkinter as tk


def test_images_collecte_configuration():
    """Test de la configuration IMAGES_COLLECTE"""
    print("🧪 Test de configuration IMAGES_COLLECTE...")

    # Créer un répertoire temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        test_images_dir = os.path.join(temp_dir, "test_images")

        # Créer une application de test (sans interface graphique)
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre

        try:
            app = cy8_prompts_manager(root=root)

            # Test 1: Vérifier l'initialisation par défaut
            current_path = os.getenv("IMAGES_COLLECTE")
            print(f"   📁 Chemin IMAGES_COLLECTE actuel: {current_path}")
            assert current_path is not None, "IMAGES_COLLECTE doit être défini"

            # Test 2: Vérifier que la variable d'interface est correcte
            assert hasattr(app, 'images_path_var'), "La variable images_path_var doit exister"
            interface_path = app.images_path_var.get()
            print(f"   🖥️ Chemin dans l'interface: {interface_path}")
            assert interface_path == current_path, "L'interface doit refléter la variable d'environnement"

            # Test 3: Tester le changement de répertoire
            app.images_path_var.set(test_images_dir)
            app.apply_images_path()

            # Vérifier que la variable d'environnement a été mise à jour
            new_env_path = os.getenv("IMAGES_COLLECTE")
            print(f"   ✅ Nouveau chemin IMAGES_COLLECTE: {new_env_path}")
            assert new_env_path == test_images_dir, "La variable d'environnement doit être mise à jour"

            # Test 4: Tester la création du répertoire
            app.create_images_directory()
            assert os.path.exists(test_images_dir), "Le répertoire doit être créé"
            print(f"   📂 Répertoire créé avec succès: {test_images_dir}")

            print("✅ Tous les tests de configuration IMAGES_COLLECTE réussis !")
            return True

        except Exception as e:
            print(f"❌ Erreur dans les tests: {e}")
            return False
        finally:
            root.destroy()


def test_preferences_storage():
    """Test de la sauvegarde des préférences"""
    print("\n🧪 Test de sauvegarde des préférences...")

    with tempfile.TemporaryDirectory() as temp_dir:
        test_images_dir = os.path.join(temp_dir, "test_preferences")

        root = tk.Tk()
        root.withdraw()

        try:
            app = cy8_prompts_manager(root=root)

            # Changer le répertoire et appliquer
            app.images_path_var.set(test_images_dir)
            app.apply_images_path()

            # Vérifier que c'est sauvé dans les préférences
            saved_path = app.user_prefs.get_preference("images_collecte_path")
            print(f"   💾 Chemin sauvé dans les préférences: {saved_path}")
            assert saved_path == test_images_dir, "Le chemin doit être sauvé dans les préférences"

            print("✅ Test de sauvegarde des préférences réussi !")
            return True

        except Exception as e:
            print(f"❌ Erreur dans le test des préférences: {e}")
            return False
        finally:
            root.destroy()


def main():
    """Lancer tous les tests"""
    print("=" * 60)
    print("🧪 TESTS DU SYSTÈME D'IMAGES SIMPLIFIÉ")
    print("   Focus: IMAGES_COLLECTE uniquement")
    print("=" * 60)

    success = True

    # Test 1: Configuration IMAGES_COLLECTE
    if not test_images_collecte_configuration():
        success = False

    # Test 2: Sauvegarde des préférences
    if not test_preferences_storage():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("   Le système d'images simplifié fonctionne parfaitement.")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

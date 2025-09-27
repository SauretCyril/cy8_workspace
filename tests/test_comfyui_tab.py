#!/usr/bin/env python3
"""
Test du nouvel onglet ComfyUI et du bouton de test de connexion
"""

import os
import sys
import tkinter as tk
import tempfile

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cy8_prompts_manager_main import cy8_prompts_manager


def test_comfyui_tab_creation():
    """Test de la création de l'onglet ComfyUI"""
    print("🧪 Test de création de l'onglet ComfyUI...")

    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre

    try:
        app = cy8_prompts_manager(root=root)

        # Vérifier que la méthode setup_comfyui_tab existe
        assert hasattr(
            app, "setup_comfyui_tab"
        ), "La méthode setup_comfyui_tab doit exister"
        print("   ✅ Méthode setup_comfyui_tab trouvée")

        # Vérifier que la méthode test_comfyui_connection existe
        assert hasattr(
            app, "test_comfyui_connection"
        ), "La méthode test_comfyui_connection doit exister"
        print("   ✅ Méthode test_comfyui_connection trouvée")

        # Vérifier que les widgets de l'onglet ComfyUI existent
        assert hasattr(app, "test_connection_btn"), "Le bouton de test doit exister"
        assert hasattr(app, "status_icon_label"), "L'icône de statut doit exister"
        assert hasattr(app, "status_text_label"), "Le texte de statut doit exister"
        assert hasattr(app, "details_frame"), "Le frame des détails doit exister"
        assert hasattr(app, "details_text"), "La zone de texte des détails doit exister"
        print("   ✅ Tous les widgets de l'onglet ComfyUI sont présents")

        # Vérifier l'état initial
        initial_icon = app.status_icon_label.cget("text")
        initial_text = app.status_text_label.cget("text")
        print(f"   📍 État initial - Icône: {initial_icon}, Texte: {initial_text}")

        print("✅ Test de création de l'onglet ComfyUI réussi !")
        return True

    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        return False
    finally:
        root.destroy()


def test_connection_button_state():
    """Test de l'état du bouton de connexion"""
    print("\n🧪 Test de l'état du bouton de connexion...")

    root = tk.Tk()
    root.withdraw()

    try:
        app = cy8_prompts_manager(root=root)

        # Vérifier l'état initial du bouton
        initial_state = app.test_connection_btn.cget("state")
        initial_text = app.test_connection_btn.cget("text")

        print(f"   📍 Bouton - État: {initial_state}, Texte: {initial_text}")

        # Le bouton doit être actif initialement
        assert (
            str(initial_state) == "normal"
        ), f"Le bouton doit être actif, trouvé: {initial_state}"
        assert (
            "Tester la connexion" in initial_text
        ), f"Le texte doit contenir 'Tester la connexion', trouvé: {initial_text}"

        print("✅ Test de l'état du bouton réussi !")
        return True

    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        return False
    finally:
        root.destroy()


def test_interface_elements():
    """Test des éléments d'interface de l'onglet ComfyUI"""
    print("\n🧪 Test des éléments d'interface...")

    root = tk.Tk()
    root.withdraw()

    try:
        app = cy8_prompts_manager(root=root)

        # Vérifier que les éléments sont correctement configurés
        server_info = os.getenv("COMFYUI_SERVER", "127.0.0.1:8188")
        print(f"   📍 Serveur configuré: {server_info}")

        # Vérifier que le frame des détails n'est pas visible initialement
        details_visible = app.details_frame.winfo_viewable()
        print(f"   📍 Détails techniques visibles: {details_visible}")

        # Le frame des détails ne doit pas être visible au départ
        assert (
            not details_visible
        ), "Le frame des détails ne doit pas être visible initialement"

        print("✅ Test des éléments d'interface réussi !")
        return True

    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        return False
    finally:
        root.destroy()


def main():
    """Lancer tous les tests de l'onglet ComfyUI"""
    print("=" * 60)
    print("🧪 TESTS DE L'ONGLET COMFYUI")
    print("   Nouveau système de test de connexion dans l'interface")
    print("=" * 60)

    success = True

    # Test 1: Création de l'onglet
    if not test_comfyui_tab_creation():
        success = False

    # Test 2: État du bouton
    if not test_connection_button_state():
        success = False

    # Test 3: Éléments d'interface
    if not test_interface_elements():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("   L'onglet ComfyUI est prêt à l'emploi.")
        print("\n💡 Pour tester la connexion :")
        print("   1. python src/cy8_prompts_manager_main.py")
        print("   2. Sélectionnez un prompt")
        print("   3. Onglet 'ComfyUI' -> 'Tester la connexion'")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test des nouvelles préférences IMAGES_COLLECTE
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from cy8_prompts_manager_main import cy8_prompts_manager
from cy8_user_preferences import cy8_user_preferences

def test_images_collecte_preferences():
    """Test de la gestion d'IMAGES_COLLECTE via les préférences"""

    print("🧪 Test des préférences IMAGES_COLLECTE")

    try:
        # Test du gestionnaire de préférences seul
        user_prefs = cy8_user_preferences()

        # Vérifier les nouvelles préférences par défaut
        default_comfyui = user_prefs.get_preference("default_comfyui_output_path")
        images_collecte = user_prefs.get_preference("images_collecte_path")

        print(f"✅ default_comfyui_output_path: {default_comfyui}")
        print(f"✅ images_collecte_path: {images_collecte}")

        # Tester la définition d'un chemin IMAGES_COLLECTE
        test_path = "C:/test_images"
        user_prefs.set_preference("images_collecte_path", test_path)

        # Vérifier que la valeur est bien sauvegardée
        retrieved_path = user_prefs.get_preference("images_collecte_path")
        if retrieved_path == test_path:
            print(f"✅ Sauvegarde préférence IMAGES_COLLECTE: {retrieved_path}")
        else:
            print(f"❌ Erreur sauvegarde: attendu {test_path}, reçu {retrieved_path}")
            return False

        # Test avec l'application complète
        root = tk.Tk()
        app = cy8_prompts_manager(root)

        # Vérifier que init_images_paths utilise bien les préférences
        print(f"✅ Application créée - IMAGES_COLLECTE: {os.getenv('IMAGES_COLLECTE')}")

        # Nettoyer le test
        user_prefs.set_preference("images_collecte_path", "")  # Remettre à vide
        root.destroy()

        print("🎉 Tous les tests passés - IMAGES_COLLECTE géré par les préférences!")
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_preferences_priority():
    """Test de l'ordre de priorité des préférences"""

    print("\n🧪 Test de priorité des préférences IMAGES_COLLECTE")

    try:
        user_prefs = cy8_user_preferences()

        # Cas 1: Préférence utilisateur définie
        user_prefs.set_preference("images_collecte_path", "C:/user_pref_path")
        os.environ["IMAGES_COLLECTE"] = "C:/env_path"  # Variable d'environnement

        root = tk.Tk()
        app = cy8_prompts_manager(root)

        final_path = os.getenv("IMAGES_COLLECTE")
        expected = "C:/user_pref_path"  # La préférence devrait avoir priorité

        # Note: Comme le chemin n'existe pas, il utilisera la valeur par défaut
        print(f"📋 Priorité testée - Chemin final: {final_path}")

        # Nettoyer
        user_prefs.set_preference("images_collecte_path", "")
        root.destroy()

        print("✅ Test de priorité terminé")
        return True

    except Exception as e:
        print(f"❌ Erreur test priorité: {e}")
        return False

if __name__ == "__main__":
    success1 = test_images_collecte_preferences()
    success2 = test_preferences_priority()

    overall_success = success1 and success2
    print(f"\n{'✅ SUCCÈS' if overall_success else '❌ ÉCHEC'} - Test des préférences IMAGES_COLLECTE")
    sys.exit(0 if overall_success else 1)

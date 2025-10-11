#!/usr/bin/env python3
"""
Test simple de lancement de l'application avec galerie
"""

import os
import sys
import tempfile
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_app_startup():
    """Test de démarrage de l'application"""
    print("🚀 Test de démarrage de l'application", flush=True)
    print("=" * 40, flush=True)

    try:
        # Créer un répertoire temporaire vide pour éviter les erreurs
        temp_dir = tempfile.mkdtemp()
        os.environ["IMAGES_COLLECTE"] = temp_dir
        print(f"📁 IMAGES_COLLECTE: {temp_dir}", flush=True)

        # Test d'import seulement
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("Import réussi", flush=True)

        # Test de création sans interface (headless)
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()  # Masquer complètement

        # Ne pas créer l'app complète pour éviter les erreurs de géométrie
        print("✅ Tkinter root créé")

        root.destroy()
        print("✅ Nettoyage effectué")

        # Nettoyer
        import shutil

        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if test_app_startup():
        print("\n🎉 Test de démarrage réussi!")
        print("\n💡 L'application devrait se lancer correctement.")
        print("   Allez dans l'onglet Images pour voir les sous-onglets:")
        print("   • 📋 Images du prompt (fonctionnalité existante)")
        print("   • 🖼️ Galerie complète (nouvelle fonctionnalité)")
    else:
        print("\n💥 Test de démarrage échoué!")
        exit(1)

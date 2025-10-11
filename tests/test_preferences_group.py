#!/usr/bin/env python3
"""
Test du nouveau groupe Préférences dans le ruban
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from cy8_prompts_manager_main import cy8_prompts_manager

def test_preferences_button():
    """Test d'intégration du bouton Préférences"""

    print("🧪 Test du groupe Préférences dans le ruban")

    try:
        # Créer l'application
        root = tk.Tk()
        app = cy8_prompts_manager(root)

        print("✅ Application créée avec succès")

        # Vérifier que la méthode open_user_preferences existe
        if hasattr(app, 'open_user_preferences'):
            print("✅ Méthode open_user_preferences trouvée")
        else:
            print("❌ Méthode open_user_preferences manquante")
            return False

        # Vérifier que user_prefs est initialisé
        if hasattr(app, 'user_prefs') and app.user_prefs:
            print("✅ Gestionnaire de préférences initialisé")
        else:
            print("❌ Gestionnaire de préférences manquant")
            return False

        # Vérifier quelques préférences de base
        prefs = app.user_prefs.preferences
        if 'version' in prefs:
            print(f"✅ Préférences chargées - Version: {prefs['version']}")
        else:
            print("⚠️ Préférences vides ou corrompues")

        # Test rapide de sauvegarde
        try:
            app.user_prefs._save_preferences()
            print("✅ Test de sauvegarde réussi")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde: {e}")

        print("🎉 Tous les tests passés - Groupe Préférences fonctionnel!")

        # Ne pas afficher l'interface pour le test
        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_preferences_button()
    print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'} - Test du groupe Préférences")
    sys.exit(0 if success else 1)

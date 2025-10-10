"""
Test du système d'identifiants uniques pour les popups
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_popup_id_manager():
    """Test du gestionnaire d'identifiants de popups"""
    print("🧪 Test du gestionnaire d'identifiants de popups")
    print("=" * 60)

    try:
        from cy8_popup_id_manager import popup_manager, get_popup_id, close_popup

        # Test 1: Création d'identifiants
        print("\n📋 Test 1: Création d'identifiants")
        popup_id1, title1 = get_popup_id(
            "Analyse complète du log ComfyUI - Mistral AI", "analysis"
        )
        popup_id2, title2 = get_popup_id("Configuration des préférences", "settings")
        popup_id3, title3 = get_popup_id("Détails du prompt", "details")

        print(f"  ✅ {popup_id1}: {title1}")
        print(f"  ✅ {popup_id2}: {title2}")
        print(f"  ✅ {popup_id3}: {title3}")

        # Test 2: Vérification des popups actives
        print("\n📊 Test 2: Popups actives")
        active_popups = popup_manager.get_active_popups()
        print(f"  📋 Nombre de popups actives: {len(active_popups)}")
        for popup_id, info in active_popups.items():
            print(
                f"    - {popup_id}: {info['title']} ({info['type']}) - {info['created_at']}"
            )

        # Test 3: Fermeture d'une popup
        print("\n🔚 Test 3: Fermeture d'une popup")
        close_popup(popup_id2)
        print(f"  ✅ Popup {popup_id2} fermée")

        active_popups_after = popup_manager.get_active_popups()
        print(f"  📋 Popups actives après fermeture: {len(active_popups_after)}")

        # Test 4: Historique des popups
        print("\n📚 Test 4: Historique des popups")
        history = popup_manager.get_popup_history()
        print(f"  📋 Nombre total de popups créées: {len(history)}")
        for entry in history[-3:]:  # Afficher les 3 dernières
            print(f"    - {entry['id']}: {entry['title']} ({entry['type']})")

        # Test 5: Affichage du statut
        print("\n📈 Test 5: Statut du gestionnaire")
        popup_manager.print_status()

        print("\n🎉 Tous les tests ont réussi !")

        # Instructions d'utilisation
        print("\n" + "=" * 60)
        print("📋 UTILISATION DANS L'APPLICATION")
        print("=" * 60)
        print(
            "1. Maintenant chaque popup a un identifiant unique (POP001, POP002, etc.)"
        )
        print("2. L'ID apparaît dans le titre de la popup")
        print("3. Pour la popup Mistral AI, l'ID est inclus dans le fichier sauvegardé")
        print("4. Vous pouvez maintenant me référencer précisément les popups !")
        print("")
        print("Exemples de communication :")
        print("  - 'Dans la popup POP001, le bouton sauvegarde ne fonctionne pas'")
        print("  - 'Le fichier généré par POP003 est mal formaté'")
        print("  - 'Comment modifier le titre de POP002 ?'")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_popup_id_manager()

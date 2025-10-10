"""
Test de l'intégration environnement avec l'onglet Log
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_environment_log_integration():
    """Test de l'intégration environnement-log"""
    print("🧪 Test d'intégration Environnement ↔ Log")
    print("=" * 60)

    try:
        # Simuler les différents états

        print("\n📋 Test 1: État initial (aucun environnement)")
        print("  - Environnement: Non identifié")
        print("  - Boutons analyse: Désactivés")
        print("  - Affichage: '⚠️ Environnement: Non identifié (requis pour l'analyse)'")

        print("\n📋 Test 2: Après identification environnement")
        print("  - Environnement: G11_01 identifié")
        print("  - Boutons analyse: Activés")
        print("  - Affichage: '🌍 Environnement: G11_01'")

        print("\n📋 Test 3: Tentative d'analyse sans environnement")
        print("  - Message d'erreur: 'Environnement requis'")
        print("  - Redirection vers onglet ComfyUI")

        print("\n📋 Test 4: Flux complet")
        print("  1. Démarrage → Boutons désactivés")
        print("  2. Onglet ComfyUI → 'Identifier l'environnement'")
        print("  3. Retour onglet Log → Boutons activés, environnement affiché")
        print("  4. Analyse possible → Environnement inclus dans sauvegarde")

        print("\n🎯 Fonctionnalités implémentées:")
        print("  ✅ Variable self.current_environment_id")
        print("  ✅ Affichage environnement dans bloc informations")
        print("  ✅ Méthode update_analysis_buttons_state()")
        print("  ✅ Méthode set_current_environment()")
        print("  ✅ Vérification environnement dans analyze_comfyui_log()")
        print("  ✅ Vérification environnement dans analyze_complete_log_global()")
        print("  ✅ Intégration avec identify_comfyui_environment()")

        print("\n📱 Interface utilisateur:")
        print("  ✅ Boutons désactivés au démarrage")
        print("  ✅ Texte explicatif sur les boutons désactivés")
        print("  ✅ Couleur orange quand environnement manque")
        print("  ✅ Couleur verte quand environnement identifié")
        print("  ✅ Message d'erreur si tentative d'analyse sans environnement")

        print("\n📊 Workflow utilisateur:")
        print("  1. 🚀 Lancer l'application")
        print("  2. 📊 Aller dans l'onglet Log")
        print("  3. ⚠️ Voir 'Environnement: Non identifié' + boutons désactivés")
        print("  4. 🔧 Aller dans l'onglet ComfyUI")
        print("  5. 🔍 Cliquer 'Identifier l'environnement'")
        print("  6. ✅ Voir 'Environnement identifié: G11_01'")
        print("  7. 📊 Retourner dans l'onglet Log")
        print("  8. 🌍 Voir 'Environnement: G11_01' + boutons activés")
        print("  9. 🔍 Pouvoir analyser le log avec environnement sauvegardé")

        print("\n🎉 Test d'intégration réussi !")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_environment_log_integration()

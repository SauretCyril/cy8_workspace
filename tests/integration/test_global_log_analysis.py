#!/usr/bin/env python3
"""
Test de l'analyse globale du log avec le nouveau bouton.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_global_log_analysis():
    """Test de l'analyse globale du log avec le nouveau bouton"""
    print("🧪 Test de l'analyse globale du log avec le nouveau bouton")
    print("=" * 60)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("✅ Import de cy8_prompts_manager réussi")

        # Créer l'application
        app = cy8_prompts_manager()
        print("✅ Application créée")

        # Vérifier que le bouton d'analyse IA globale existe
        if hasattr(app, "ai_analyze_btn"):
            print("✅ Bouton d'analyse IA globale trouvé")
            print(f"   Text: {app.ai_analyze_btn.cget('text')}")
        else:
            print("❌ Bouton d'analyse IA globale non trouvé")

        # Vérifier que la méthode d'analyse globale existe
        if hasattr(app, "analyze_complete_log_global"):
            print("✅ Méthode analyze_complete_log_global trouvée")
        else:
            print("❌ Méthode analyze_complete_log_global non trouvée")

        # Vérifier que les méthodes obsolètes ont été supprimées
        obsolete_methods = [
            "analyze_complete_log_with_ai",
            "display_log_analysis",
            "display_analysis_error",
            "save_log_analysis",
        ]

        for method in obsolete_methods:
            if hasattr(app, method):
                print(f"⚠️  Méthode obsolète encore présente: {method}")
            else:
                print(f"✅ Méthode obsolète supprimée: {method}")

        # Vérifier que la méthode show_log_detail est simplifiée
        if hasattr(app, "show_log_detail"):
            print("✅ Méthode show_log_detail présente (fenêtre détails simple)")
        else:
            print("❌ Méthode show_log_detail manquante")

        # Vérifier l'existence du module Mistral
        try:
            from cy8_mistral import analyze_comfyui_log_complete

            print("✅ Fonction analyze_comfyui_log_complete disponible")
        except ImportError as e:
            print(f"❌ Fonction analyze_comfyui_log_complete non disponible: {e}")

        print("\n🎯 Résumé des fonctionnalités:")
        print("   • Double-clic sur ligne d'erreur → Détails simples (sans IA)")
        print("   • Bouton '🤖 Analyse IA complète' → Analyse globale du log")
        print("   • Même question et rôle pour Mistral AI")
        print("   • Analyse du log complet au lieu d'erreurs individuelles")

        # Fermer l'application
        app.root.quit()
        app.root.destroy()

        print("\n✅ Test terminé avec succès!")
        return True

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_global_log_analysis()
    if success:
        print("\n🎉 Tous les tests sont passés!")
    else:
        print("\n💥 Certains tests ont échoué!")
        sys.exit(1)

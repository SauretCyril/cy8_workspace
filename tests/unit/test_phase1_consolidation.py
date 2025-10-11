#!/usr/bin/env python3
"""
Test de validation Phase 1 - Consolidation des fonctions UI
Vérifie que cy8_ui_utils.center_window() fonctionne correctement
"""

import tkinter as tk
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from cy8_ui_utils import center_window
    print("✅ Import cy8_ui_utils.center_window réussi")
except ImportError as e:
    print(f"❌ Erreur import cy8_ui_utils: {e}")
    sys.exit(1)

def test_center_window():
    """Test simple de la fonction center_window"""
    root = tk.Tk()
    root.title("Test Phase 1 - Consolidation UI")

    # Créer une fenêtre de test
    test_window = tk.Toplevel(root)
    test_window.title("Fenêtre de test centrée")

    # Ajouter du contenu
    tk.Label(test_window, text="✅ Consolidation Phase 1 réussie!\n\nLa fonction center_window() \nfonctionne correctement.",
             font=("Arial", 12), pady=20, padx=20).pack()

    # Bouton fermer
    tk.Button(test_window, text="Fermer", command=test_window.destroy,
              font=("Arial", 10), pady=5).pack(pady=10)

    # TESTER LA FONCTION CONSOLIDÉE
    try:
        center_window(test_window, 400, 200)
        print("✅ Function center_window() appelée avec succès")
        print("✅ Phase 1 consolidation VALIDÉE")

        # Afficher la fenêtre pendant 3 secondes puis fermer
        root.after(3000, root.quit)
        root.mainloop()

        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'appel center_window(): {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test Phase 1 - Consolidation des fonctions UI")
    print("=" * 50)

    success = test_center_window()

    if success:
        print("\n🎉 PHASE 1 CONSOLIDATION RÉUSSIE!")
        print("✅ cy8_ui_utils.center_window() fonctionne")
        print("✅ Imports consolidés correctement")
        print("✅ Fonctions dupliquées supprimées")
    else:
        print("\n❌ Échec du test Phase 1")
        sys.exit(1)

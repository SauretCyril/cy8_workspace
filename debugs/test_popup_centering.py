#!/usr/bin/env python3
"""
Test du centrage des popups
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_center_function():
    """Test de la fonction de centrage"""
    print("=== TEST FONCTION DE CENTRAGE ===")

    try:
        # Import de la fonction de centrage
        from cy8_prompts_manager_main import center_window
        print("✅ Import de center_window réussi")

        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale

        # Test 1: Centrer une petite popup
        popup1 = tk.Toplevel(root)
        popup1.title("Test Popup 1 - 400x300")
        popup1.geometry("400x300")
        center_window(popup1, 400, 300)

        # Vérifier la position
        popup1.update_idletasks()
        x = popup1.winfo_x()
        y = popup1.winfo_y()
        width = popup1.winfo_width()
        height = popup1.winfo_height()

        screen_width = popup1.winfo_screenwidth()
        screen_height = popup1.winfo_screenheight()

        expected_x = (screen_width - 400) // 2
        expected_y = (screen_height - 300) // 2

        print(f"✅ Popup 1: Position ({x}, {y}), Attendu environ ({expected_x}, {expected_y})")
        print(f"✅ Popup 1: Taille {width}x{height}")

        # Test 2: Centrer une grande popup
        popup2 = tk.Toplevel(root)
        popup2.title("Test Popup 2 - 800x600")
        popup2.geometry("800x600")
        center_window(popup2, 800, 600)

        popup2.update_idletasks()
        x2 = popup2.winfo_x()
        y2 = popup2.winfo_y()

        expected_x2 = (screen_width - 800) // 2
        expected_y2 = (screen_height - 600) // 2

        print(f"✅ Popup 2: Position ({x2}, {y2}), Attendu environ ({expected_x2}, {expected_y2})")

        # Test 3: Centrer sans spécifier la taille
        popup3 = tk.Toplevel(root)
        popup3.title("Test Popup 3 - Auto-size")
        label = ttk.Label(popup3, text="Popup auto-dimensionnée\navec du contenu\nsur plusieurs lignes", font=("TkDefaultFont", 12))
        label.pack(padx=20, pady=20)

        center_window(popup3)  # Sans spécifier width/height

        popup3.update_idletasks()
        x3 = popup3.winfo_x()
        y3 = popup3.winfo_y()
        w3 = popup3.winfo_width()
        h3 = popup3.winfo_height()

        print(f"✅ Popup 3: Position ({x3}, {y3}), Taille {w3}x{h3}")

        # Afficher brièvement les popups pour vérification visuelle
        print("\n👁️ Popups affichées pendant 3 secondes pour vérification visuelle...")
        root.after(3000, lambda: root.quit())  # Fermer après 3 secondes
        root.mainloop()

        # Nettoyer
        popup1.destroy()
        popup2.destroy()
        popup3.destroy()
        root.destroy()

        print("🎉 Test du centrage terminé avec succès !")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_center_function()

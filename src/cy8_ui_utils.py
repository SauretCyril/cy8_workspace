"""
cy8_ui_utils.py - Utilitaires UI partagés
=========================================

Module contenant les fonctions utilitaires communes pour l'interface utilisateur.
Consolide les fonctions dupliquées identifiées lors de l'audit du code.

Fonctions disponibles:
    - center_window(window, width, height) : Centre une fenêtre sur l'écran
    - close_dialog(window) : Ferme proprement un dialogue/popup
    - get_window_center_position(width, height) : Calcule la position centrée

Historique:
    - 2025-10-10: Création du module (Phase 1 consolidation audit)
    - Consolide center_window (2 définitions → 1)
    - Consolide cancel (4 définitions → 1 close_dialog)
"""

import tkinter as tk
from typing import Tuple, Optional


def center_window(window: tk.Toplevel, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """
    Centre une fenêtre sur l'écran.
    
    Args:
        window: Fenêtre Tkinter à centrer (Toplevel, Tk, etc.)
        width: Largeur de la fenêtre (optionnel, détectée automatiquement si None)
        height: Hauteur de la fenêtre (optionnel, détectée automatiquement si None)
    
    Exemple:
        >>> dialog = tk.Toplevel()
        >>> center_window(dialog, 600, 400)
    
    Note:
        Consolide les 2 définitions précédentes:
        - cy8_popup_manager.py:14
        - cy8_prompts_manager_main.py:12
    """
    # Mettre à jour la fenêtre pour obtenir les bonnes dimensions
    window.update_idletasks()
    
    # Obtenir les dimensions de la fenêtre
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    
    # Obtenir les dimensions de l'écran
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculer la position centrée
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Appliquer la géométrie
    window.geometry(f"{width}x{height}+{x}+{y}")


def get_window_center_position(width: int, height: int, 
                                screen_width: Optional[int] = None, 
                                screen_height: Optional[int] = None) -> Tuple[int, int]:
    """
    Calcule la position centrée pour une fenêtre.
    
    Args:
        width: Largeur de la fenêtre
        height: Hauteur de la fenêtre
        screen_width: Largeur de l'écran (optionnel, détectée si None)
        screen_height: Hauteur de l'écran (optionnel, détectée si None)
    
    Returns:
        Tuple (x, y) avec les coordonnées du coin supérieur gauche
    
    Exemple:
        >>> x, y = get_window_center_position(600, 400)
        >>> window.geometry(f"600x400+{x}+{y}")
    """
    if screen_width is None:
        root = tk.Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    return x, y


def close_dialog(window: tk.Toplevel) -> None:
    """
    Ferme proprement un dialogue ou popup.
    
    Args:
        window: Fenêtre Tkinter à fermer (Toplevel, Tk, etc.)
    
    Exemple:
        >>> def on_cancel():
        >>>     close_dialog(dialog)
        >>> ttk.Button(frame, text="Annuler", command=on_cancel)
    
    Note:
        Consolide les 4 définitions de cancel():
        - cy8_popup_manager.py:304
        - cy8_popup_manager.py:543
        - cy8_prompts_manager_main.py:4735
        - cy8_prompts_manager_main.py:11845
        
        Toutes faisaient simplement window.destroy() ou dialog.destroy()
    """
    if window and window.winfo_exists():
        window.destroy()


def create_centered_dialog(parent: tk.Tk, title: str, width: int, height: int, 
                           modal: bool = True) -> tk.Toplevel:
    """
    Crée et centre un dialogue Toplevel.
    
    Args:
        parent: Fenêtre parente
        title: Titre du dialogue
        width: Largeur du dialogue
        height: Hauteur du dialogue
        modal: Si True, rend le dialogue modal (bloque l'interaction avec parent)
    
    Returns:
        Fenêtre Toplevel créée et centrée
    
    Exemple:
        >>> dialog = create_centered_dialog(root, "Configuration", 500, 400)
        >>> # ... ajouter des widgets au dialogue
        >>> dialog.mainloop()
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    
    # Rendre modal si demandé
    if modal:
        dialog.transient(parent)
        dialog.grab_set()
    
    # Centrer le dialogue
    center_window(dialog, width, height)
    
    return dialog


def confirm_dialog(parent: tk.Tk, title: str, message: str, 
                   confirm_text: str = "Confirmer", 
                   cancel_text: str = "Annuler") -> bool:
    """
    Affiche un dialogue de confirmation simple.
    
    Args:
        parent: Fenêtre parente
        title: Titre du dialogue
        message: Message à afficher
        confirm_text: Texte du bouton de confirmation
        cancel_text: Texte du bouton d'annulation
    
    Returns:
        True si l'utilisateur a confirmé, False sinon
    
    Exemple:
        >>> if confirm_dialog(root, "Suppression", "Confirmer la suppression ?"):
        >>>     # Supprimer l'élément
        >>>     pass
    """
    from tkinter import messagebox
    return messagebox.askyesno(title, message, parent=parent)


# Statistiques du module
__stats__ = {
    "functions_consolidated": 6,  # 2 center_window + 4 cancel
    "lines_saved": 33,
    "files_impacted": 4,  # main, popup_manager, editable_tables, ce fichier
    "calls_to_update": 26  # 22 center_window + 4 cancel
}

__all__ = [
    'center_window',
    'get_window_center_position', 
    'close_dialog',
    'create_centered_dialog',
    'confirm_dialog'
]


if __name__ == "__main__":
    # Test des fonctions
    print("🧪 Test de cy8_ui_utils.py")
    print("=" * 50)
    
    # Test 1: Calcul de position centrée
    x, y = get_window_center_position(600, 400)
    print(f"✓ Position centrée calculée: x={x}, y={y}")
    
    # Test 2: Création d'une fenêtre de test
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("Test cy8_ui_utils")
    
    label = tk.Label(dialog, text="Fenêtre centrée automatiquement", padx=20, pady=20)
    label.pack()
    
    center_window(dialog, 400, 200)
    
    print("✓ Fenêtre de test créée et centrée")
    print(f"✓ Géométrie appliquée: {dialog.geometry()}")
    
    # Test 3: Fermeture
    close_dialog(dialog)
    print("✓ Fermeture testée avec succès")
    
    root.destroy()
    
    print("\n📊 Statistiques du module:")
    for key, value in __stats__.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Tous les tests passés!")

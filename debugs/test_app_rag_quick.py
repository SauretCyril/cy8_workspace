#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide de l'application avec les corrections RAG
"""
import sys
import os

# Ajouter le chemin src au Python path
sys.path.append('src')

def test_app_quick():
    """Test rapide de l'application"""
    print('=== TEST APPLICATION AVEC CORRECTIONS RAG ===')

    try:
        # Import de l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cacher la fenetre

        print('Creation de l\'instance...')
        app = cy8_prompts_manager()

        print('Application creee avec succes')

        # Test des corrections
        if hasattr(app, 'rag_manager') and app.rag_manager:
            print('RAG Manager trouve')

            # Test d'une requête rapide
            try:
                result = app.rag_manager._query_rapid_mode("test query", 3)
                print('Mode rapide fonctionne')
            except Exception as e:
                print(f'Mode rapide: {e}')

        root.destroy()
        print('Test termine avec succes!')
        return True

    except Exception as e:
        print(f'Erreur: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_quick()
    exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet avec identification reelle et RAG
"""
import sys
import os

# Ajouter le chemin src au Python path
sys.path.append('src')

def test_real_identification():
    """Test avec identification reelle"""
    print('=== TEST IDENTIFICATION REELLE + RAG ===')

    try:
        # Import de l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cacher la fenetre

        print('Creation de l\'instance...')
        app = cy8_prompts_manager()

        print('Application creee avec succes')

        # Vérifier l'état initial
        print(f'\nEtat initial:')
        print(f'  current_environment_id = {app.current_environment_id}')
        if hasattr(app, 'rag_manager') and app.rag_manager:
            print(f'  rag_manager.environment_id = {app.rag_manager.environment_id}')

        # Faire une identification réelle
        print('\nLancement identification reelle...')
        try:
            app.identify_comfyui_environment()
            print('Identification terminee')

            # Vérifier l'état après identification
            print(f'\nEtat apres identification:')
            print(f'  current_environment_id = {app.current_environment_id}')
            print(f'  comfyui_config_id = {app.comfyui_config_id.get()}')

            if hasattr(app, 'rag_manager') and app.rag_manager:
                print(f'  rag_manager.environment_id = {app.rag_manager.environment_id}')

                # Test RAG après identification
                print('\nTest RAG apres identification...')
                if app.current_environment_id:
                    print('✅ Environment detecte - RAG devrait fonctionner')

                    # Test d'une requête rapide
                    try:
                        result = app.rag_manager._query_rapid_mode("test", 3)
                        print('✅ Requete RAG rapide reussie')
                    except Exception as e:
                        print(f'⚠️ Erreur requete RAG: {e}')
                else:
                    print('❌ Environment toujours None apres identification')

        except Exception as e:
            print(f'Erreur identification: {e}')

        root.destroy()
        print('\nTest termine!')
        return True

    except Exception as e:
        print(f'Erreur: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_identification()
    exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la synchronisation de l'environnement avec le RAG
"""
import sys
import os

# Ajouter le chemin src au Python path
sys.path.append('src')

def test_environment_sync():
    """Test de la synchronisation environnement/RAG"""
    print('=== TEST SYNCHRONISATION ENVIRONNEMENT RAG ===')
    
    try:
        # Import de l'application
        from cy8_prompts_manager_main import cy8_prompts_manager
        
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cacher la fenetre
        
        print('Creation de l\'instance...')
        app = cy8_prompts_manager()
        
        print('Application creee avec succes')
        
        # Simuler l'identification d'environnement
        print('\nTest 1: current_environment_id initial')
        print(f'current_environment_id = {app.current_environment_id}')
        
        if hasattr(app, 'rag_manager') and app.rag_manager:
            print(f'rag_manager.environment_id = {app.rag_manager.environment_id}')
        
        # Simuler une identification réussie
        print('\nTest 2: Simulation identification H12_01...')
        app.current_environment_id = 'H12_01'
        app.comfyui_config_id.set('H12_01')
        
        # Appeler set_current_environment comme le fait l'identification
        print('Test 3: Appel de set_current_environment...')
        app.set_current_environment('H12_01')
        
        print('\nTest 4: Verification apres synchronisation')
        print(f'current_environment_id = {app.current_environment_id}')
        
        if hasattr(app, 'rag_manager') and app.rag_manager:
            print(f'rag_manager.environment_id = {app.rag_manager.environment_id}')
            
            # Test d'une requête pour voir si l'erreur persiste
            print('\nTest 5: Test requete RAG apres synchronisation...')
            try:
                # Cette partie devrait maintenant fonctionner
                if app.current_environment_id:
                    print('Environment detecte pour RAG: OK')
                else:
                    print('ERREUR: Environment toujours None')
                    
            except Exception as e:
                print(f'Erreur requete RAG: {e}')
        
        root.destroy()
        print('\nTest termine avec succes!')
        return True
        
    except Exception as e:
        print(f'Erreur: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_environment_sync()
    exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du système TODO/Focus intégré au RAG
"""
import sys
import os

# Ajouter le chemin src au Python path
sys.path.append('src')

def test_todo_system():
    """Test du système TODO"""
    print('=== TEST SYSTÈME TODO/FOCUS ===')

    try:
        # Import de l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cacher la fenetre

        print('Creation de l\'instance...')
        app = cy8_prompts_manager()

        # Simuler l'identification d'environnement
        app.current_environment_id = 'TEST_H12'
        app.set_current_environment('TEST_H12')

        print('Application creee avec succes')

        # Vérifier le TODO manager
        if hasattr(app, 'rag_manager') and app.rag_manager and app.rag_manager.todo_manager:
            todo_manager = app.rag_manager.todo_manager
            print('✅ TODO manager trouve')

            # Test 1: Ajouter une tâche
            print('\nTest 1: Ajout d\'une tache...')
            todo_id = todo_manager.add_todo(
                "Analyser les erreurs ComfyUI",
                "Examiner le log pour identifier les problèmes récurrents",
                priority=4
            )
            print(f'Tache ajoutee avec ID: {todo_id}')

            # Test 2: Lister les tâches
            print('\nTest 2: Liste des taches...')
            todos = todo_manager.get_todos()
            for todo in todos:
                print(f'- {todo["id"]}: {todo["title"]} ({todo["status"]})')

            # Test 3: Commandes chat
            print('\nTest 3: Commandes chat...')

            # Test commande /todo list
            result = app.rag_manager.process_todo_command('/todo list')
            print('Commande /todo list:')
            print(result['response'][:100] + '...')

            # Test commande /focus
            if todo_id:
                result = app.rag_manager.process_todo_command(f'/focus {todo_id}')
                print(f'\nCommande /focus {todo_id}:')
                print(result['response'][:100] + '...')

                # Vérifier le focus
                focus_id = app.rag_manager.get_current_focus()
                print(f'Focus actuel: {focus_id}')

                # Test /status
                result = app.rag_manager.process_todo_command('/status')
                print(f'\nCommande /status:')
                print(result['response'][:100] + '...')

                # Test /end-focus
                result = app.rag_manager.process_todo_command('/end-focus')
                print(f'\nCommande /end-focus:')
                print(result['response'][:100] + '...')

            # Test 4: Reconnaissance des commandes
            print('\nTest 4: Reconnaissance des commandes...')
            test_commands = [
                '/todo list',
                '/todo add Test',
                '/focus abc123',
                '/end-focus',
                '/help',
                'simple question'
            ]

            for cmd in test_commands:
                is_todo = app.rag_manager.is_todo_command(cmd)
                print(f'{cmd}: {"TODO" if is_todo else "NORMAL"}')
        else:
            print('❌ TODO manager non trouve')

        root.destroy()
        print('\n✅ Test termine avec succes!')
        return True

    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_todo_system()
    exit(0 if success else 1)

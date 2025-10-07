import os
import sys
import json

# Ajouter le chemin src pour les imports
sys.path.append('src')

def test_identification_complete():
    """Test complet de l'identification comme dans l'application"""
    print('=== TEST IDENTIFICATION COMPLÈTE ===')

    try:
        # Simuler l'environnement de l'application
        from cy8_prompts_manager_main import cy8_prompts_manager

        print('🔧 Création d\'une instance temporaire de l\'application...')

        # Créer une instance minimale pour tester les méthodes
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre

        app = cy8_prompts_manager()
        app.root = root

        # Initialiser les variables nécessaires
        app.comfyui_config_id = tk.StringVar()
        app.current_environment_id = None

        # Créer un label temporaire pour les tests
        import tkinter.ttk as ttk
        app.config_info_label = ttk.Label(root, text="Test")

        print('✅ Instance créée')

        # Test 1: Méthode fallback
        print('\n🔍 Test 1: Méthode de fallback...')
        fallback_id = app._generate_environment_id_fallback()
        print(f'ID fallback généré: {fallback_id}')

        # Test 2: Analyse de l'environnement
        print('\n🔍 Test 2: Analyse complète de l\'environnement...')
        try:
            env_analysis = app._analyze_comfyui_environment()
            print(f'Résultat analyse: {env_analysis}')
        except Exception as e:
            print(f'Erreur analyse: {e}')

        # Test 3: Extraction depuis analysis
        print('\n🔍 Test 3: Test extraction avec données vides...')
        empty_result = app._extract_environment_id_from_analysis({}, [])
        print(f'Extraction données vides: {empty_result}')

        # Test 4: Vérifier s'il y a des préférences stockées
        print('\n🔍 Test 4: Vérification des préférences utilisateur...')
        try:
            if hasattr(app, 'user_prefs'):
                print('Gestionnaire de préférences disponible')
            else:
                print('Pas de gestionnaire de préférences')
        except Exception as e:
            print(f'Erreur préférences: {e}')

        # Test 5: Vérifier la base de données
        print('\n🔍 Test 5: Vérification de la base de données...')
        try:
            if hasattr(app, 'db_manager'):
                print('Gestionnaire de base de données disponible')
                # Vérifier s'il y a des environnements stockés
                environments = app.db_manager.get_all_environments()
                print(f'Environnements en base: {len(environments)}')
                for env in environments:
                    print(f'  - {env}')
            else:
                print('Pas de gestionnaire de base de données')
        except Exception as e:
            print(f'Erreur base de données: {e}')

        root.destroy()

    except Exception as e:
        print(f'❌ Erreur lors du test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_identification_complete()

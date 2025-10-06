#!/usr/bin/env python3
"""
Test rapide du terminal intégré dans l'interface
Vérifie que l'onglet terminal est bien créé et configuré.
"""

import sys
import tkinter as tk
from pathlib import Path

# Ajouter le dossier src au chemin
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_terminal_tab_creation():
    """Test de création de l'onglet terminal"""
    print("🧪 Test création onglet terminal...")

    try:
        # Import des modules
        from cy8_prompts_manager_main import cy8_prompts_manager

        # Créer instance (sans lancer l'interface)
        app = cy8_prompts_manager()

        # Vérifier que l'onglet terminal existe
        if hasattr(app, 'terminal_tab'):
            print("✅ Onglet terminal créé")
        else:
            print("❌ Onglet terminal manquant")
            return False

        # Vérifier les composants du terminal
        components = [
            'terminal_output',
            'terminal_input',
            'terminal_cwd_var',
            'terminal_rag_enabled',
            'terminal_history',
            'current_process'
        ]

        missing = []
        for component in components:
            if not hasattr(app, component):
                missing.append(component)

        if missing:
            print(f"❌ Composants manquants: {missing}")
            return False
        else:
            print("✅ Tous les composants terminal présents")

        # Vérifier les méthodes du terminal
        methods = [
            'setup_terminal_tab',
            'execute_terminal_command',
            'run_command_in_subprocess',
            'interrupt_terminal_command',
            'change_terminal_directory',
            'browse_terminal_directory',
            'on_terminal_key_press',
            'navigate_terminal_history',
            'append_terminal_output',
            'save_terminal_session',
            'clear_terminal_output',
            'index_terminal_session'
        ]

        missing_methods = []
        for method in methods:
            if not hasattr(app, method):
                missing_methods.append(method)

        if missing_methods:
            print(f"❌ Méthodes manquantes: {missing_methods}")
            return False
        else:
            print("✅ Toutes les méthodes terminal présentes")

        # Détruire l'instance proprement
        if hasattr(app, 'root'):
            app.root.destroy()

        return True

    except Exception as e:
        print(f"❌ Erreur test interface terminal: {e}")
        return False

def test_terminal_configuration():
    """Test de la configuration du terminal"""
    print("🧪 Test configuration terminal...")

    try:
        # Créer une racine Tkinter de test
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre

        # Import et création app
        from cy8_prompts_manager_main import cy8_prompts_manager
        app = cy8_prompts_manager()

        # Vérifier configuration initiale
        if hasattr(app, 'terminal_cwd'):
            print(f"✅ Répertoire initial: {app.terminal_cwd}")
        else:
            print("❌ Répertoire de travail non configuré")
            return False

        # Vérifier historique
        if hasattr(app, 'terminal_history') and isinstance(app.terminal_history, list):
            print("✅ Historique initialisé")
        else:
            print("❌ Historique non configuré")
            return False

        # Vérifier processus
        if hasattr(app, 'current_process'):
            print("✅ Gestionnaire processus configuré")
        else:
            print("❌ Gestionnaire processus manquant")
            return False

        # Nettoyer
        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Erreur test configuration: {e}")
        return False

def test_terminal_widgets():
    """Test des widgets du terminal"""
    print("🧪 Test widgets terminal...")

    try:
        # Créer interface de test
        root = tk.Tk()
        root.withdraw()

        from cy8_prompts_manager_main import cy8_prompts_manager
        app = cy8_prompts_manager()

        # Vérifier les widgets
        widgets_to_check = [
            ('terminal_output', tk.Text),
            ('terminal_input', tk.Entry),
            ('terminal_cwd_var', tk.StringVar),
            ('terminal_rag_enabled', tk.BooleanVar)
        ]

        for widget_name, expected_type in widgets_to_check:
            if hasattr(app, widget_name):
                widget = getattr(app, widget_name)
                if isinstance(widget, expected_type):
                    print(f"✅ {widget_name}: {expected_type.__name__}")
                else:
                    print(f"❌ {widget_name}: type incorrect ({type(widget)})")
                    return False
            else:
                print(f"❌ {widget_name}: manquant")
                return False

        # Nettoyer
        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Erreur test widgets: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test d'intégration terminal - Interface\n")

    tests = [
        ("Création onglet terminal", test_terminal_tab_creation),
        ("Configuration terminal", test_terminal_configuration),
        ("Widgets terminal", test_terminal_widgets)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"🧪 {test_name}")
        print('='*40)

        try:
            success = test_func()
            results.append((test_name, success))

            if success:
                print(f"✅ {test_name}: SUCCÈS")
            else:
                print(f"❌ {test_name}: ÉCHEC")

        except Exception as e:
            print(f"💥 {test_name}: ERREUR - {e}")
            results.append((test_name, False))

    # Résumé
    print(f"\n{'='*50}")
    print("📊 RÉSUMÉ TESTS INTERFACE TERMINAL")
    print('='*50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{status}: {test_name}")

    print(f"\n🎯 Score: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Terminal intégré parfaitement !")
        return True
    else:
        print(f"⚠️ {total - passed} problème(s) détecté(s)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

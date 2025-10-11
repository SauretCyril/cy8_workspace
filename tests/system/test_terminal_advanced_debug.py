#!/usr/bin/env python3
"""
Diagnostic avancé du terminal - Débuggage complet
Test avec logs détaillés pour identifier où ça bloque
"""

import sys
import os
import time
import threading

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_terminal_with_debug():
    """Test avec debug détaillé du terminal"""
    print("🔍 DIAGNOSTIC AVANCÉ DU TERMINAL")
    print("=" * 50)

    try:
        # Import de l'application
        print("1. Import de l'application...")
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("2. Création d'une instance mock...")

        # Créer une classe de test qui hérite de cy8_prompts_manager
        class TerminalDebugger(cy8_prompts_manager):
            def __init__(self):
                # Initialisation minimale pour le test
                self.terminal_cwd = os.getcwd()
                self.current_process = None
                self.terminal_history = []
                self.terminal_history_index = -1

                # Mock de l'interface
                self.mock_terminal_output = []

            def append_terminal_output(self, text, tag="output"):
                """Version mock qui enregistre au lieu d'afficher"""
                print(f"   📝 OUTPUT: '{text.strip()}' (tag: {tag})")
                self.mock_terminal_output.append((text, tag))

            def root_after_mock(self, delay, func):
                """Mock de root.after qui exécute immédiatement"""
                print(f"   ⏰ AFTER: Exécution de {func}")
                func()

            def test_echo_command(self):
                """Test spécifique de la commande echo"""
                print("\n3. Test de la commande echo...")

                # Remplacer root.after temporairement
                original_after = getattr(self, 'root', None)

                class MockRoot:
                    def after(self, delay, func):
                        print(f"   ⏰ MOCK AFTER: delay={delay}, exécution immédiate")
                        try:
                            func()
                        except Exception as e:
                            print(f"   ❌ ERREUR dans func(): {e}")

                self.root = MockRoot()

                # Tester la fonction
                try:
                    print("   🔧 Exécution de run_command_in_subprocess('echo test')...")
                    self.run_command_in_subprocess("echo test")

                    # Attendre un peu que le thread termine
                    print("   ⏳ Attente de 2 secondes pour le thread...")
                    time.sleep(2)

                    print(f"   📊 Résultats collectés: {len(self.mock_terminal_output)} entrées")
                    for i, (text, tag) in enumerate(self.mock_terminal_output):
                        print(f"      {i+1}. '{text.strip()}' (tag: {tag})")

                    return len(self.mock_terminal_output) > 0

                except Exception as e:
                    print(f"   ❌ ERREUR: {e}")
                    import traceback
                    traceback.print_exc()
                    return False

        # Créer et tester
        debugger = TerminalDebugger()
        success = debugger.test_echo_command()

        print(f"\n✅ Test terminé: {'SUCCÈS' if success else 'ÉCHEC'}")
        return success

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subprocess_direct():
    """Test direct de subprocess pour comparaison"""
    print("\n" + "=" * 50)
    print("🧪 TEST SUBPROCESS DIRECT (pour comparaison)")
    print("=" * 50)

    import subprocess

    try:
        print("Test 1: subprocess.run...")
        result = subprocess.run("echo test", shell=True, capture_output=True, text=True)
        print(f"   stdout: '{result.stdout}'")
        print(f"   stderr: '{result.stderr}'")
        print(f"   returncode: {result.returncode}")

        print("\nTest 2: subprocess.Popen + communicate...")
        process = subprocess.Popen(
            "echo test",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        print(f"   stdout: '{stdout}'")
        print(f"   stderr: '{stderr}'")
        print(f"   returncode: {process.returncode}")

        return True

    except Exception as e:
        print(f"❌ Erreur subprocess: {e}")
        return False

if __name__ == "__main__":
    print("🚀 LANCEMENT DU DIAGNOSTIC AVANCÉ")
    print("Cette version va tracer exactement ce qui se passe")
    print()

    # Test 1: Subprocess direct
    subprocess_ok = test_subprocess_direct()

    # Test 2: Application avec debug
    app_ok = test_terminal_with_debug()

    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    print(f"• Subprocess direct: {'✅ OK' if subprocess_ok else '❌ ÉCHEC'}")
    print(f"• Application terminal: {'✅ OK' if app_ok else '❌ ÉCHEC'}")

    if subprocess_ok and not app_ok:
        print("\n🎯 CONCLUSION: Le problème est dans l'application")
        print("   Les logs ci-dessus montrent où ça bloque.")
    elif not subprocess_ok:
        print("\n🎯 CONCLUSION: Problème système avec subprocess")
    else:
        print("\n🎯 CONCLUSION: Tout fonctionne en test")
        print("   Le problème peut être dans l'interface graphique.")

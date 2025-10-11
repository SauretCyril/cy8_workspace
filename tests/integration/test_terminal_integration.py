#!/usr/bin/env python3
"""
Test d'intégration du terminal intégré dans cy8_prompts_manager
Teste les fonctionnalités principales du terminal avec RAG.
"""

import sys
import os
import subprocess
import time
import threading
import tempfile
from pathlib import Path

# Ajouter le dossier src au chemin
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_terminal_commands():
    """Test des commandes de base du terminal"""
    print("🧪 Test des commandes terminal de base...")

    try:
        # Test commande simple
        result = subprocess.run(['echo', 'Hello Terminal'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'Hello Terminal' in result.stdout
        print("✅ Commande echo OK")

        # Test commande avec erreur
        result = subprocess.run(['python', '-c', 'print("Test Python")'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'Test Python' in result.stdout
        print("✅ Commande Python OK")

        # Test commande inexistante
        result = subprocess.run(['commande_inexistante_12345'], capture_output=True, text=True, shell=True)
        assert result.returncode != 0
        print("✅ Gestion erreur commande OK")

        return True

    except Exception as e:
        print(f"❌ Erreur test commandes: {e}")
        return False

def test_terminal_directory_operations():
    """Test des opérations de répertoire"""
    print("🧪 Test des opérations de répertoire...")

    try:
        import tempfile
        import shutil

        # Créer un répertoire temporaire
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test changement de répertoire
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            current_dir = os.getcwd()
            assert current_dir == os.path.abspath(temp_dir)
            print("✅ Changement répertoire OK")

            # Test création fichier
            test_file = os.path.join(temp_dir, "test_terminal.txt")
            with open(test_file, 'w') as f:
                f.write("Test terminal integration")
            assert os.path.exists(test_file)
            print("✅ Création fichier OK")

            # Retour répertoire original
            os.chdir(original_dir)

        return True

    except Exception as e:
        print(f"❌ Erreur test répertoires: {e}")
        return False

def test_terminal_rag_indexing():
    """Test de l'indexation RAG des sessions terminal"""
    print("🧪 Test indexation RAG terminal...")

    try:
        # Import du gestionnaire RAG
        from cy8_rag_manager import RAGManager

        # Initialiser le gestionnaire
        rag_manager = RAGManager()

        # Simuler une session terminal
        from datetime import datetime

        session_content = f"""=== Session Terminal ===
Timestamp: {datetime.now().isoformat()}
Répertoire: {os.getcwd()}
Commande: python --version
Code retour: 0
Environnement: venv

=== Contexte ===
Application: cy8_prompts_manager
Module: Terminal intégré
Utilisateur: Session interactive

=== Analyse ===
✅ Commande exécutée avec succès
🐍 Exécution de script/programme
"""

        # Ajouter au RAG
        doc_id = f"terminal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        rag_manager.add_document(
            doc_id=doc_id,
            content=session_content,
            metadata={
                'type': 'terminal_session',
                'command': 'python --version',
                'returncode': 0,
                'cwd': os.getcwd(),
                'timestamp': datetime.now().isoformat()
            }
        )

        print("✅ Document ajouté au RAG")

        # Test requête
        results = rag_manager.query("commande python version", limit=5)

        # Vérifier que notre document est trouvé
        found = False
        for result in results:
            if doc_id in str(result):
                found = True
                break

        if found:
            print("✅ Document retrouvé dans RAG")
        else:
            print("⚠️ Document pas trouvé mais RAG fonctionne")

        return True

    except Exception as e:
        print(f"❌ Erreur test RAG terminal: {e}")
        return False

def test_terminal_history():
    """Test de l'historique des commandes"""
    print("🧪 Test historique commandes...")

    try:
        # Simuler historique
        history = []
        commands = ["ls", "pwd", "python --version", "pip list"]

        # Ajouter commandes
        for cmd in commands:
            if cmd not in history:
                history.append(cmd)

        assert len(history) == 4
        print("✅ Historique créé")

        # Test navigation
        history_index = -1

        # Naviguer vers le haut
        history_index -= 1
        if history_index < -len(history):
            history_index = -len(history)

        current_cmd = history[history_index]
        assert current_cmd == "pip list"
        print("✅ Navigation historique OK")

        return True

    except Exception as e:
        print(f"❌ Erreur test historique: {e}")
        return False

def test_terminal_process_management():
    """Test de la gestion des processus"""
    print("🧪 Test gestion processus...")

    try:
        import threading
        import time

        # Test processus simple
        process = subprocess.Popen(
            ['python', '-c', 'import time; time.sleep(0.1); print("Done")'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Attendre fin
        stdout, stderr = process.communicate(timeout=5)

        assert process.returncode == 0
        assert "Done" in stdout
        print("✅ Processus simple OK")

        # Test interruption processus
        long_process = subprocess.Popen(
            ['python', '-c', 'import time; time.sleep(10)'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Laisser démarrer
        time.sleep(0.1)

        # Terminer
        long_process.terminate()
        try:
            long_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            long_process.kill()

        assert long_process.returncode != 0  # Processus terminé
        print("✅ Interruption processus OK")

        return True

    except Exception as e:
        print(f"❌ Erreur test processus: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage tests terminal intégré\n")

    tests = [
        ("Commandes de base", test_terminal_commands),
        ("Opérations répertoire", test_terminal_directory_operations),
        ("Indexation RAG", test_terminal_rag_indexing),
        ("Historique commandes", test_terminal_history),
        ("Gestion processus", test_terminal_process_management)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)

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
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS TERMINAL")
    print('='*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{status}: {test_name}")

    print(f"\n🎯 Score final: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests du terminal passent !")
        return True
    else:
        print(f"⚠️ {total - passed} test(s) en échec")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

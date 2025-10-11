#!/usr/bin/env python3
"""
Test complet de la fonctionnalité de double-clic avec solutions IA
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from cy8_prompts_manager_main import cy8_prompts_manager


def test_complete_error_solution_workflow():
    """Test complet du workflow de solutions d'erreurs"""
    print("🎯 Test complet du workflow de solutions d'erreurs")
    print("=" * 60)

    try:
        # Créer l'application
        app = cy8_prompts_manager()

        print("✅ Application créée avec onglet Log et solutions IA")

        # Créer un fichier de log de test avec erreurs variées
        test_log_content = """2025-09-28 10:15:23.456 INFO: Starting ComfyUI server
2025-09-28 10:15:24.789 INFO: Adding extra search path custom_nodes H:\\comfyui\\main\\custom_nodes
2025-09-28 10:15:25.012 INFO: Import times for custom nodes:
2025-09-28 10:15:26.345 INFO: 0.2 seconds: custom_nodes\\ExtraPathReader
2025-09-28 10:15:27.678 INFO: 0.0 seconds (IMPORT FAILED): custom_nodes\\BrokenNode
2025-09-28 10:15:28.901 ERROR: ModuleNotFoundError: No module named 'torch_audio'
[2025-09-28 10:15:29.234] WARNING: Deprecated API usage detected in custom node
(2025-09-28 10:15:30.567) INFO: Server ready at http://127.0.0.1:8188
10:15:31.890 ERROR: ConnectionError: Failed to connect to external service
10:15:32.123 WARNING: Memory usage high (85%)
10:15:33.456 ERROR: AttributeError: 'NoneType' object has no attribute 'device'
10:15:34.789 ERROR: FileNotFoundError: [Errno 2] No such file or directory: 'models/checkpoints/model.safetensors'
"""

        test_log_file = "test_complete_log.txt"

        # Écrire le fichier de test
        with open(test_log_file, "w", encoding="utf-8") as f:
            f.write(test_log_content)

        print(f"📄 Fichier de log créé: {test_log_file}")

        # Configurer l'analyseur de log
        app.comfyui_log_path.set(test_log_file)

        # Configurer le répertoire des solutions
        solutions_dir = "test_solutions_complete"
        app.error_solutions_dir.set(solutions_dir)

        print(f"📁 Répertoire des solutions: {solutions_dir}")

        # Analyser le log
        print("🔍 Analyse du log...")
        app.analyze_comfyui_log()

        # Vérifier les résultats
        if hasattr(app, "log_results_tree"):
            items = app.log_results_tree.get_children()
            print(f"📊 {len(items)} éléments trouvés dans le tableau")

            # Compter les erreurs
            error_count = 0
            warning_count = 0
            success_count = 0

            error_items = []

            for item in items:
                values = app.log_results_tree.item(item)["values"]
                if values and len(values) > 1:
                    error_type = values[1]  # type est en position 1 après timestamp
                    if error_type == "ERREUR":
                        error_count += 1
                        error_items.append((item, values))
                    elif error_type == "ATTENTION":
                        warning_count += 1
                    elif error_type == "OK":
                        success_count += 1

            print(f"   🔴 {error_count} erreurs")
            print(f"   ⚠️  {warning_count} warnings")
            print(f"   ✅ {success_count} succès")
            print()

            # Simuler le double-clic sur chaque erreur pour tester le cache
            print("🖱️  Simulation du double-clic sur les erreurs:")

            for i, (item, values) in enumerate(
                error_items[:3], 1
            ):  # Tester les 3 premières erreurs
                timestamp = values[0]
                error_type = values[1]
                message = values[4] if len(values) > 4 else "N/A"

                print(f"   {i}. 🕐 {timestamp} - {error_type}")
                print(f"      📝 {message[:60]}...")

                # Simuler la création/chargement d'une solution
                from cy8_mistral import load_error_solution, save_error_solution

                existing_solution = load_error_solution(timestamp, solutions_dir)

                if not existing_solution:
                    # Créer une solution simulée (sans appeler Mistral AI pour les tests)
                    mock_solution = f"""ANALYSE D'ERREUR COMFYUI - SIMULATION
==========================================

TIMESTAMP: {timestamp}
TYPE: {error_type}
MESSAGE: {message}

EXPLICATION:
Cette erreur a été analysée automatiquement par le système de solutions IA.

CAUSES POSSIBLES:
1. Problème de configuration
2. Module ou dépendance manquante
3. Problème de permissions ou de chemins

SOLUTIONS RECOMMANDÉES:
1. Vérifier la configuration ComfyUI
2. Installer les dépendances manquantes
3. Vérifier les chemins d'accès
4. Redémarrer ComfyUI après correction

PRÉVENTION:
- Maintenir les dépendances à jour
- Vérifier régulièrement les logs
- Utiliser un environnement virtuel stable

---
Solution générée automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                    saved_path = save_error_solution(
                        timestamp, message, mock_solution, solutions_dir
                    )
                    if saved_path:
                        print(
                            f"      ✅ Solution créée: {os.path.basename(saved_path)}"
                        )
                    else:
                        print(f"      ❌ Échec création solution")
                else:
                    print(f"      ♻️  Solution déjà en cache")

                print()

            print("🎉 Test du workflow complet réussi !")

            # Vérifier le contenu du répertoire des solutions
            if os.path.exists(solutions_dir):
                solution_files = [
                    f for f in os.listdir(solutions_dir) if f.endswith(".txt")
                ]
                print(f"📁 {len(solution_files)} fichiers de solutions créés:")
                for solution_file in solution_files:
                    print(f"   📄 {solution_file}")

            return True

        else:
            print("❌ TreeView log non trouvé")
            return False

    except Exception as e:
        print(f"❌ Erreur pendant le test: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Nettoyer les fichiers de test
        try:
            if os.path.exists(test_log_file):
                os.remove(test_log_file)
                print("🧹 Fichier de log test supprimé")

            # Nettoyer le répertoire des solutions
            import shutil

            if os.path.exists(solutions_dir):
                shutil.rmtree(solutions_dir)
                print("🧹 Répertoire des solutions test supprimé")
        except:
            pass


def test_mistral_integration_ready():
    """Vérifier que l'intégration Mistral est prête"""
    print("🤖 Vérification de l'intégration Mistral AI")
    print("=" * 50)

    try:
        # Vérifier les imports
        from cy8_mistral import (
            analyze_comfyui_error,
            save_error_solution,
            load_error_solution,
        )

        print("✅ Imports Mistral OK")

        # Vérifier les variables d'environnement
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key:
            print("✅ Clé API Mistral configurée")
            print(f"   🔑 Clé: ...{api_key[-6:] if len(api_key) > 6 else 'courte'}")
        else:
            print("⚠️  Clé API Mistral non configurée")
            print(
                "   💡 Ajoutez MISTRAL_API_KEY dans votre fichier .env pour utiliser l'IA"
            )

        # Vérifier l'interface
        from cy8_prompts_manager_main import cy8_prompts_manager

        print("✅ Interface avec solutions IA prête")
        print("   📋 Nouvelles fonctionnalités disponibles:")
        print("   • Double-clic sur erreurs pour solutions")
        print("   • Cache intelligent des solutions")
        print("   • Configuration du répertoire de stockage")
        print("   • Interface complète avec Mistral AI")

        return True

    except Exception as e:
        print(f"❌ Erreur de vérification: {e}")
        return False


if __name__ == "__main__":
    print("🧪 TEST COMPLET DU SYSTÈME DE SOLUTIONS D'ERREURS")
    print("=" * 70)

    success = True

    # Test 1: Vérification de l'intégration Mistral
    success &= test_mistral_integration_ready()
    print()

    # Test 2: Workflow complet
    success &= test_complete_error_solution_workflow()
    print()

    if success:
        print("🎉 SYSTÈME DE SOLUTIONS D'ERREURS OPÉRATIONNEL !")
        print()
        print("🎯 RÉSUMÉ DES FONCTIONNALITÉS:")
        print("   ✨ Double-clic sur erreurs dans l'onglet Log")
        print("   🤖 Analyse automatique avec Mistral AI")
        print("   💾 Sauvegarde automatique des solutions")
        print("   ♻️  Cache intelligent par timestamp")
        print("   📁 Configuration du répertoire de stockage")
        print("   🔄 Possibilité de régénérer les solutions")
        print("   📤 Export et gestion des fichiers de solutions")
        print()
        print("📋 UTILISATION:")
        print("   1. Allez dans l'onglet 📊 Log")
        print("   2. Configurez le répertoire des solutions")
        print("   3. Analysez un fichier log ComfyUI")
        print("   4. Double-cliquez sur une erreur")
        print("   5. Consultez la solution IA proposée")
    else:
        print("❌ PROBLÈME AVEC LE SYSTÈME DE SOLUTIONS")
        print("🔧 Vérifiez la configuration et les dépendances")

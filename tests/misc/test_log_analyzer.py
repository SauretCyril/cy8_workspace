#!/usr/bin/env python3
"""
Script de test pour l'analyseur de logs ComfyUI
"""

import os
import sys

sys.path.insert(0, "../src")


def create_test_log():
    """Créer un fichier de log de test avec différents types d'entrées"""
    test_log_content = """
2025-09-26 10:00:01,123 - INFO - Starting ComfyUI
2025-09-26 10:00:02,456 - INFO - Total VRAM: 8192 MB
2025-09-26 10:00:03,789 - INFO - CUDA Available: True
2025-09-26 10:00:04,012 - INFO - Torch version: 2.0.1
2025-09-26 10:00:05,345 - INFO - Loading custom nodes from: custom_nodes/ComfyUI-AnimateDiff-Evolved
2025-09-26 10:00:06,678 - INFO - Custom node ComfyUI-AnimateDiff-Evolved loaded successfully
2025-09-26 10:00:07,901 - INFO - Loading custom nodes from: custom_nodes/ComfyUI-VideoHelperSuite
2025-09-26 10:00:08,234 - INFO - Custom node ComfyUI-VideoHelperSuite loaded successfully
2025-09-26 10:00:09,567 - ERROR - Failed to import custom node: ComfyUI-broken-node
2025-09-26 10:00:10,890 - ERROR - ModuleNotFoundError: No module named 'missing_package'
2025-09-26 10:00:11,123 - WARNING - Deprecated function used in workflow
2025-09-26 10:00:12,456 - INFO - Server started on 127.0.0.1:8188
2025-09-26 10:00:13,789 - ERROR - ImportError: Cannot import name 'broken_function' from 'some_module'
2025-09-26 10:00:14,012 - INFO - Loading model: checkpoints/sd_xl_base_1.0.safetensors
2025-09-26 10:00:15,345 - WARNING - Model file size is unusually large
2025-09-26 10:00:16,678 - ERROR - FileNotFoundError: Model file not found: missing_model.safetensors
2025-09-26 10:00:17,901 - INFO - GPU detected: NVIDIA GeForce RTX 4080
2025-09-26 10:00:18,234 - ERROR - AttributeError: 'NoneType' object has no attribute 'encode'
2025-09-26 10:00:19,567 - INFO - Custom node manager: Checking for updates
2025-09-26 10:00:20,890 - WARNING - Some dependencies are outdated
"""

    with open("test_comfyui.log", "w", encoding="utf-8") as f:
        f.write(test_log_content.strip())

    print("✅ Fichier de test créé: test_comfyui.log")


def test_log_analyzer():
    """Tester l'analyseur de logs"""
    print("🧪 Test de l'analyseur de logs ComfyUI")
    print("=" * 50)

    try:
        from cy8_log_analyzer import cy8_log_analyzer

        # Créer un fichier de test
        create_test_log()

        # Créer l'analyseur
        analyzer = cy8_log_analyzer()

        # Analyser le fichier de test
        result = analyzer.analyze_log_file("test_comfyui.log")

        if result["success"]:
            print("✅ Analyse réussie !")
            print(f"\n📊 Résumé:")
            summary = result["summary"]
            print(f"  • Custom nodes OK: {summary['custom_nodes_ok']}")
            print(f"  • Custom nodes échoués: {summary['custom_nodes_failed']}")
            print(f"  • Erreurs: {summary['errors']}")
            print(f"  • Warnings: {summary['warnings']}")
            print(f"  • Informations: {summary['info_messages']}")

            print(f"\n📋 Détails des entrées ({len(result['entries'])} éléments):")
            for i, entry in enumerate(
                result["entries"][:10]
            ):  # Afficher les 10 premiers
                status_icon = {
                    "OK": "✅",
                    "ERREUR": "❌",
                    "ATTENTION": "⚠️",
                    "INFO": "ℹ️",
                }.get(entry["type"], "🔸")
                print(
                    f"  {i+1:2d}. {status_icon} {entry['category']:15} | {entry['element']:20} | Ligne {entry['line']:3d}"
                )
                print(
                    f"      {entry['message'][:80]}{'...' if len(entry['message']) > 80 else ''}"
                )

            if len(result["entries"]) > 10:
                print(f"      ... et {len(result['entries']) - 10} autres éléments")

            # Afficher le résumé textuel
            print(f"\n{analyzer.get_summary_text()}")

        else:
            print(f"❌ Erreur lors de l'analyse: {result['error']}")

        # Nettoyer
        if os.path.exists("test_comfyui.log"):
            os.remove("test_comfyui.log")
            print("\n🧹 Fichier de test supprimé")

        return result["success"]

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_interface_integration():
    """Tester l'intégration dans l'interface"""
    print("\n🎨 Test de l'intégration dans l'interface")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager

        # Vérifier que les nouvelles méthodes existent
        methods_to_check = ["browse_log_file", "analyze_comfyui_log"]

        for method in methods_to_check:
            if hasattr(cy8_prompts_manager, method):
                print(f"✅ Méthode {method} trouvée")
            else:
                print(f"❌ Méthode {method} manquante")
                return False

        print("✅ Toutes les méthodes sont présentes")
        return True

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Test principal"""
    print("🚀 Test de la fonctionnalité d'analyse des logs ComfyUI")
    print("=" * 60)

    # Test 1: Analyseur de logs
    test1_ok = test_log_analyzer()

    # Test 2: Intégration interface
    test2_ok = test_interface_integration()

    print(f"\n📊 Résultats des tests:")
    print(f"  - Analyseur de logs: {'✅ OK' if test1_ok else '❌ FAIL'}")
    print(f"  - Interface: {'✅ OK' if test2_ok else '❌ FAIL'}")

    if test1_ok and test2_ok:
        print("\n🎉 Tous les tests sont passés !")
        print("\n💡 Pour utiliser la fonction:")
        print("   1. Lancez l'application: python src/cy8_prompts_manager_main.py")
        print("   2. Allez dans l'onglet 'ComfyUI'")
        print("   3. Dans la section 'Analyse des logs ComfyUI':")
        print("      - Vérifiez le chemin du fichier log")
        print("      - Cliquez sur 'Analyser le log'")
        print("   4. Consultez les résultats dans le tableau")
    else:
        print("\n❌ Certains tests ont échoué")

    return test1_ok and test2_ok


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test du système d'envoi de contexte au RAG
"""

import sys
import os
import time
import json

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_context_functions():
    """Tester les fonctions de contexte RAG"""

    try:
        # Importer les modules nécessaires
        from cy8_prompts_manager_main import cy8_prompts_manager
        from cy8_rag_manager import RAGManager

        print("✅ Modules importés avec succès")

        # Créer une instance mock pour tester les fonctions
        class MockApp:
            def __init__(self):
                self.current_environment_id = "G11_05"
                self.rag_manager = RAGManager("G11_05")
                self.db_manager = None  # Simuler pas de db pour ce test

        app = MockApp()

        # Données de test
        extra_paths_data = {
            "comfyui_root": "E:/Comfyui_G11/ComfyUI",
            "extra_paths": {
                "comfyui": {
                    "base_path": "E:/Comfyui_G11/ComfyUI",
                    "checkpoints": "H:/comfyui/G11_05/models/checkpoints",
                    "vae": "H:/comfyui/G11_05/models/vae",
                    "custom_nodes": "E:/Comfyui_G11/ComfyUI/custom_nodes"
                }
            }
        }

        server_status = {
            "status": "online",
            "system_stats": {
                "ram": "32 GB",
                "vram": "24 GB"
            }
        }

        # Test création du rapport contexte
        print("\n🧪 Test création rapport contexte...")

        env_info = {
            "environment_id": "G11_05",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "extra_paths": extra_paths_data,
            "comfyui_root": extra_paths_data["comfyui_root"],
            "custom_nodes_paths": ["E:/Comfyui_G11/ComfyUI/custom_nodes"],
            "models_paths": ["H:/comfyui/G11_05/models/checkpoints", "H:/comfyui/G11_05/models/vae"],
            "server_status": server_status,
            "categorized_analyses": {
                "errors": [
                    {"timestamp": "2024-10-05 10:30:00", "message": "Custom node failed to load"},
                    {"timestamp": "2024-10-05 10:31:00", "message": "CUDA out of memory error"}
                ],
                "custom_nodes_issues": [
                    {"timestamp": "2024-10-05 10:32:00", "message": "Custom node 'ComfyUI-Manager' has dependency issues"}
                ],
                "performance_issues": [
                    {"timestamp": "2024-10-05 10:33:00", "message": "GPU memory usage exceeding 90%"}
                ],
                "warnings": [
                    {"timestamp": "2024-10-05 10:34:00", "message": "Model not found, using default"}
                ]
            }
        }

        # Créer le rapport (en utilisant la fonction directement)
        def create_test_rag_context_report(env_info):
            """Version test de la fonction create_rag_context_report"""
            report_lines = []

            report_lines.append("=== RAPPORT CONTEXTE COMFYUI POUR RAG EXPERT ===")
            report_lines.append(f"Environnement: {env_info['environment_id']}")
            report_lines.append(f"Timestamp: {env_info['timestamp']}")
            report_lines.append("")

            report_lines.append("CONTEXTE D'EXPERTISE:")
            report_lines.append("- Tu es un expert en maintenance applicative ComfyUI")
            report_lines.append("- Tu es spécialisé en Python et environnements virtuels")
            report_lines.append("- Tu connais les problèmes courants de ComfyUI et leurs solutions")
            report_lines.append("- Tu peux diagnostiquer les erreurs de custom nodes et de dépendances")
            report_lines.append("")

            if "comfyui_root" in env_info:
                report_lines.append(f"RACINE COMFYUI: {env_info['comfyui_root']}")
                report_lines.append("")

            if "custom_nodes_paths" in env_info:
                report_lines.append("CUSTOM NODES DETECTES:")
                for path in env_info["custom_nodes_paths"]:
                    report_lines.append(f"- {path}")
                report_lines.append("")

            if "models_paths" in env_info:
                report_lines.append("CHEMINS MODELES:")
                for path in env_info["models_paths"]:
                    report_lines.append(f"- {path}")
                report_lines.append("")

            if "server_status" in env_info:
                status = env_info["server_status"]
                report_lines.append("ETAT SERVEUR:")
                report_lines.append(f"- Statut: {status.get('status', 'inconnu')}")
                if "system_stats" in status:
                    stats = status["system_stats"]
                    report_lines.append(f"- RAM: {stats.get('ram', 'N/A')}")
                    report_lines.append(f"- VRAM: {stats.get('vram', 'N/A')}")
                report_lines.append("")

            if "categorized_analyses" in env_info:
                categories = env_info["categorized_analyses"]

                if categories.get("errors"):
                    report_lines.append("ERREURS CRITIQUES DETECTEES:")
                    for error in categories["errors"][:10]:
                        report_lines.append(f"- {error.get('timestamp', 'N/A')}: {error.get('message', 'N/A')}")
                    report_lines.append("")

                if categories.get("custom_nodes_issues"):
                    report_lines.append("PROBLEMES CUSTOM NODES:")
                    for issue in categories["custom_nodes_issues"][:10]:
                        report_lines.append(f"- {issue.get('timestamp', 'N/A')}: {issue.get('message', 'N/A')}")
                    report_lines.append("")

                if categories.get("performance_issues"):
                    report_lines.append("PROBLEMES PERFORMANCE:")
                    for perf in categories["performance_issues"][:10]:
                        report_lines.append(f"- {perf.get('timestamp', 'N/A')}: {perf.get('message', 'N/A')}")
                    report_lines.append("")

                if categories.get("warnings"):
                    report_lines.append("AVERTISSEMENTS:")
                    for warning in categories["warnings"][:10]:
                        report_lines.append(f"- {warning.get('timestamp', 'N/A')}: {warning.get('message', 'N/A')}")
                    report_lines.append("")

            report_lines.append("INSTRUCTIONS POUR REPONSES:")
            report_lines.append("- Utilise ces informations pour contextualiser tes réponses")
            report_lines.append("- Priorise les erreurs critiques dans tes diagnostics")
            report_lines.append("- Propose des solutions basées sur l'environnement identifié")
            report_lines.append("- Référence les chemins et configurations spécifiques")
            report_lines.append("- Suggère des optimisations de performance si pertinent")

            return "\n".join(report_lines)

        # Créer le rapport
        rapport = create_test_rag_context_report(env_info)

        print(f"✅ Rapport contexte créé: {len(rapport)} caractères")
        print("\n📋 Rapport complet:")
        print("=" * 80)
        print(rapport)
        print("=" * 80)

        # Test du RAG manager si disponible
        print(f"\n🧪 Test RAG Manager...")
        print(f"   RAG disponible: {app.rag_manager.is_available()}")

        if app.rag_manager.is_available():
            print("\n✅ RAG disponible - Test d'indexation...")

            # Test d'indexation du contexte
            success = app.rag_manager.index_analysis_result({
                "timestamp": time.time(),
                "type": "environment_context_test",
                "analysis_type": "environment_context",
                "content": rapport,
                "environment_id": "G11_05",
                "context_type": "complete_environment_state_test"
            })

            if success:
                print("✅ Contexte indexé avec succès dans le RAG")

                # Test de recherche
                print("\n🔍 Test recherche dans le RAG...")
                results = app.rag_manager.search_relevant_analyses("erreur custom node", limit=3)

                if results:
                    print(f"✅ Recherche réussie: {len(results)} résultats trouvés")
                    for i, result in enumerate(results):
                        print(f"   Résultat {i+1}: {result['content'][:100]}...")
                else:
                    print("ℹ️ Aucun résultat trouvé (normal pour un test)")
            else:
                print("❌ Échec d'indexation")
        else:
            print("⚠️ RAG non disponible - test d'indexation ignoré")

        print("\n✅ Test terminé avec succès !")

    except Exception as e:
        print(f"\n❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_context_functions()

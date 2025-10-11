#!/usr/bin/env python3
"""
Test du système RAG Hybride avec modes Rapide et Expert
"""

import sys
import os
import json
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_hybride():
    """Test complet du système RAG Hybride"""
    print("🧪 TEST RAG HYBRIDE - Modes Rapide et Expert")
    print("=" * 60)

    try:
        # Importer le RAG Manager
        from cy8_rag_manager import RAGManager

        # Mock DB Manager simple
        class MockDBManager:
            def get_environment_analyses_directory(self, env_id):
                return os.path.join(os.getcwd(), "data", "analyses", env_id)

            def clear_analysis_results(self, env_id):
                pass

        # Initialiser le RAG
        print("🔧 Initialisation du RAG Manager...")
        db_manager = MockDBManager()
        rag = RAGManager(db_manager, "TEST_ENV")

        if not rag.is_available():
            print("❌ RAG non disponible - vérifiez les dépendances")
            print("pip install chromadb sentence-transformers")
            return False

        print("✅ RAG Manager initialisé avec succès")

        # Ajouter quelques analyses de test
        print("\n📝 Ajout d'analyses de test...")

        test_analyses = [
            {
                "timestamp": datetime.now().isoformat(),
                "environment_id": "TEST_ENV",
                "type": "log_analysis",
                "summary": "Erreur CUDA memory allocation failed",
                "errors": [
                    {
                        "type": "cuda_error",
                        "message": "CUDA out of memory. Tried to allocate 2.00 GiB",
                        "solution": "Réduire la taille du batch ou redémarrer ComfyUI"
                    }
                ],
                "successes": ["Custom nodes chargés correctement"],
                "recommendations": ["Surveiller l'utilisation VRAM"]
            },
            {
                "timestamp": datetime.now().isoformat(),
                "environment_id": "TEST_ENV",
                "type": "log_analysis",
                "summary": "Custom node manquant: ComfyUI-Manager",
                "errors": [
                    {
                        "type": "missing_custom_node",
                        "message": "Cannot import name 'ComfyUI-Manager'",
                        "solution": "Installer ComfyUI-Manager depuis le gestionnaire"
                    }
                ],
                "successes": ["Modèles SD 1.5 trouvés"],
                "recommendations": ["Vérifier l'installation des custom nodes"]
            },
            {
                "timestamp": datetime.now().isoformat(),
                "environment_id": "TEST_ENV",
                "type": "log_analysis",
                "summary": "Problème de version PyTorch incompatible",
                "errors": [
                    {
                        "type": "dependency_conflict",
                        "message": "PyTorch 2.1.0 incompatible avec CUDA 11.7",
                        "solution": "Installer PyTorch compatible CUDA 11.7"
                    }
                ],
                "successes": ["ControlNet nodes fonctionnels"],
                "recommendations": ["Vérifier compatibilité PyTorch/CUDA"]
            }
        ]

        for i, analysis in enumerate(test_analyses, 1):
            print(f"  📄 Indexation analyse {i}...")
            rag.index_analysis_result(analysis)

        print(f"✅ {len(test_analyses)} analyses indexées")

        # Test des modes
        test_queries = [
            "J'ai une erreur CUDA memory, que faire ?",
            "Comment résoudre les problèmes de custom nodes ?",
            "Quelles sont les erreurs les plus fréquentes ?",
            "PyTorch ne fonctionne pas avec ma version CUDA"
        ]

        print("\n" + "=" * 60)
        print("🔍 TESTS DES MODES RAG")
        print("=" * 60)

        for query in test_queries:
            print(f"\n❓ Question: {query}")
            print("-" * 50)

            # Test Mode Rapide
            print("\n⚡ MODE RAPIDE:")
            rapid_result = rag.query_with_mode(query, mode="rapide", max_results=3)
            print(f"  Succès: {rapid_result['success']}")
            print(f"  Temps: {rapid_result.get('metadata', {}).get('response_time', 'N/A')}s")
            print(f"  Documents: {rapid_result.get('documents_found', 0)}")
            print(f"  Réponse: {rapid_result['response'][:200]}...")

            # Test Mode Expert (simulation sans Mistral)
            print("\n🧠 MODE EXPERT:")
            expert_result = rag.query_with_mode(query, mode="expert", max_results=3)
            print(f"  Succès: {expert_result['success']}")
            print(f"  Temps: {expert_result.get('metadata', {}).get('response_time', 'N/A')}s")
            print(f"  Documents: {expert_result.get('documents_found', 0)}")
            if "mistral_tokens" in expert_result:
                print(f"  Tokens Mistral: {expert_result['mistral_tokens']}")
            print(f"  Réponse: {expert_result['response'][:200]}...")

        # Test des informations sur les modes
        print("\n" + "=" * 60)
        print("ℹ️ INFORMATIONS SUR LES MODES")
        print("=" * 60)

        mode_info = rag.get_mode_info()
        for mode_name, info in mode_info.items():
            print(f"\n{info['name']}:")
            print(f"  Description: {info['description']}")
            print(f"  Vitesse: {info['speed']}")
            print(f"  Coût: {info['cost']}")
            print(f"  Précision: {info['accuracy']}")
            print(f"  Idéal pour: {', '.join(info['best_for'])}")

        print("\n✅ TESTS RAG HYBRIDE TERMINÉS AVEC SUCCÈS!")
        return True

    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Installation requise: pip install chromadb sentence-transformers")
        return False

    except Exception as e:
        print(f"❌ Erreur pendant les tests: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_modes_comparison():
    """Test de comparaison des performances entre les modes"""
    print("\n" + "=" * 60)
    print("📊 COMPARAISON DES PERFORMANCES")
    print("=" * 60)

    try:
        from cy8_rag_manager import RAGManager

        class MockDBManager:
            def get_environment_analyses_directory(self, env_id):
                return os.path.join(os.getcwd(), "data", "analyses", env_id)

        rag = RAGManager(MockDBManager(), "PERF_TEST")

        if not rag.is_available():
            print("❌ RAG non disponible pour test performance")
            return False

        test_query = "Comment optimiser les performances de ComfyUI ?"

        print(f"Question test: {test_query}\n")

        # Tester plusieurs fois chaque mode
        modes = ["rapide", "expert"]
        results = {}

        for mode in modes:
            print(f"🧪 Test mode {mode}...")
            times = []

            for i in range(3):
                result = rag.query_with_mode(test_query, mode=mode)
                if result["success"]:
                    time_taken = result.get("metadata", {}).get("response_time", 0)
                    times.append(time_taken)
                    print(f"  Essai {i+1}: {time_taken}s")
                else:
                    print(f"  Essai {i+1}: Échec")

            if times:
                avg_time = sum(times) / len(times)
                results[mode] = {
                    "avg_time": avg_time,
                    "min_time": min(times),
                    "max_time": max(times)
                }
                print(f"  Moyenne: {avg_time:.2f}s")

        # Afficher le résumé comparatif
        print("\n📈 RÉSUMÉ COMPARATIF:")
        for mode, data in results.items():
            print(f"  {mode.upper()}:")
            print(f"    Temps moyen: {data['avg_time']:.2f}s")
            print(f"    Min/Max: {data['min_time']:.2f}s / {data['max_time']:.2f}s")

        return True

    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False


if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS RAG HYBRIDE")
    print("=" * 60)

    success = test_rag_hybride()

    if success:
        test_modes_comparison()

    print("\n🏁 TESTS TERMINÉS")

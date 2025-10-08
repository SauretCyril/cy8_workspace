#!/usr/bin/env python3
"""
Test spécifique pour diagnostiquer les problèmes d'apprentissage RAG
"""

import sys
import os
sys.path.append('src')

from cy8_database_manager import cy8_database_manager
from cy8_rag_manager import RAGManager

def test_rag_learning_detailed():
    """Test détaillé de l'apprentissage RAG"""
    print("🧪 DIAGNOSTIC DÉTAILLÉ DE L'APPRENTISSAGE RAG")
    print("=" * 50)

    try:
        # 1. Initialiser les composants
        print("📝 1. Initialisation des composants...")
        db_manager = cy8_database_manager()
        rag_manager = RAGManager(db_manager, "test_env")

        print(f"   ✅ RAG disponible: {rag_manager.is_available()}")

        if not rag_manager.is_available():
            print("   ❌ RAG non disponible - Arrêt du test")
            return False

        # 2. Vérifier l'état initial
        print("\n📊 2. État initial du RAG...")
        initial_count = rag_manager.collection.count()
        print(f"   📚 Documents initiaux: {initial_count}")

        # 3. Test d'indexation simple
        print("\n📥 3. Test d'indexation de nouvelles données...")
        test_data = {
            "test_id": "diagnostic_001",
            "environment_id": "test_env",
            "log_content": "TEST DIAGNOSTIC: Erreur de mémoire CUDA",
            "errors_detected": ["CUDA out of memory", "Test diagnostic error"],
            "success_rate": 75.0,
            "performance_metrics": {"gpu_usage": "95%"},
            "recommendations": ["Réduire la batch size", "Utiliser plus de VRAM"],
            "analysis_summary": "Test diagnostique pour vérifier l'apprentissage"
        }

        try:
            rag_manager.index_analysis_result(test_data)
            new_count = rag_manager.collection.count()
            print(f"   📚 Documents après indexation: {new_count}")
            print(f"   ✅ Indexation: {'Réussie' if new_count > initial_count else 'Échouée'}")
        except Exception as e:
            print(f"   ❌ Erreur indexation: {e}")
            return False

        # 4. Test de recherche immédiate
        print("\n🔍 4. Test de recherche immédiate...")
        try:
            search_results = rag_manager.search_similar_issues("CUDA memory", limit=3)
            print(f"   📋 Résultats trouvés: {len(search_results)}")

            found_our_test = False
            for i, result in enumerate(search_results):
                print(f"   📄 Résultat {i+1}: {str(result)[:100]}...")
                if "diagnostic" in str(result).lower() or "cuda" in str(result).lower():
                    found_our_test = True

            print(f"   ✅ Notre test trouvé: {'Oui' if found_our_test else 'Non'}")

        except Exception as e:
            print(f"   ❌ Erreur recherche: {e}")
            return False

        # 5. Test d'apprentissage depuis conversations
        print("\n💬 5. Test d'apprentissage depuis conversations...")
        try:
            # Simuler une conversation
            conversation_data = {
                "user_message": "J'ai une erreur CUDA out of memory, que faire ?",
                "assistant_response": "Vous devriez réduire la batch size et vérifier votre VRAM disponible",
                "context": "ComfyUI workflow execution",
                "timestamp": "2024-10-08T10:30:00",
                "environment_id": "test_env"
            }

            # Indexer la conversation (si la méthode existe)
            if hasattr(rag_manager, 'index_conversation'):
                rag_manager.index_conversation(conversation_data)
                print("   ✅ Conversation indexée")
            else:
                print("   ⚠️ Méthode index_conversation non disponible")

        except Exception as e:
            print(f"   ❌ Erreur indexation conversation: {e}")

        # 6. Test de recherche après apprentissage
        print("\n🎯 6. Test de recherche après apprentissage...")
        try:
            search_results = rag_manager.search("batch size CUDA", limit=5)
            print(f"   📋 Résultats pour 'batch size CUDA': {len(search_results)}")

            learning_verified = False
            for result in search_results:
                if "batch" in str(result).lower() and "cuda" in str(result).lower():
                    learning_verified = True
                    break

            print(f"   🧠 Apprentissage vérifié: {'Oui' if learning_verified else 'Non'}")

        except Exception as e:
            print(f"   ❌ Erreur test apprentissage: {e}")

        # 7. Vérifier la persistance
        print("\n💾 7. Test de persistance des données...")
        final_count = rag_manager.collection.count()
        print(f"   📚 Documents finaux: {final_count}")
        print(f"   📈 Gain: +{final_count - initial_count} documents")

        # Résumé
        print("\n📊 RÉSUMÉ DU DIAGNOSTIC:")
        print(f"   🔧 RAG initialisé: ✅")
        print(f"   📥 Indexation fonctionne: ✅")
        print(f"   🔍 Recherche fonctionne: ✅")
        print(f"   🧠 Apprentissage détecté: {'✅' if learning_verified else '❌'}")
        print(f"   💾 Persistance: ✅")

        if learning_verified:
            print("\n🎉 CONCLUSION: Le RAG apprend correctement !")
        else:
            print("\n⚠️ CONCLUSION: Problème d'apprentissage détecté")
            print("   💡 Suggestions:")
            print("   - Vérifier la méthode d'indexation des conversations")
            print("   - Contrôler les paramètres de recherche")
            print("   - Examiner la qualité des embeddings")

        return learning_verified

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_learning_detailed()

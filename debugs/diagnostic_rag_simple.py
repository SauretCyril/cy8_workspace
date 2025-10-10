#!/usr/bin/env python3
"""
Test de diagnostic du RAG Manager
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_rag_manager import RAGManager

def test_rag_initialization():
    """Test d'initialisation du RAG"""
    print("🧪 === TEST DIAGNOSTIC RAG ===")

    try:
        # Initialiser le gestionnaire de base de données
        print("1. Initialisation cy8_database_manager...")
        db_manager = cy8_database_manager("data/prompts.db")
        print("   ✅ cy8_database_manager créé")

        # IMPORTANT: Initialiser la base de données pour que cursor soit défini
        print("   📦 Initialisation de la base de données...")
        db_manager.init_database("dev")  # Mode dev pour créer si nécessaire
        print("   ✅ Base de données initialisée")

        # Initialiser le RAG Manager
        print("2. Initialisation RAGManager...")
        rag_manager = RAGManager(db_manager, environment_id="test_env")
        print("   ✅ RAGManager créé")

        # Vérifier les composants
        print("3. Vérification des composants...")
        print(f"   - ChromaDB client: {rag_manager.chroma_client is not None}")
        print(f"   - Collection: {rag_manager.collection is not None}")
        print(f"   - Modèle embeddings: {rag_manager.embeddings_model is not None}")
        print(f"   - Environment ID: {rag_manager.environment_id}")

        # Test is_available
        print("4. Test is_available()...")
        available = rag_manager.is_available()
        print(f"   - RAG disponible: {available}")

        if not available:
            print("   ❌ RAG non disponible - analysing...")

            # Analyser les causes
            from cy8_rag_manager import CHROMADB_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE
            print(f"   - CHROMADB_AVAILABLE: {CHROMADB_AVAILABLE}")
            print(f"   - SENTENCE_TRANSFORMERS_AVAILABLE: {SENTENCE_TRANSFORMERS_AVAILABLE}")

            if rag_manager.collection is None:
                print("   ❌ Collection est None")
            if rag_manager.embeddings_model is None:
                print("   ❌ Modèle d'embeddings est None")

        # Test de base si disponible
        if available:
            print("5. Test d'indexation...")
            test_data = {
                "test_id": "diagnostic_test",
                "environment_id": "test_env",
                "log_content": "Test diagnostic RAG",
                "analysis_summary": "Test de diagnostic"
            }

            try:
                initial_count = rag_manager.collection.count()
                rag_manager.index_analysis_result(test_data)
                new_count = rag_manager.collection.count()
                print(f"   ✅ Indexation: {initial_count} -> {new_count}")

                # Test de recherche
                print("6. Test de recherche...")
                results = rag_manager.search_similar_issues("diagnostic", limit=3)
                print(f"   ✅ Recherche: {len(results)} résultats")

                for i, result in enumerate(results[:2]):
                    print(f"   - Résultat {i+1}: {result.get('content', '')[:50]}...")

            except Exception as e:
                print(f"   ❌ Erreur lors des tests: {e}")
                import traceback
                traceback.print_exc()

        print("\n🏁 Test terminé")
        return available

    except Exception as e:
        print(f"❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_initialization()

#!/usr/bin/env python3
"""
Test du système RAG pour la recherche PyTorch/CUDA
"""

import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_pytorch_search():
    """Test du système RAG pour les informations PyTorch/CUDA"""

    print("🔍 TEST RAG SYSTÈME - PYTORCH/CUDA")
    print("=" * 60)

    try:
        # Import du gestionnaire RAG
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser les gestionnaires
        db_manager = cy8_database_manager()
        rag_manager = RAGManager(db_manager, "G11_05")

        print(f"✅ RAG Manager initialisé pour G11_05")

        # Test de différentes requêtes
        test_queries = [
            "pytorch version",
            "version pytorch",
            "cuda version",
            "version cuda",
            "torch version",
            "pytorch cuda",
            "modules pytorch cuda",
            "peux tu m'indiquer les versions des modules pytroch.. cuda",
            "VRAM",
            "memory",
            "gpu"
        ]

        print(f"\n🔍 **TEST RECHERCHES RAG:**")

        for query in test_queries:
            print(f"\n📝 Requête: '{query}'")

            try:
                # Rechercher des analyses similaires
                if hasattr(rag_manager, 'search_similar_issues'):
                    results = rag_manager.search_similar_issues(query, limit=3)
                elif hasattr(rag_manager, 'search_relevant_analyses'):
                    results = rag_manager.search_relevant_analyses(query, limit=3)
                else:
                    print("   ❌ Méthode de recherche non trouvée")
                    continue

                if results:
                    print(f"   ✅ {len(results)} résultat(s) trouvé(s):")
                    for i, result in enumerate(results):
                        if isinstance(result, dict):
                            content = result.get('content', str(result))[:100]
                            score = result.get('distance', 'N/A')
                            print(f"     {i+1}. Score: {score} | {content}...")
                        else:
                            print(f"     {i+1}. {str(result)[:100]}...")
                else:
                    print("   ❌ Aucun résultat trouvé")

            except Exception as e:
                print(f"   ❌ Erreur lors de la recherche: {e}")

        # Test de recherche directe dans la collection
        print(f"\n📚 **TEST COLLECTION CHROMADB:**")

        try:
            if hasattr(rag_manager, 'collection') and rag_manager.collection:
                # Vérifier le contenu de la collection
                count = rag_manager.collection.count()
                print(f"   📊 Documents dans la collection: {count}")

                # Essayer une recherche directe
                if count > 0:
                    results = rag_manager.collection.query(
                        query_texts=["pytorch version"],
                        n_results=3
                    )
                    print(f"   🔍 Recherche directe 'pytorch version': {len(results['documents'][0]) if results['documents'] else 0} résultats")

                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            print(f"     {i+1}. {doc[:100]}...")
            else:
                print("   ❌ Collection ChromaDB non accessible")

        except Exception as e:
            print(f"   ❌ Erreur collection ChromaDB: {e}")

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_pytorch_search()

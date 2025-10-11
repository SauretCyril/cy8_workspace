#!/usr/bin/env python3
"""
Test rapide du RAG après correction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_rag_manager import RAGManager

def test_rag_after_fix():
    """Test du RAG après la correction de la méthode dupliquée"""
    print("🔧 === TEST RAG APRÈS CORRECTION ===")

    try:
        # Initialiser comme dans l'application
        print("1. Initialisation database_manager...")
        db_manager = cy8_database_manager("data/prompts.db")
        db_manager.init_database("dev")
        print("   ✅ Database manager initialisé")

        # Initialiser le RAG Manager avec environnement par défaut
        print("2. Initialisation RAG Manager...")
        default_env_id = "default_workspace"
        rag_manager = RAGManager(db_manager, default_env_id)
        print(f"   ✅ RAG Manager créé pour l'environnement: {default_env_id}")

        # Vérifier la disponibilité
        print("3. Vérification disponibilité...")
        available = rag_manager.is_available()
        print(f"   📊 RAG disponible: {available}")

        if available:
            print("4. Test d'indexation...")
            # Créer des données de test simples
            test_data = {
                "test_id": "test_correction",
                "environment_id": default_env_id,
                "log_content": "Test de correction du RAG - problème de méthode dupliquée résolu",
                "analysis_summary": "Correction de la méthode get_environment_analyses_directory",
                "errors_detected": ["Méthode dupliquée dans database_manager"],
                "recommendations": ["Supprimer la méthode dupliquée qui retourne None"]
            }

            # Indexer
            initial_count = rag_manager.collection.count()
            rag_manager.index_analysis_result(test_data)
            new_count = rag_manager.collection.count()
            print(f"   📊 Documents: {initial_count} -> {new_count}")

            # Test de recherche
            print("5. Test de recherche...")
            results = rag_manager.search_similar_issues("correction RAG", limit=3)
            print(f"   🔍 Résultats trouvés: {len(results)}")

            for i, result in enumerate(results[:2]):
                content = result.get('content', '')[:100]
                similarity = result.get('similarity', 0)
                print(f"   - Résultat {i+1}: {content}... (similarité: {similarity:.3f})")

            print("\n✅ RAG fonctionne correctement après correction !")
            return True
        else:
            print("❌ RAG non disponible")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_after_fix()

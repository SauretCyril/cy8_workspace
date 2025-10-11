#!/usr/bin/env python3
"""
Test simple du RAG Manager pour vérifier son fonctionnement
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_availability():
    """Test de disponibilité du RAG Manager"""
    print("🧪 Test de disponibilité du RAG Manager")
    print("=" * 50)

    try:
        # Test import ChromaDB
        print("🔍 Test import ChromaDB...")
        import chromadb
        print("✅ ChromaDB disponible")

        # Test import SentenceTransformers
        print("🔍 Test import SentenceTransformers...")
        import sentence_transformers
        print("✅ SentenceTransformers disponible")

        # Test import RAGManager
        print("🔍 Test import RAGManager...")
        from cy8_rag_manager import RAGManager
        print("✅ RAGManager disponible")

        # Test import database manager
        print("🔍 Test import DatabaseManager...")
        from cy8_database_manager import cy8_database_manager
        print("✅ DatabaseManager disponible")

        # Test création d'une instance RAG (simulation)
        print("🔍 Test création d'instance RAG...")
        db_path = "test.db"
        if os.path.exists(db_path):
            os.remove(db_path)

        db_manager = cy8_database_manager(db_path)
        rag_manager = RAGManager(db_manager, "test_env")
        print("✅ RAGManager instancié avec succès")

        # Nettoyage
        if os.path.exists(db_path):
            os.remove(db_path)

        print("\n🎉 Tous les tests RAG réussis !")
        return True

    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

    finally:
        print("\n" + "=" * 50)
        print("Test terminé")

if __name__ == "__main__":
    test_rag_availability()

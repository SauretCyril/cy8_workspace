#!/usr/bin/env python3
"""
Test de synchronisation du RAG Tester
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cy8_database_manager import cy8_database_manager
from cy8_rag_manager import RAGManager
from cy8_rag_tester import RAGTester

def test_rag_tester_sync():
    """Test de la synchronisation du RAG Tester avec les changements d'environnement"""
    print("🧪 === TEST SYNCHRONISATION RAG TESTER ===")

    try:
        # Initialiser
        print("1. Initialisation...")
        db_manager = cy8_database_manager("data/prompts.db")
        db_manager.init_database("dev")

        # Créer RAG Manager avec environnement initial
        initial_env = "test_env_1"
        rag_manager = RAGManager(db_manager, initial_env)
        rag_tester = RAGTester(rag_manager, db_manager)

        print(f"   ✅ RAG Manager env: {rag_manager.environment_id}")
        print(f"   ✅ RAG Tester env: {rag_tester.environment_id}")

        # Changer l'environnement
        print("2. Changement d'environnement...")
        new_env = "test_env_2"
        rag_manager.environment_id = new_env

        print(f"   🔄 RAG Manager env: {rag_manager.environment_id}")
        print(f"   🔄 RAG Tester env: {rag_tester.environment_id}")

        # Vérifier la synchronisation
        print("3. Vérification synchronisation...")
        if rag_tester.environment_id == new_env:
            print("   ✅ RAG Tester correctement synchronisé")
            return True
        else:
            print(f"   ❌ RAG Tester non synchronisé: {rag_tester.environment_id} != {new_env}")
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_tester_sync()

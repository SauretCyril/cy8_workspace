#!/usr/bin/env python3
"""
Test direct du système TODO sans passer par l'application complète
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_directly():
    """Test direct du RAG manager"""
    print("=== TEST DIRECT RAG MANAGER ===")

    try:
        # Imports directs
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        print("✅ Imports réussis")

        # Initialiser DB manager
        db_manager = cy8_database_manager()
        print("✅ DB manager créé")

        # Créer RAG manager
        rag = RAGManager(db_manager=db_manager, environment_id="TEST_H12")
        print("✅ RAG manager créé")

        # Vérifier méthodes disponibles
        methods = [attr for attr in dir(rag) if not attr.startswith('_')]
        print(f"📋 Méthodes disponibles: {len(methods)}")

        # Chercher spécifiquement process_todo_command
        if hasattr(rag, 'process_todo_command'):
            print("✅ process_todo_command trouvée")

            # Test d'appel
            result = rag.process_todo_command('/todo list')
            print(f"📝 Résultat: {result}")

        else:
            print("❌ process_todo_command NOT FOUND")
            todo_methods = [m for m in methods if 'todo' in m.lower()]
            print(f"🔍 Méthodes avec 'todo': {todo_methods}")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_directly()

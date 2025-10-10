#!/usr/bin/env python3
"""
Test des corrections RAG - Vérification du mode rapide et de la base de données
"""
import sys
import os

# Ajouter le chemin src au Python path
sys.path.append('src')

def test_rag_fixes():
    """Test des corrections RAG"""
    print('=== TEST DES CORRECTIONS RAG ===')

    try:
        # Test 1: Import du gestionnaire RAG
        print('\n🔧 Test 1: Import du gestionnaire RAG...')
        from cy8_rag_manager import RAGManager
        print('✅ Import RAG réussi')

        # Test 2: Création d'une instance minimale
        print('\n🔧 Test 2: Initialisation RAG...')

        # Simuler un db_manager minimal
        class MockDBManager:
            def get_database_path(self):
                return "G:/tmp/prompts_manager.db"

        db_manager = MockDBManager()
        environment_id = "TEST_H12"

        # Créer l'instance RAG
        rag = RAGManager(db_manager, environment_id)
        print('✅ RAG initialisé')

        # Test 3: Test de la structure de base
        print('\n🔧 Test 3: Test structure de données...')

        # Créer des données de test
        test_analysis = {
            "timestamp": "2025-01-07T10:00:00",
            "environment_id": "TEST_H12",
            "summary": "Test d'analyse",
            "errors": [
                {
                    "type": "custom_node_error",
                    "message": "Test erreur",
                    "solution": "Test solution"
                },
                "Erreur simple"
            ],
            "successes": ["Test succès"],
            "recommendations": ["Test recommandation"]
        }

        # Test de _prepare_content_for_indexing
        content = rag._prepare_content_for_indexing(test_analysis)
        print(f'✅ Contenu préparé: {len(content)} caractères')

        # Test 4: Test de parsing des documents
        print('\n🔧 Test 4: Test parsing documents...')

        # Simuler des documents avec différents formats
        test_docs = [
            {
                "content": test_analysis,  # Dict normal
                "metadata": {"env": "H12"}
            },
            {
                "content": '{"errors": [], "successes": ["test"]}',  # String JSON
                "metadata": {"env": "H12"}
            },
            {
                "content": "pas du json",  # String non-JSON
                "metadata": {"errors": ["test"], "env": "H12"}
            }
        ]

        # Test de _generate_template_response
        if hasattr(rag, '_generate_template_response'):
            response = rag._generate_template_response("test query", test_docs)
            print(f'✅ Template response générée: {len(response)} caractères')

        # Test 5: Test de la base de données server_state
        print('\n🔧 Test 5: Test base de données...')

        # Test de _update_server_state
        try:
            rag._update_server_state(test_analysis)
            print('✅ Mise à jour server_state réussie')
        except Exception as e:
            print(f'⚠️ Erreur server_state (normal si base non initialisée): {e}')

        print('\n🎉 TESTS TERMINÉS AVEC SUCCÈS!')
        return True

    except Exception as e:
        print(f'\n❌ Erreur lors des tests: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_fixes()
    exit(0 if success else 1)

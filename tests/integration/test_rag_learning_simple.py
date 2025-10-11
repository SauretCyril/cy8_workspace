#!/usr/bin/env python3
"""
Test simple pour vérifier que le RAG apprend maintenant
"""

import sys
import os
sys.path.append('src')

from cy8_database_manager import cy8_database_manager
from cy8_rag_manager import RAGManager

def test_rag_learning_simple():
    """Test simple de l'apprentissage RAG"""
    print("🧪 TEST SIMPLE D'APPRENTISSAGE RAG")
    print("=" * 40)

    try:
        # 1. Initialiser avec un environnement par défaut
        print("🔧 1. Initialisation RAG...")
        db_manager = cy8_database_manager()

        # Utiliser le même environnement par défaut que l'application
        default_env_id = "default_workspace"
        rag_manager = RAGManager(db_manager, default_env_id)

        print(f"   🏷️ Environnement: {default_env_id}")
        print(f"   ✅ RAG disponible: {rag_manager.is_available()}")

        if not rag_manager.is_available():
            print("   ❌ RAG non disponible")
            return False

        # 2. État initial
        print("\n📊 2. État initial...")
        initial_count = rag_manager.collection.count()
        print(f"   📚 Documents initiaux: {initial_count}")

        # 3. Ajouter des données d'apprentissage
        print("\n📥 3. Ajout de données d'apprentissage...")

        # Données de test avec l'environnement correct
        test_data = {
            "test_id": "learning_test_001",
            "environment_id": default_env_id,  # Important: utiliser le bon environment_id
            "log_content": "LEARNING TEST: Erreur de texture corrompue détectée",
            "errors_detected": [
                "Texture corruption error",
                "Image loading failed",
                "VRAM insufficient"
            ],
            "success_rate": 85.0,
            "performance_metrics": {
                "processing_time": "2.3s",
                "memory_usage": "8.2GB"
            },
            "recommendations": [
                "Vérifier l'intégrité des fichiers de texture",
                "Augmenter la VRAM allouée",
                "Réduire la résolution des textures"
            ],
            "analysis_summary": "Test d'apprentissage: problème de texture avec solutions proposées"
        }

        try:
            rag_manager.index_analysis_result(test_data)
            print("   ✅ Données indexées avec succès")
        except Exception as e:
            print(f"   ❌ Erreur indexation: {e}")
            return False

        # 4. Vérifier l'apprentissage
        print("\n🔍 4. Vérification de l'apprentissage...")
        new_count = rag_manager.collection.count()
        print(f"   📚 Documents après apprentissage: {new_count}")
        print(f"   📈 Nouveaux documents: +{new_count - initial_count}")

        if new_count <= initial_count:
            print("   ❌ Aucun nouveau document ajouté")
            return False

        # 5. Test de recherche pour vérifier l'apprentissage
        print("\n🧠 5. Test de recherche des connaissances...")

        test_queries = [
            "texture corruption",
            "VRAM insufficient",
            "image loading failed",
            "résolution textures"
        ]

        learning_confirmed = False

        for query in test_queries:
            print(f"   🔍 Recherche: '{query}'")
            results = rag_manager.search(query, limit=3)
            print(f"      📋 Résultats: {len(results)}")

            # Vérifier si notre test apparaît dans les résultats
            for result in results:
                if "learning test" in str(result).lower() or "texture" in str(result).lower():
                    learning_confirmed = True
                    print(f"      ✅ Apprentissage confirmé !")
                    break

        # 6. Résultats finaux
        print(f"\n📊 RÉSULTATS FINAUX:")
        print(f"   🔧 RAG initialisé: ✅")
        print(f"   📥 Indexation: ✅")
        print(f"   📈 Nouveaux documents: +{new_count - initial_count}")
        print(f"   🧠 Apprentissage confirmé: {'✅' if learning_confirmed else '❌'}")

        if learning_confirmed:
            print(f"\n🎉 SUCCÈS: Le RAG apprend correctement !")
            print(f"   💡 Le système peut maintenant mémoriser et retrouver les informations")
            return True
        else:
            print(f"\n⚠️ PROBLÈME: L'apprentissage n'est pas confirmé")
            print(f"   💡 Les données sont indexées mais la recherche ne les retrouve pas")
            return False

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_learning_simple()

    if success:
        print("\n✨ Le RAG est maintenant fonctionnel et apprend correctement !")
    else:
        print("\n🔧 Des ajustements sont encore nécessaires.")

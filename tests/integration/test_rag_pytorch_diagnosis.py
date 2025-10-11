#!/usr/bin/env python3
"""
Diagnostic RAG - Recherche des versions PyTorch indexées
Vérification pourquoi le RAG ne trouve pas les informations techniques spécifiques
"""

import sys
import os
import time

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_pytorch_version_in_rag():
    """Test si les versions PyTorch sont bien indexées dans le RAG"""
    print("🔍 DIAGNOSTIC RAG - VERSIONS PYTORCH")
    print("=" * 60)

    try:
        # Import des modules
        from cy8_database_manager import cy8_database_manager
        from cy8_rag_manager import RAGManager

        print("1. Connexion à la base de données...")

        # Utiliser la vraie base de données
        db_path = "G:/tmp/prompts_manager.db"  # Base par défaut
        if not os.path.exists(db_path):
            db_path = ":memory:"
            print("   ⚠️ Base par défaut non trouvée, utilisation mémoire")

        db_manager = cy8_database_manager(db_path)

        print("2. Vérification des analyses stockées...")

        # Récupérer toutes les analyses
        try:
            analyses = db_manager.get_all_analysis_results()
            print(f"   📊 Total analyses trouvées: {len(analyses)}")

            # Chercher les mentions de PyTorch
            pytorch_mentions = []
            for analysis in analyses:
                content = str(analysis.get('content', ''))
                message = str(analysis.get('message', ''))

                # Rechercher PyTorch dans le contenu
                if any(keyword in content.lower() for keyword in ['pytorch', 'torch version', 'torch.__version__']):
                    pytorch_mentions.append({
                        'id': analysis.get('id', 'N/A'),
                        'environment_id': analysis.get('environment_id', 'N/A'),
                        'timestamp': analysis.get('timestamp', 'N/A'),
                        'type': analysis.get('type', 'N/A'),
                        'content_extract': content[:200] + '...' if len(content) > 200 else content
                    })

                # Rechercher aussi dans le message
                if any(keyword in message.lower() for keyword in ['pytorch', 'torch version']):
                    pytorch_mentions.append({
                        'id': analysis.get('id', 'N/A'),
                        'environment_id': analysis.get('environment_id', 'N/A'),
                        'timestamp': analysis.get('timestamp', 'N/A'),
                        'type': analysis.get('type', 'N/A'),
                        'message_extract': message[:200] + '...' if len(message) > 200 else message
                    })

            print(f"   🔍 Analyses mentionnant PyTorch: {len(pytorch_mentions)}")

            # Afficher les premiers résultats
            for i, mention in enumerate(pytorch_mentions[:5]):
                print(f"\n   📋 Analyse {i+1}:")
                print(f"      ID: {mention['id']}")
                print(f"      Environnement: {mention['environment_id']}")
                print(f"      Type: {mention['type']}")
                if 'content_extract' in mention:
                    print(f"      Contenu: {mention['content_extract']}")
                if 'message_extract' in mention:
                    print(f"      Message: {mention['message_extract']}")

            return len(pytorch_mentions) > 0

        except Exception as e:
            print(f"   ❌ Erreur accès analyses: {e}")
            return False

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_search_pytorch():
    """Test de recherche RAG spécifique à PyTorch"""
    print("\n3. Test de recherche RAG...")

    try:
        from cy8_database_manager import cy8_database_manager
        from cy8_rag_manager import RAGManager

        db_path = "G:/tmp/prompts_manager.db"
        if not os.path.exists(db_path):
            db_path = ":memory:"

        db_manager = cy8_database_manager(db_path)
        rag_manager = RAGManager(db_manager, environment_id="test")

        # Tests de recherche spécifiques
        test_queries = [
            "version torch",
            "pytorch version",
            "torch.__version__",
            "quelle version pytorch",
            "ma version torch",
            "torch 2.1",
            "cuda version"
        ]

        for query in test_queries:
            print(f"\n   🔍 Requête: '{query}'")
            try:
                # Test de recherche sémantique
                if hasattr(rag_manager, 'search_similar_documents'):
                    results = rag_manager.search_similar_documents(query, limit=3)
                    print(f"      📊 Résultats trouvés: {len(results) if results else 0}")

                    if results:
                        for i, result in enumerate(results[:2]):
                            print(f"      📄 Résultat {i+1}: {str(result)[:100]}...")
                else:
                    print("      ⚠️ Méthode search_similar_documents non disponible")

            except Exception as e:
                print(f"      ❌ Erreur recherche: {e}")

        return True

    except Exception as e:
        print(f"   ❌ Erreur test recherche: {e}")
        return False

def analyze_rag_indexing_issue():
    """Analyser pourquoi le RAG ne trouve pas les infos techniques"""
    print("\n" + "=" * 60)
    print("🧠 ANALYSE DU PROBLÈME RAG")
    print("=" * 60)

    print("\n❓ PROBLÈME IDENTIFIÉ :")
    print("Le RAG donne des recommandations génériques au lieu")
    print("de répondre avec les informations spécifiques indexées.")
    print()

    print("🔍 CAUSES POSSIBLES :")
    print("1. 📝 Les analyses ne contiennent pas les versions PyTorch")
    print("2. 🔍 Le système de recherche ne trouve pas les bonnes analyses")
    print("3. 🎯 La question n'est pas formulée de manière optimale")
    print("4. 📊 Le contexte environnement n'est pas bien filtré")
    print("5. 🧠 Le RAG privilégie les recommandations générales")
    print()

    print("✅ SOLUTIONS À TESTER :")
    print("1. 📋 Questions plus spécifiques :")
    print("   - 'Version PyTorch environnement G11_01'")
    print("   - 'Torch version détectée dans les logs'")
    print("   - 'Configuration PyTorch actuelle'")
    print()

    print("2. 🔧 Améliorer l'indexation :")
    print("   - Extraire automatiquement les versions techniques")
    print("   - Créer des résumés structurés par environnement")
    print("   - Indexer les métadonnées techniques séparément")
    print()

    print("3. 🎯 Améliorer la recherche :")
    print("   - Prioriser les analyses de l'environnement actuel")
    print("   - Filtrer par type d'information (technique vs générale)")
    print("   - Utiliser des mots-clés techniques spécifiques")

def show_pytorch_extraction_example():
    """Montrer comment PyTorch est extrait des logs"""
    print("\n4. Extraction PyTorch des logs...")
    print("=" * 30)

    print("🔧 Le système cherche dans les logs :")
    print("   Pattern: 'pytorch version:\\s*([^\\s]+)'")
    print("   Exemple log: 'pytorch version: 2.1.2+cu118'")
    print("   Extraction: '2.1.2+cu118'")
    print()

    print("📊 Informations extraites :")
    print("   • Version PyTorch: 2.1.2")
    print("   • Version CUDA: cu118 (CUDA 11.8)")
    print("   • Compatibilité détectée automatiquement")
    print()

    print("🎯 Ces informations DEVRAIENT être trouvables via RAG !")

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC - POURQUOI LE RAG NE TROUVE PAS PYTORCH")
    print()

    # Tests
    pytorch_found = test_pytorch_version_in_rag()
    search_works = test_rag_search_pytorch()

    # Analyse
    analyze_rag_indexing_issue()
    show_pytorch_extraction_example()

    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 60)
    print(f"• PyTorch trouvé dans analyses: {'✅ OUI' if pytorch_found else '❌ NON'}")
    print(f"• Recherche RAG fonctionne: {'✅ OUI' if search_works else '❌ NON'}")

    if pytorch_found and search_works:
        print("\n🎯 RECOMMANDATION :")
        print("Les données sont là ! Essayez des questions plus spécifiques :")
        print("  - 'Version PyTorch détectée dans mon environnement'")
        print("  - 'Configuration technique actuelle'")
        print("  - 'Informations PyTorch/CUDA extraites des logs'")
    else:
        print("\n⚠️ PROBLÈME IDENTIFIÉ :")
        print("Les informations techniques ne sont pas correctement")
        print("indexées ou recherchées. Amélioration nécessaire.")

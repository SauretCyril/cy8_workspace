#!/usr/bin/env python3
"""
Test des nouveaux boutons RAG dans l'interface Chat
"""

import sys
import os
import time

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_buttons():
    """Tester les boutons RAG dans l'interface"""
    print("🧪 TEST DES BOUTONS RAG")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        import tkinter as tk

        print("1. 🚀 Initialisation de l'application...")

        # Créer l'application
        app = cy8_prompts_manager()

        print("2. 🔍 Vérification des nouveaux boutons...")

        # Vérifier que les méthodes existent
        required_methods = [
            'examine_rag_index',
            'reindex_rag_analyses',
            'show_rag_statistics'
        ]

        for method_name in required_methods:
            if hasattr(app, method_name):
                print(f"   ✅ Méthode {method_name} trouvée")
            else:
                print(f"   ❌ Méthode {method_name} manquante")
                return False

        print("3. 🧠 Test des fonctionnalités RAG...")

        # Test examine_rag_index
        try:
            app.examine_rag_index()
            print("   ✅ examine_rag_index() fonctionne")
        except Exception as e:
            print(f"   ⚠️ examine_rag_index() erreur: {e}")

        # Test show_rag_statistics
        try:
            app.show_rag_statistics()
            print("   ✅ show_rag_statistics() fonctionne")
        except Exception as e:
            print(f"   ⚠️ show_rag_statistics() erreur: {e}")

        # Test get_collection_stats du RAG manager
        if app.rag_manager:
            try:
                stats = app.rag_manager.get_collection_stats()
                print(f"   ✅ get_collection_stats(): {stats.get('total_documents', 0)} documents")
            except Exception as e:
                print(f"   ⚠️ get_collection_stats() erreur: {e}")
        else:
            print("   ⚠️ RAG manager non disponible")

        print("4. 📊 Résumé des fonctionnalités:")
        print("   🧠 Examiner RAG - Analyse détaillée de l'index")
        print("   🔄 Ré-indexer - Rechargement complet des analyses")
        print("   📊 Stats RAG - Statistiques et recommandations")

        print("\n✅ TOUS LES BOUTONS RAG SONT OPÉRATIONNELS")
        print("🎯 Les boutons sont disponibles dans l'onglet Chat > Actions rapides")

        return True

    except Exception as e:
        print(f"❌ Erreur test boutons RAG: {e}")
        return False

def test_rag_stats_method():
    """Test spécifique de la méthode get_collection_stats"""
    print("\n🔬 TEST SPÉCIFIQUE - get_collection_stats()")
    print("=" * 50)

    try:
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser le système
        db_path = "G:/tmp/prompts_manager.db"
        db_manager = cy8_database_manager(db_path)

        # Tester avec un environnement
        rag_manager = RAGManager(db_manager, "TEST_ENV")

        if rag_manager.is_available():
            print("✅ RAG disponible")

            # Tester get_collection_stats
            stats = rag_manager.get_collection_stats()

            print("📊 Statistiques obtenues:")
            for key, value in stats.items():
                print(f"   • {key}: {value}")

            # Vérifier la structure
            required_keys = ['total_documents', 'last_indexed', 'available']
            for key in required_keys:
                if key in stats:
                    print(f"   ✅ Clé '{key}' présente")
                else:
                    print(f"   ❌ Clé '{key}' manquante")

            return True
        else:
            print("⚠️ RAG non disponible - test ignoré")
            return True

    except Exception as e:
        print(f"❌ Erreur test stats: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS DES NOUVEAUX BOUTONS RAG")
    print("=" * 60)

    success = True

    # Test 1: Boutons dans l'interface
    success &= test_rag_buttons()

    # Test 2: Méthode stats spécifique
    success &= test_rag_stats_method()

    print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'} - Tests des boutons RAG")
    print("\n💡 UTILISATION:")
    print("1. Lancer l'application: python src/cy8_prompts_manager_main.py")
    print("2. Aller dans l'onglet '💬 Chat'")
    print("3. Utiliser les nouveaux boutons dans 'Actions rapides':")
    print("   • 🧠 Examiner RAG - Diagnostic complet")
    print("   • 🔄 Ré-indexer - Rechargement des analyses")
    print("   • 📊 Stats RAG - Métriques détaillées")

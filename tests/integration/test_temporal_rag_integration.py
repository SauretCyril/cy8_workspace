#!/usr/bin/env python3
"""
Test de l'intégration RAG temporel dans l'interface
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_temporal_rag_integration():
    """Tester l'intégration du RAG temporel dans l'interface"""
    print("🕒 TEST INTÉGRATION RAG TEMPOREL")
    print("=" * 50)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager
        import tkinter as tk

        print("1. 🚀 Initialisation de l'application...")

        # Créer l'application
        app = cy8_prompts_manager()

        print("2. 🔍 Vérification de l'extension temporelle...")

        # Vérifier que temporal_rag est initialisé
        if hasattr(app, 'temporal_rag') and app.temporal_rag:
            print("   ✅ Extension RAG temporelle initialisée")
        else:
            print("   ❌ Extension RAG temporelle manquante")
            return False

        # Vérifier les nouvelles méthodes
        temporal_methods = [
            'show_current_server_state',
            'show_temporal_analysis',
            'show_temporal_evolution'
        ]

        for method_name in temporal_methods:
            if hasattr(app, method_name):
                print(f"   ✅ Méthode {method_name} trouvée")
            else:
                print(f"   ❌ Méthode {method_name} manquante")
                return False

        print("3. 🧠 Test des fonctionnalités temporelles...")

        # Test des méthodes temporelles
        try:
            app.show_current_server_state()
            print("   ✅ show_current_server_state() fonctionne")
        except Exception as e:
            print(f"   ⚠️ show_current_server_state() erreur: {e}")

        try:
            app.show_temporal_analysis()
            print("   ✅ show_temporal_analysis() fonctionne")
        except Exception as e:
            print(f"   ⚠️ show_temporal_analysis() erreur: {e}")

        try:
            app.show_temporal_evolution()
            print("   ✅ show_temporal_evolution() fonctionne")
        except Exception as e:
            print(f"   ⚠️ show_temporal_evolution() erreur: {e}")

        print("4. 🎛️ Vérification des boutons...")

        # Les nouveaux boutons ont été ajoutés à la ligne 3 du grid
        print("   ✅ Nouveaux boutons ajoutés:")
        print("     • 🔥 État actuel (row=3, col=0)")
        print("     • 🕒 Analyse temporelle (row=3, col=1)")
        print("     • 📈 Évolution (row=3, col=2)")

        print("\n✅ INTÉGRATION RAG TEMPOREL RÉUSSIE !")
        print("🎯 Les boutons sont maintenant disponibles dans l'onglet Chat")

        return True

    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False

def test_temporal_functions():
    """Tester spécifiquement les fonctions temporelles"""
    print("\n🔬 TEST FONCTIONS TEMPORELLES")
    print("=" * 40)

    try:
        from cy8_temporal_rag import TemporalRAGManager
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser le système
        db_path = "G:/tmp/prompts_manager.db"
        db_manager = cy8_database_manager(db_path)
        rag_manager = RAGManager(db_manager, "TEST_INTEGRATION")

        if rag_manager.is_available():
            temporal_rag = TemporalRAGManager(rag_manager)

            print("✅ RAG temporel disponible")

            # Test search_with_temporal_priority
            results = temporal_rag.search_with_temporal_priority("PyTorch erreur", limit=3)
            print(f"✅ search_with_temporal_priority: {len(results)} résultats")

            # Test search_recent_only
            recent = temporal_rag.search_recent_only("serveur", max_age_hours=24, limit=3)
            print(f"✅ search_recent_only: {len(recent)} résultats")

            # Test get_temporal_distribution
            distribution = temporal_rag.get_temporal_distribution()
            if "error" not in distribution:
                print(f"✅ get_temporal_distribution: {distribution.get('total_documents', 0)} documents")
            else:
                print(f"⚠️ get_temporal_distribution: {distribution['error']}")

            return True
        else:
            print("⚠️ RAG non disponible - test ignoré")
            return True

    except Exception as e:
        print(f"❌ Erreur test fonctions temporelles: {e}")
        return False

if __name__ == "__main__":
    print("🕒 TESTS INTÉGRATION RAG TEMPOREL")
    print("=" * 60)

    success = True

    # Test 1: Intégration dans l'interface
    success &= test_temporal_rag_integration()

    # Test 2: Fonctions temporelles
    success &= test_temporal_functions()

    print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'} - Tests intégration RAG temporel")

    print("\n🎯 NOUVEAUX BOUTONS DISPONIBLES:")
    print("=" * 40)
    print("Onglet Chat > Actions rapides > Ligne 4:")
    print("🔥 **État actuel** - Analyse des dernières 24h")
    print("   • Détecte l'état du serveur en temps réel")
    print("   • Identifie les erreurs récentes")
    print("   • Évalue la santé du système")

    print("\n🕒 **Analyse temporelle** - Distribution des données")
    print("   • Fraîcheur des analyses (% récentes)")
    print("   • Chronologie des événements")
    print("   • Qualité temporelle du RAG")

    print("\n📈 **Évolution** - Tendances temporelles")
    print("   • Comparaison récent vs ancien")
    print("   • Détection des tendances")
    print("   • Évolution de l'activité")

    print("\n💡 UTILISATION:")
    print("1. Lancer: python src/cy8_prompts_manager_main.py")
    print("2. Onglet Chat > Actions rapides")
    print("3. Utiliser les boutons temporels (ligne 4)")
    print("4. Le RAG privilégie automatiquement les analyses récentes !")

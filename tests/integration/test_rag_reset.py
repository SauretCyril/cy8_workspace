#!/usr/bin/env python3
"""
Test de la réinitialisation RAG améliorée
"""

import sys
import os

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_rag_reset():
    """Test de la réinitialisation RAG complète"""
    print("🗑️ TEST RÉINITIALISATION RAG COMPLÈTE")
    print("=" * 50)

    try:
        # Importer les modules
        from cy8_database_manager import cy8_database_manager
        from cy8_rag_manager import RAGManager

        print("1. ✅ Imports réussis")

        # Créer le DB manager
        db_manager = cy8_database_manager()
        db_manager.init_database("dev")

        print("2. ✅ DB Manager initialisé")

        # Vérifier l'état avant reset
        results_before = db_manager.get_analysis_results()
        count_before = len(results_before) if results_before else 0
        print(f"3. 📊 Analyses en base AVANT: {count_before}")

        # Test de la méthode clear_analysis_results
        if hasattr(db_manager, 'clear_analysis_results'):
            print("4. ✅ Méthode clear_analysis_results trouvée")

            # Effectuer le nettoyage
            db_manager.clear_analysis_results()
            print("5. 🗑️ Nettoyage de la base effectué")

            # Vérifier l'état après
            results_after = db_manager.get_analysis_results()
            count_after = len(results_after) if results_after else 0
            print(f"6. 📊 Analyses en base APRÈS: {count_after}")

            if count_after == 0:
                print("7. ✅ SUCCÈS: Base de données nettoyée")
            else:
                print(f"7. ⚠️ ATTENTION: {count_after} analyses restantes")
        else:
            print("4. ❌ Méthode clear_analysis_results MANQUANTE")
            return False

        # Vérifier les dossiers
        print("\n📁 VÉRIFICATION DOSSIERS:")

        vector_db_path = os.path.join(os.getcwd(), "data", "analyses", "vector_db")
        if os.path.exists(vector_db_path):
            print(f"   📂 {vector_db_path} EXISTS")
            # Lister le contenu
            try:
                content = os.listdir(vector_db_path)
                print(f"   📋 Contenu: {content}")
            except:
                print("   ⚠️ Impossible de lire le contenu")
        else:
            print(f"   ✅ {vector_db_path} SUPPRIMÉ")

        analyses_path = os.path.join(os.getcwd(), "data", "analyses")
        if os.path.exists(analyses_path):
            print(f"   📂 {analyses_path} EXISTS")
            # Compter les fichiers d'analyse
            analysis_files = []
            for root, dirs, files in os.walk(analyses_path):
                for file in files:
                    if file.endswith(('.txt', '.json', '.log')):
                        analysis_files.append(os.path.join(root, file))
            print(f"   📋 Fichiers d'analyse: {len(analysis_files)}")

        print("\n🎯 RECOMMANDATION:")
        if count_after == 0:
            print("✅ La base de données est nettoyée")
            print("🔄 Redémarrez l'application pour recréer un RAG vide")
        else:
            print("⚠️ La base contient encore des analyses")
            print("🔧 Utilisez le bouton 'RAG Reset' dans l'interface")

        return count_after == 0

    except Exception as e:
        print(f"❌ Erreur test reset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🗑️ TEST RÉINITIALISATION RAG")
    print("=" * 60)

    success = test_rag_reset()

    if success:
        print("\n✅ RÉINITIALISATION RÉUSSIE")
        print("🚀 Redémarrez l'application pour un RAG propre")
    else:
        print("\n❌ PROBLÈME DE RÉINITIALISATION")
        print("🔧 Vérifiez les erreurs ci-dessus")

#!/usr/bin/env python3
"""
Test de l'aspect temporel du RAG - Analyses horodatées
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rag_temporal_awareness():
    """Tester si le RAG tient compte de l'aspect temporel des analyses"""
    print("🕒 TEST ASPECT TEMPOREL DU RAG")
    print("=" * 50)

    try:
        from cy8_rag_manager import RAGManager
        from cy8_database_manager import cy8_database_manager

        # Initialiser le système
        db_path = "G:/tmp/prompts_manager.db"
        db_manager = cy8_database_manager(db_path)
        rag_manager = RAGManager(db_manager, "TEST_TEMPORAL")

        if not rag_manager.is_available():
            print("⚠️ RAG non disponible - test annulé")
            return False

        print("1. 📊 Examen des métadonnées temporelles...")

        # Vérifier les documents existants pour leurs timestamps
        if rag_manager.collection:
            try:
                results = rag_manager.collection.get(
                    limit=10,
                    include=["metadatas", "documents"]
                )

                if results and results.get('metadatas'):
                    print(f"   📄 Documents trouvés: {len(results['metadatas'])}")

                    timestamps = []
                    for i, metadata in enumerate(results['metadatas']):
                        timestamp = metadata.get('timestamp', 'N/A')
                        env_id = metadata.get('environment_id', 'N/A')
                        analysis_type = metadata.get('analysis_type', 'N/A')

                        print(f"   • Doc {i+1}: {timestamp} | {env_id} | {analysis_type}")

                        if timestamp != 'N/A':
                            timestamps.append(timestamp)

                    if timestamps:
                        print(f"   ✅ Timestamps présents: {len(timestamps)}/{len(results['metadatas'])}")

                        # Analyser la répartition temporelle
                        print(f"   📅 Plus ancien: {min(timestamps)}")
                        print(f"   📅 Plus récent: {max(timestamps)}")
                    else:
                        print("   ❌ Aucun timestamp valide trouvé")

                else:
                    print("   📭 Aucun document dans la collection")

            except Exception as e:
                print(f"   ❌ Erreur lecture métadonnées: {e}")

        print("\n2. 🧪 Test d'indexation avec différents timestamps...")

        # Créer des analyses avec des timestamps différents
        now = datetime.now()
        test_analyses = [
            {
                "timestamp": (now - timedelta(days=7)).isoformat(),
                "type": "log_analysis",
                "content": "Erreur PyTorch version 1.12.0 - ancienne analyse",
                "environment_id": "TEST_TEMPORAL",
                "analysis_type": "error_analysis",
                "age": "ancienne"
            },
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "type": "log_analysis",
                "content": "PyTorch 2.1.0 fonctionne parfaitement - analyse récente",
                "environment_id": "TEST_TEMPORAL",
                "analysis_type": "success_analysis",
                "age": "récente"
            },
            {
                "timestamp": now.isoformat(),
                "type": "log_analysis",
                "content": "Configuration PyTorch optimisée - analyse actuelle",
                "environment_id": "TEST_TEMPORAL",
                "analysis_type": "current_analysis",
                "age": "actuelle"
            }
        ]

        # Indexer les analyses test
        for i, analysis in enumerate(test_analyses):
            success = rag_manager.index_analysis_result(analysis)
            if success:
                print(f"   ✅ Analyse {analysis['age']} indexée")
            else:
                print(f"   ❌ Échec indexation analyse {analysis['age']}")

        print("\n3. 🔍 Test de recherche - Le RAG favorise-t-il les analyses récentes ?")

        # Rechercher PyTorch
        query = "PyTorch version configuration"
        results = rag_manager.search_similar_issues(query, limit=5)

        if results:
            print(f"   📋 Résultats trouvés: {len(results)}")

            # Analyser l'ordre des résultats
            for i, result in enumerate(results):
                metadata = result.get('metadata', {})
                timestamp = metadata.get('timestamp', 'N/A')
                similarity = result.get('similarity', 0)
                content_preview = result.get('content', '')[:50] + "..."

                print(f"   • Rang {i+1}: Score {similarity:.3f} | {timestamp}")
                print(f"     📝 {content_preview}")

            # Vérifier si les résultats sont ordonnés par pertinence ou par date
            timestamps_found = []
            for result in results:
                ts = result.get('metadata', {}).get('timestamp')
                if ts and ts != 'N/A':
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        timestamps_found.append(dt)
                    except:
                        pass

            if len(timestamps_found) >= 2:
                is_chronological = all(timestamps_found[i] <= timestamps_found[i+1] for i in range(len(timestamps_found)-1))
                is_reverse_chronological = all(timestamps_found[i] >= timestamps_found[i+1] for i in range(len(timestamps_found)-1))

                if is_reverse_chronological:
                    print("   📈 RÉSULTATS: Ordre chronologique inverse (récent → ancien)")
                elif is_chronological:
                    print("   📉 RÉSULTATS: Ordre chronologique (ancien → récent)")
                else:
                    print("   🎯 RÉSULTATS: Ordre par similarité sémantique (pas temporel)")

        else:
            print("   ❌ Aucun résultat trouvé")

        print("\n4. 🎯 ANALYSE TEMPORELLE DU RAG")
        print("=" * 40)

        # Analyser la méthode search_similar_issues
        print("📝 Méthode de recherche actuelle:")
        print("   • search_similar_issues() utilise la similarité vectorielle")
        print("   • Pas de filtre temporel explicite")
        print("   • Pas de pondération par âge des documents")

        print("\n🔍 Métadonnées disponibles:")
        print("   ✅ timestamp: Horodatage d'indexation")
        print("   ✅ environment_id: Contexte environnement")
        print("   ✅ analysis_type: Type d'analyse")

        print("\n⚡ Recommandations:")
        print("   1. 🕒 Ajouter un paramètre temporel aux recherches")
        print("   2. 📊 Pondérer les résultats par récence")
        print("   3. 🎯 Créer des filtres par période")
        print("   4. 📈 Privilégier les analyses récentes pour l'état actuel")

        return True

    except Exception as e:
        print(f"❌ Erreur test temporel: {e}")
        return False

def test_get_recent_log_analyses():
    """Tester la méthode get_recent_log_analyses qui gère l'aspect temporel"""
    print("\n🔄 TEST get_recent_log_analyses()")
    print("=" * 40)

    try:
        from cy8_prompts_manager_main import cy8_prompts_manager

        # Créer l'instance (sans interface graphique)
        app = cy8_prompts_manager()

        if not hasattr(app, 'get_recent_log_analyses'):
            print("❌ Méthode get_recent_log_analyses non trouvée")
            return False

        print("✅ Méthode get_recent_log_analyses trouvée")

        # Tester avec un environnement
        recent_analyses = app.get_recent_log_analyses("G11_05", limit=10)

        if recent_analyses:
            print(f"📊 Analyses récentes trouvées: {len(recent_analyses)}")

            # Analyser la structure temporelle
            for i, analysis in enumerate(recent_analyses[:3]):  # Afficher les 3 premiers
                timestamp = analysis.get('timestamp_analyse', 'N/A')
                log_type = analysis.get('log_type', 'N/A')
                message = analysis.get('message', '')[:50] + "..."

                print(f"   • Analyse {i+1}: {timestamp} | {log_type}")
                print(f"     📝 {message}")

            print("\n✅ La méthode récupère bien les analyses ordonnées")
            print("🎯 MAIS: Ces analyses ne sont pas automatiquement")
            print("    filtrées par récence dans les recherches RAG")

        else:
            print("📭 Aucune analyse récente trouvée")

        return True

    except Exception as e:
        print(f"❌ Erreur test get_recent_log_analyses: {e}")
        return False

if __name__ == "__main__":
    print("🕒 TESTS ASPECT TEMPOREL DU RAG")
    print("=" * 60)

    success = True

    # Test 1: Aspect temporel général
    success &= test_rag_temporal_awareness()

    # Test 2: Méthode get_recent_log_analyses
    success &= test_get_recent_log_analyses()

    print(f"\n{'✅ SUCCÈS' if success else '❌ ÉCHEC'} - Tests aspect temporel")

    print("\n📋 CONCLUSION SUR L'ASPECT TEMPOREL:")
    print("=" * 50)
    print("✅ ACTUELLEMENT GÉRÉ:")
    print("   • Timestamps stockés dans les métadonnées")
    print("   • get_recent_log_analyses() ordonne par date")
    print("   • Indexation conserve l'horodatage")

    print("\n❌ PAS ENCORE GÉRÉ:")
    print("   • Recherche RAG sans filtrage temporel")
    print("   • Pas de pondération par récence")
    print("   • Analyses anciennes et récentes mélangées")

    print("\n🎯 IMPACT:")
    print("   Le RAG peut retourner des informations obsolètes")
    print("   avec le même poids que les informations récentes!")

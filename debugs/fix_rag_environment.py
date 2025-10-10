#!/usr/bin/env python3
"""
Script pour corriger le problème d'environment_id dans le RAG
"""

import sys
import os
sys.path.append('src')

from cy8_database_manager import cy8_database_manager

def fix_rag_environment():
    """Corriger le problème d'environnement RAG"""
    print("🔧 CORRECTION DU PROBLÈME D'ENVIRONNEMENT RAG")
    print("=" * 50)

    try:
        # 1. Vérifier les environnements existants
        print("📋 1. Vérification des environnements existants...")
        db_manager = cy8_database_manager()

        environments = db_manager.get_all_environments()
        print(f"   📊 Environnements trouvés: {len(environments)}")

        if environments:
            for env in environments:
                env_id, name, path = env[:3]  # au cas où il y a plus de colonnes
                print(f"   🏷️  {env_id}: {name} ({path})")

        # 2. Créer un environnement par défaut si nécessaire
        default_env_id = "default_test"

        if not any(env[0] == default_env_id for env in environments):
            print(f"\n🆕 2. Création d'un environnement par défaut: {default_env_id}")

            success = db_manager.add_environment(
                env_id=default_env_id,
                name="Environnement de Test RAG",
                comfyui_path="C:/ComfyUI"  # Chemin par défaut
            )

            if success:
                print(f"   ✅ Environnement {default_env_id} créé avec succès")
            else:
                print(f"   ❌ Échec création environnement {default_env_id}")
                return False
        else:
            print(f"\n✅ 2. Environnement {default_env_id} existe déjà")

        # 3. Tester le RAG avec l'environnement par défaut
        print(f"\n🧪 3. Test du RAG avec l'environnement {default_env_id}...")

        from cy8_rag_manager import RAGManager
        rag_manager = RAGManager(db_manager, default_env_id)

        if rag_manager.is_available():
            print("   ✅ RAG Manager initialisé avec succès")
            print(f"   🏷️  Environnement: {rag_manager.environment_id}")

            # Test d'indexation simple
            test_data = {
                "test_id": "fix_test_001",
                "environment_id": default_env_id,
                "log_content": "Test de correction RAG",
                "errors_detected": ["Test error"],
                "success_rate": 100.0,
                "performance_metrics": {"status": "ok"},
                "recommendations": ["RAG fonctionne correctement"],
                "analysis_summary": "Test de correction du problème d'environnement"
            }

            try:
                initial_count = rag_manager.collection.count()
                rag_manager.index_analysis_result(test_data)
                new_count = rag_manager.collection.count()

                print(f"   📚 Documents avant: {initial_count}")
                print(f"   📚 Documents après: {new_count}")
                print(f"   ✅ Indexation: {'Réussie' if new_count > initial_count else 'Échouée'}")

                # Test de recherche
                results = rag_manager.search("correction RAG", limit=2)
                print(f"   🔍 Résultats recherche: {len(results)}")

                if results:
                    print("   🎉 RAG fonctionne correctement !")
                    return True
                else:
                    print("   ⚠️ Recherche ne retourne pas de résultats")
                    return False

            except Exception as e:
                print(f"   ❌ Erreur test RAG: {e}")
                return False
        else:
            print("   ❌ RAG Manager non disponible")
            return False

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

def suggest_fixes():
    """Suggérer des corrections pour l'application"""
    print("\n💡 SUGGESTIONS DE CORRECTIONS:")
    print("1. Modifier l'initialisation du RAG dans cy8_prompts_manager_main.py")
    print("2. Créer un environnement par défaut au démarrage")
    print("3. Initialiser le RAG seulement après identification d'environnement")
    print("4. Ajouter une vérification d'environment_id avant indexation")

if __name__ == "__main__":
    success = fix_rag_environment()

    if success:
        print("\n🎉 CORRECTION RÉUSSIE!")
        print("Le RAG peut maintenant apprendre correctement.")
    else:
        print("\n⚠️ CORRECTION PARTIELLE")
        suggest_fixes()

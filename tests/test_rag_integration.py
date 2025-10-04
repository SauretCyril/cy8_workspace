#!/usr/bin/env python3
"""
Test du système RAG avec intégration complète
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime
import json

# Import des classes nécessaires
try:
    from cy8_rag_manager import RAGManager
    from cy8_database_manager import cy8_database_manager
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import failed: {e}")
    RAG_AVAILABLE = False


def test_rag_integration():
    """Test d'intégration complète du système RAG"""
    
    if not RAG_AVAILABLE:
        print("❌ RAG non disponible - vérifiez les imports")
        return False
    
    print("🧪 Test d'intégration du système RAG ComfyUI")
    print("=" * 60)
    
    # 1. Initialiser le gestionnaire de base de données
    print("\n1️⃣ Initialisation de la base de données...")
    db_manager = cy8_database_manager("G:/tmp/test_rag.db")
    db_manager.init_database("test")
    
    # 2. Créer un environnement de test
    print("2️⃣ Création d'un environnement de test...")
    env_id = "G11_TEST"
    env_path = "H:/comfyui/G11_TEST"
    
    # Simuler l'insertion d'un environnement
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO environnements (id, nom, chemin, description, actif)
            VALUES (?, ?, ?, ?, ?)
        """, (env_id, "Test Environment", env_path, "Environnement de test RAG", 1))
        conn.commit()
        conn.close()
        print(f"✅ Environnement créé: {env_id}")
    except Exception as e:
        print(f"⚠️ Erreur environnement: {e}")
    
    # 3. Initialiser le RAG
    print("3️⃣ Initialisation du RAG...")
    rag = RAGManager(db_manager, env_id)
    
    if not rag.is_available():
        print("❌ RAG non disponible")
        return False
    
    print("✅ RAG initialisé avec succès")
    
    # 4. Ajouter des contraintes système
    print("4️⃣ Ajout de contraintes système...")
    test_constraints = [
        ("numpy_version", "1.24.x", "Ne peut pas utiliser numpy 2.x à cause du matériel RTX 3060"),
        ("memory_limit", "12GB_VRAM", "Limitation VRAM pour les gros modèles"),
        ("python_version", "3.10.11", "Version Python stable pour ComfyUI"),
        ("custom_node_conflict", "controlnet_vs_ipadapter", "Conflit entre ControlNet et IP-Adapter"),
    ]
    
    for constraint_type, value, description in test_constraints:
        rag.add_constraint(constraint_type, value, description)
        print(f"  ✅ {constraint_type}: {value}")
    
    # 5. Simuler des analyses de logs
    print("5️⃣ Indexation d'analyses de logs...")
    test_analyses = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "error_analysis",
            "summary": "Erreur de mémoire VRAM lors du chargement du modèle SDXL",
            "errors": [
                {
                    "type": "memory_error",
                    "message": "CUDA out of memory. Tried to allocate 2.73 GiB",
                    "solution": "Réduire la taille du batch ou utiliser un modèle plus petit"
                }
            ],
            "successes": ["Chargement des custom nodes réussi"],
            "recommendations": ["Optimiser l'utilisation VRAM", "Utiliser model offloading"]
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "dependency_analysis", 
            "summary": "Conflit de version numpy détecté",
            "errors": [
                {
                    "type": "dependency_conflict",
                    "message": "numpy 2.1.0 incompatible avec custom node XYZ",
                    "solution": "Downgrade vers numpy 1.24.4"
                }
            ],
            "successes": [],
            "recommendations": ["Fixer les versions dans requirements.txt"]
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "performance_analysis",
            "summary": "Optimisation réussie du pipeline de génération",
            "errors": [],
            "successes": [
                "Temps de génération réduit de 45%",
                "Utilisation VRAM optimisée",
                "Pipeline stable sur 100 générations"
            ],
            "recommendations": ["Maintenir cette configuration", "Documenter les paramètres optimaux"]
        }
    ]
    
    for i, analysis in enumerate(test_analyses, 1):
        success = rag.index_analysis_result(analysis)
        if success:
            print(f"  ✅ Analyse {i} indexée")
        else:
            print(f"  ❌ Erreur indexation analyse {i}")
    
    # 6. Test de recherche
    print("6️⃣ Tests de recherche...")
    test_queries = [
        "problème de mémoire VRAM",
        "erreur numpy version",
        "optimisation performance",
        "conflit custom nodes",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Recherche: '{query}'")
        results = rag.search_similar_issues(query, limit=2)
        if results:
            for j, result in enumerate(results, 1):
                similarity = int(result['similarity'] * 100)
                print(f"  {j}. Similarité: {similarity}% - {result['content'][:100]}...")
        else:
            print(f"  Aucun résultat pour '{query}'")
    
    # 7. Test du résumé de statut
    print("\n7️⃣ Test du résumé de statut...")
    status = rag.get_server_status_summary()
    print(f"État actuel: {status['current_state']['value']}")
    print(f"Contraintes: {len(status['constraints'])}")
    print(f"Erreurs récurrentes: {len(status['recurring_errors'])}")
    
    # 8. Test de génération de contexte
    print("8️⃣ Test de génération de contexte...")
    context = rag.generate_chat_context("Comment optimiser les performances ?")
    print("Contexte généré:")
    print("-" * 40)
    print(context[:500] + "..." if len(context) > 500 else context)
    
    print("\n" + "=" * 60)
    print("🎉 Test d'intégration RAG RÉUSSI !")
    print(f"📁 Base vectorielle: {rag.vector_db_path}")
    print(f"🗃️ Base contraintes: {rag.constraints_db_path}")
    
    return True


def test_chat_simulation():
    """Simuler une conversation chat"""
    print("\n🗨️ Simulation de conversation chat...")
    
    # Simulation simple
    user_messages = [
        "Quel est l'état du serveur ?",
        "J'ai une erreur de mémoire VRAM",
        "Comment optimiser numpy ?",
        "Rappelle-moi mes contraintes système",
    ]
    
    for message in user_messages:
        print(f"\n👤 Utilisateur: {message}")
        print(f"🤖 Assistant: [Traiterait la requête avec le RAG]")
    
    print("✅ Simulation chat terminée")


if __name__ == "__main__":
    try:
        success = test_rag_integration()
        if success:
            test_chat_simulation()
        else:
            print("❌ Échec du test d'intégration")
            sys.exit(1)
    except Exception as e:
        print(f"💥 Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)